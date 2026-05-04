import sqlite3
from datetime import datetime
from time import perf_counter
from typing import List, Optional

from ....core.telemetry import telemetry
from ..records import (
    PrimaryTarget,
    StoredUser,
    SyncStatus,
    SyncUser,
    TargetMessageBreakdown,
    UserIdentityRecord,
)
from .common import SQLiteReadCommonMixin


class SQLiteTargetReadMixin(SQLiteReadCommonMixin):
    def get_sync_status(self, chat_id: int, user_id: int) -> SyncStatus:
        with self._read_connection() as conn:
            row = conn.execute(
                """
                SELECT
                    t.last_msg_id,
                    t.tail_msg_id,
                    t.is_complete,
                    t.deep_mode,
                    t.recursive_depth,
                    t.last_sync_at,
                    COALESCE(NULLIF(u.current_author_name, ''), NULLIF(t.author_name, '')) AS author_name
                FROM sync_targets t
                LEFT JOIN users u ON u.user_id = t.user_id
                WHERE t.user_id = ? AND t.chat_id = ?
            """,
                (user_id, chat_id),
            ).fetchone()
            if row:
                return SyncStatus.coerce(dict(row))
        return SyncStatus()

    def get_outdated_chats(self, threshold_seconds: int) -> List[tuple]:
        cutoff = int(datetime.now().timestamp()) - threshold_seconds
        with self._read_connection() as conn:
            rows = conn.execute(
                """
                SELECT chat_id, user_id FROM sync_targets
                WHERE is_complete = 0 OR COALESCE(last_sync_at, 0) < ?
            """,
                (cutoff,),
            ).fetchall()
            chat_rows = conn.execute(
                """
                SELECT chat_id FROM sync_state
                WHERE COALESCE(last_sync_timestamp, 0) < ?
            """,
                (cutoff,),
            ).fetchall()

        results = {(r["chat_id"], r["user_id"]) for r in rows}
        for r in chat_rows:
            results.add((r["chat_id"], r["chat_id"]))
        return list(results)

    def filter_missing_target_links(
        self, chat_id: int, target_id: int, message_ids: List[int]
    ) -> List[int]:
        if not message_ids:
            return []

        started_at = perf_counter()
        existing_ids = set()
        with self._read_connection() as conn:
            for chunk in self._chunked(message_ids):
                placeholders = ", ".join(["?"] * len(chunk))
                rows = conn.execute(
                    f"""
                    SELECT message_id FROM message_target_links
                    WHERE chat_id = ? AND target_user_id = ? AND message_id IN ({placeholders})
                """,
                    (chat_id, target_id, *chunk),
                ).fetchall()
                existing_ids.update(row["message_id"] for row in rows)

        missing_ids = [
            message_id for message_id in message_ids if message_id not in existing_ids
        ]
        telemetry.track_counter("storage.target_link_filter.calls", 1)
        telemetry.track_counter(
            "storage.target_link_filter.candidates", len(message_ids)
        )
        telemetry.track_counter("storage.target_link_filter.missing", len(missing_ids))
        telemetry.track_duration(
            "storage.target_link_filter.total", perf_counter() - started_at
        )
        return missing_ids

    def get_unique_sync_users(self) -> List[SyncUser]:
        with self._read_connection() as conn:
            rows = conn.execute(
                """
                SELECT DISTINCT user_id, author_name
                FROM messages
                GROUP BY user_id
                ORDER BY author_name ASC
            """
            ).fetchall()
            return [
                SyncUser(user_id=row["user_id"], author_name=row["author_name"])
                for row in rows
            ]

    def get_user(self, user_id: int) -> Optional[StoredUser]:
        with self._read_connection() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()
            return StoredUser.coerce(dict(row)) if row else None

    def get_user_identity_history(self, user_id: int) -> List[UserIdentityRecord]:
        with self._read_connection() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM user_identity_history
                WHERE user_id = ?
                ORDER BY observed_at ASC, COALESCE(source_message_id, 0) ASC
            """,
                (user_id,),
            ).fetchall()
            return [UserIdentityRecord.coerce(dict(row)) for row in rows]

    def get_primary_targets(self) -> List[PrimaryTarget]:
        try:
            with self._read_connection() as conn:
                rows = conn.execute(
                    """
                    SELECT
                        t.user_id,
                        t.chat_id,
                        COALESCE(NULLIF(u.current_author_name, ''), NULLIF(t.author_name, '')) AS author_name,
                        t.added_at,
                        t.last_sync_at,
                        t.last_msg_id,
                        t.tail_msg_id,
                        t.is_complete,
                        t.deep_mode,
                        t.recursive_depth,
                        u.username,
                        u.first_name,
                        u.last_name,
                        c.title as chat_title,
                        (SELECT COUNT(*)
                         FROM message_target_links l
                         JOIN messages m ON l.chat_id = m.chat_id AND l.message_id = m.message_id
                         WHERE l.target_user_id = t.user_id AND m.user_id = t.user_id) as user_msg_count,
                        (SELECT COUNT(*)
                         FROM message_target_links l
                         JOIN messages m ON l.chat_id = m.chat_id AND l.message_id = m.message_id
                         WHERE l.target_user_id = t.user_id AND m.user_id != t.user_id) as context_msg_count
                    FROM sync_targets t
                    LEFT JOIN users u ON t.user_id = u.user_id
                    LEFT JOIN chats c ON t.chat_id = c.chat_id
                    ORDER BY COALESCE(NULLIF(u.current_author_name, ''), NULLIF(t.author_name, '')) ASC
                """
                ).fetchall()
                return [PrimaryTarget.coerce(dict(row)) for row in rows]
        except sqlite3.OperationalError as e:
            if "no such table" in str(e):
                return []
            raise

    def has_target_link(self, chat_id: int, message_id: int, target_id: int) -> bool:
        with self._read_connection() as conn:
            res = conn.execute(
                """
                SELECT 1 FROM message_target_links
                WHERE chat_id = ? AND message_id = ? AND target_user_id = ?
                LIMIT 1
            """,
                (chat_id, message_id, target_id),
            ).fetchone()
            return res is not None

    def get_target_message_breakdown(
        self, chat_id: int, target_id: int
    ) -> TargetMessageBreakdown:
        with self._read_connection() as conn:
            row = conn.execute(
                """
                SELECT
                    COUNT(*) AS total_linked,
                    SUM(CASE WHEN m.user_id = ? THEN 1 ELSE 0 END) AS own_messages
                FROM message_target_links l
                JOIN messages m ON l.chat_id = m.chat_id AND l.message_id = m.message_id
                WHERE l.chat_id = ? AND l.target_user_id = ?
            """,
                (target_id, chat_id, target_id),
            ).fetchone()
            total_linked = (
                row["total_linked"] if row and row["total_linked"] is not None else 0
            )
            own_messages = (
                row["own_messages"] if row and row["own_messages"] is not None else 0
            )
            return TargetMessageBreakdown(
                own_messages=own_messages,
                with_context=total_linked,
            )
