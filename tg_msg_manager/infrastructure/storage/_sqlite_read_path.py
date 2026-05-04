import json
import logging
import sqlite3
from time import perf_counter
from datetime import datetime, timezone
from typing import Any, Iterable, List, Optional

from ...core.models.message import MessageData
from ...core.models.reporting import (
    ReportDatabaseSummary,
    ReportRetrySummary,
    ReportTargetSummary,
)
from ...core.telemetry import telemetry
from .records import (
    PrimaryTarget,
    RetryTaskRecord,
    StoredUser,
    SyncStatus,
    SyncUser,
    TargetMessageBreakdown,
    UserExportRow,
    UserExportSummary,
)

logger = logging.getLogger(__name__)


class SQLiteReadPathMixin:
    @staticmethod
    def _chunked(values: Iterable[int], size: int = 900) -> List[List[int]]:
        items = list(values)
        return [items[i : i + size] for i in range(0, len(items), size)]

    def _row_to_message(self, row: sqlite3.Row) -> MessageData:
        data = dict(row)
        msg_id = data.get("message_id") if "message_id" in data else data.get("msg_id")
        return MessageData(
            message_id=msg_id,
            chat_id=data["chat_id"],
            user_id=data["user_id"],
            author_name=data.get("author_name"),
            timestamp=datetime.fromtimestamp(data["timestamp"], tz=timezone.utc),
            text=data.get("text"),
            media_type=data.get("media_type"),
            reply_to_id=data.get("reply_to_id"),
            fwd_from_id=data.get("fwd_from_id"),
            context_group_id=data.get("context_group_id"),
            raw_payload=json.loads(data["raw_payload"]),
        )

    def get_message(self, chat_id: int, message_id: int) -> Optional[MessageData]:
        with self._read_connection() as conn:
            row = conn.execute(
                "SELECT * FROM messages WHERE chat_id = ? AND message_id = ?",
                (chat_id, message_id),
            ).fetchone()
            return self._row_to_message(row) if row else None

    def message_exists(self, chat_id: int, message_id: int) -> bool:
        with self._read_connection() as conn:
            row = conn.execute(
                "SELECT 1 FROM messages WHERE chat_id = ? AND message_id = ?",
                (chat_id, message_id),
            ).fetchone()
            return row is not None

    def get_last_msg_id(self, chat_id: int) -> int:
        with self._read_connection() as conn:
            row = conn.execute(
                "SELECT last_msg_id FROM sync_state WHERE chat_id = ?", (chat_id,)
            ).fetchone()
            return row["last_msg_id"] if row else 0

    def get_sync_status(self, chat_id: int, user_id: int) -> SyncStatus:
        with self._read_connection() as conn:
            row = conn.execute(
                """
                SELECT
                    last_msg_id,
                    tail_msg_id,
                    is_complete,
                    deep_mode,
                    recursive_depth,
                    last_sync_at,
                    author_name
                FROM sync_targets
                WHERE user_id = ? AND chat_id = ?
            """,
                (user_id, chat_id),
            ).fetchone()
            if row:
                return SyncStatus.coerce(dict(row))
        return SyncStatus()

    def filter_existing_ids(self, chat_id: int, message_ids: List[int]) -> List[int]:
        if not message_ids:
            return []
        placeholders = ", ".join(["?"] * len(message_ids))
        with self._read_connection() as conn:
            rows = conn.execute(
                f"SELECT message_id FROM messages WHERE chat_id = ? AND message_id IN ({placeholders})",
                (chat_id, *message_ids),
            ).fetchall()
        existing = {row["message_id"] for row in rows}
        return [mid for mid in message_ids if mid not in existing]

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

    def get_message_count(self, chat_id: int, target_id: Optional[int] = None) -> int:
        with self._read_connection() as conn:
            if target_id:
                row = conn.execute(
                    """
                    SELECT COUNT(*) as count
                    FROM message_target_links
                    WHERE chat_id = ? AND target_user_id = ?
                """,
                    (chat_id, target_id),
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT COUNT(*) as count FROM messages WHERE chat_id = ?",
                    (chat_id,),
                ).fetchone()
            return row["count"] if row else 0

    def get_all_message_ids_for_chat(self, chat_id: int) -> List[int]:
        with self._read_connection() as conn:
            rows = conn.execute(
                "SELECT message_id FROM messages WHERE chat_id = ? ORDER BY message_id DESC",
                (chat_id,),
            ).fetchall()
            return [row["message_id"] for row in rows]

    def get_messages_in_id_range(
        self, chat_id: int, start_id: int, end_id: int
    ) -> List[MessageData]:
        with self._read_connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM messages
                WHERE chat_id = ? AND message_id BETWEEN ? AND ?
                ORDER BY timestamp ASC, message_id ASC
            """,
                (chat_id, start_id, end_id),
            ).fetchall()
            return [self._row_to_message(row) for row in rows]

    def get_messages_replying_to(
        self, chat_id: int, reply_to_ids: List[int]
    ) -> List[MessageData]:
        if not reply_to_ids:
            return []

        placeholders = ", ".join(["?"] * len(reply_to_ids))
        with self._read_connection() as conn:
            rows = conn.execute(
                f"""
                SELECT * FROM messages
                WHERE chat_id = ? AND reply_to_id IN ({placeholders})
                ORDER BY timestamp ASC, message_id ASC
            """,
                (chat_id, *reply_to_ids),
            ).fetchall()
            return [self._row_to_message(row) for row in rows]

    def get_messages_by_ids(
        self, chat_id: int, message_ids: List[int]
    ) -> List[MessageData]:
        if not message_ids:
            return []

        started_at = perf_counter()
        rows = []
        with self._read_connection() as conn:
            for chunk in self._chunked(message_ids):
                placeholders = ", ".join(["?"] * len(chunk))
                rows.extend(
                    conn.execute(
                        f"""
                    SELECT * FROM messages
                    WHERE chat_id = ? AND message_id IN ({placeholders})
                    ORDER BY timestamp ASC, message_id ASC
                """,
                        (chat_id, *chunk),
                    ).fetchall()
                )
        telemetry.track_counter("storage.get_messages_by_ids.calls", 1)
        telemetry.track_counter(
            "storage.get_messages_by_ids.requested_ids", len(message_ids)
        )
        telemetry.track_counter("storage.get_messages_by_ids.rows", len(rows))
        telemetry.track_duration(
            "storage.get_messages_by_ids.total", perf_counter() - started_at
        )
        return [self._row_to_message(row) for row in rows]

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
            rows = conn.execute("""
                SELECT DISTINCT user_id, author_name
                FROM messages
                GROUP BY user_id
                ORDER BY author_name ASC
            """).fetchall()
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

    def get_primary_targets(self) -> List[PrimaryTarget]:
        try:
            with self._read_connection() as conn:
                rows = conn.execute("""
                    SELECT
                        t.*, u.username, u.first_name, u.last_name, c.title as chat_title,
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
                    ORDER BY t.author_name ASC
                """).fetchall()
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

    def get_user_messages(self, user_id: int) -> List[MessageData]:
        with self._read_connection() as conn:
            rows = conn.execute(
                """
                SELECT m.* FROM messages m
                JOIN message_target_links l ON m.chat_id = l.chat_id AND m.message_id = l.message_id
                WHERE l.target_user_id = ?
                ORDER BY m.timestamp ASC, m.message_id ASC
            """,
                (user_id,),
            ).fetchall()
            return [self._row_to_message(row) for row in rows]

    def get_user_export_summary(self, user_id: int) -> Optional[UserExportSummary]:
        with self._read_connection() as conn:
            count_row = conn.execute(
                """
                SELECT COUNT(*) AS message_count
                FROM messages m
                JOIN message_target_links l ON m.chat_id = l.chat_id AND m.message_id = l.message_id
                WHERE l.target_user_id = ?
            """,
                (user_id,),
            ).fetchone()

            message_count = count_row["message_count"] if count_row else 0
            if not message_count:
                return None

            first_row = conn.execute(
                """
                SELECT m.message_id, m.timestamp
                FROM messages m
                JOIN message_target_links l ON m.chat_id = l.chat_id AND m.message_id = l.message_id
                WHERE l.target_user_id = ?
                ORDER BY m.timestamp ASC, m.message_id ASC
                LIMIT 1
            """,
                (user_id,),
            ).fetchone()
            last_row = conn.execute(
                """
                SELECT m.message_id, m.timestamp
                FROM messages m
                JOIN message_target_links l ON m.chat_id = l.chat_id AND m.message_id = l.message_id
                WHERE l.target_user_id = ?
                ORDER BY m.timestamp DESC, m.message_id DESC
                LIMIT 1
            """,
                (user_id,),
            ).fetchone()
            author_row = conn.execute(
                """
                SELECT m.author_name
                FROM messages m
                JOIN message_target_links l ON m.chat_id = l.chat_id AND m.message_id = l.message_id
                WHERE l.target_user_id = ?
                  AND m.user_id = ?
                  AND COALESCE(TRIM(m.author_name), '') != ''
                ORDER BY m.timestamp ASC, m.message_id ASC
                LIMIT 1
            """,
                (user_id, user_id),
            ).fetchone()

            return UserExportSummary(
                message_count=int(message_count),
                first_message_id=first_row["message_id"],
                last_message_id=last_row["message_id"],
                first_timestamp=first_row["timestamp"],
                last_timestamp=last_row["timestamp"],
                target_author_name=author_row["author_name"] if author_row else None,
            )

    def iter_user_export_rows(self, user_id: int, chunk_size: int = 1000):
        started_at = perf_counter()
        yielded = 0
        with self._read_connection() as conn:
            cursor = conn.execute(
                """
                SELECT
                    m.message_id,
                    m.chat_id,
                    m.user_id,
                    m.author_name,
                    m.timestamp,
                    m.text,
                    m.media_type,
                    m.reply_to_id,
                    m.fwd_from_id,
                    m.context_group_id,
                    m.raw_payload,
                    0 AS is_service
                FROM messages m
                JOIN message_target_links l ON m.chat_id = l.chat_id AND m.message_id = l.message_id
                WHERE l.target_user_id = ?
                ORDER BY m.timestamp ASC, m.message_id ASC
            """,
                (user_id,),
            )
            try:
                while True:
                    rows = cursor.fetchmany(chunk_size)
                    if not rows:
                        break
                    for row in rows:
                        yielded += 1
                        yield UserExportRow.coerce(dict(row))
            finally:
                telemetry.track_counter("storage.iter_user_export_rows.calls", 1)
                telemetry.track_counter("storage.iter_user_export_rows.rows", yielded)
                telemetry.track_duration(
                    "storage.iter_user_export_rows.total", perf_counter() - started_at
                )

    def get_user_export_rows(self, user_id: int) -> List[UserExportRow]:
        with self._read_connection() as conn:
            rows = conn.execute(
                """
                SELECT
                    m.message_id,
                    m.chat_id,
                    m.user_id,
                    m.author_name,
                    m.timestamp,
                    m.text,
                    m.media_type,
                    m.reply_to_id,
                    m.fwd_from_id,
                    m.context_group_id,
                    m.raw_payload,
                    0 AS is_service
                FROM messages m
                JOIN message_target_links l ON m.chat_id = l.chat_id AND m.message_id = l.message_id
                WHERE l.target_user_id = ?
                ORDER BY m.timestamp ASC, m.message_id ASC
            """,
                (user_id,),
            ).fetchall()
            return [UserExportRow.coerce(dict(row)) for row in rows]

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

    def get_report_database_summary(self) -> ReportDatabaseSummary:
        with self._read_connection() as conn:
            row = conn.execute(
                """
                SELECT
                    (SELECT COUNT(*) FROM chats) AS chats_count,
                    (SELECT COUNT(*) FROM users) AS users_count,
                    (SELECT COUNT(*) FROM messages) AS messages_count,
                    (SELECT COUNT(*) FROM sync_targets) AS targets_count,
                    (SELECT COUNT(*) FROM sync_targets WHERE is_complete = 0) AS incomplete_targets_count,
                    (SELECT COUNT(*) FROM message_target_links) AS target_links_count,
                    (SELECT COUNT(*) FROM messages WHERE reply_to_id IS NOT NULL) AS reply_messages_count,
                    (
                        SELECT COUNT(*)
                        FROM messages m
                        WHERE m.reply_to_id IS NOT NULL
                          AND NOT EXISTS (
                              SELECT 1
                              FROM messages parent
                              WHERE parent.chat_id = m.chat_id
                                AND parent.message_id = m.reply_to_id
                          )
                    ) AS missing_parent_count,
                    (
                        SELECT COUNT(DISTINCT context_group_id)
                        FROM messages
                        WHERE COALESCE(TRIM(context_group_id), '') != ''
                    ) AS context_cluster_count
            """
            ).fetchone()
        return ReportDatabaseSummary(
            chats_count=int(row["chats_count"] or 0),
            users_count=int(row["users_count"] or 0),
            messages_count=int(row["messages_count"] or 0),
            targets_count=int(row["targets_count"] or 0),
            incomplete_targets_count=int(row["incomplete_targets_count"] or 0),
            target_links_count=int(row["target_links_count"] or 0),
            reply_messages_count=int(row["reply_messages_count"] or 0),
            missing_parent_count=int(row["missing_parent_count"] or 0),
            context_cluster_count=int(row["context_cluster_count"] or 0),
        )

    def get_report_target_summaries(self) -> List[ReportTargetSummary]:
        with self._read_connection() as conn:
            rows = conn.execute(
                """
                SELECT
                    t.user_id,
                    t.chat_id,
                    t.author_name,
                    c.title AS chat_title,
                    t.last_msg_id,
                    t.tail_msg_id,
                    t.is_complete,
                    t.deep_mode,
                    t.recursive_depth,
                    COALESCE(t.last_sync_at, 0) AS last_sync_at,
                    COUNT(l.message_id) AS linked_messages,
                    COALESCE(SUM(CASE WHEN m.user_id = t.user_id THEN 1 ELSE 0 END), 0) AS own_messages,
                    COALESCE(SUM(CASE WHEN m.user_id != t.user_id THEN 1 ELSE 0 END), 0) AS context_messages,
                    COALESCE(SUM(
                        CASE
                            WHEN m.reply_to_id IS NOT NULL
                             AND NOT EXISTS (
                                 SELECT 1
                                 FROM messages parent
                                 WHERE parent.chat_id = m.chat_id
                                   AND parent.message_id = m.reply_to_id
                             )
                            THEN 1
                            ELSE 0
                        END
                    ), 0) AS missing_parent_messages
                FROM sync_targets t
                LEFT JOIN chats c ON c.chat_id = t.chat_id
                LEFT JOIN message_target_links l
                    ON l.chat_id = t.chat_id AND l.target_user_id = t.user_id
                LEFT JOIN messages m
                    ON m.chat_id = l.chat_id AND m.message_id = l.message_id
                GROUP BY
                    t.user_id,
                    t.chat_id,
                    t.author_name,
                    c.title,
                    t.last_msg_id,
                    t.tail_msg_id,
                    t.is_complete,
                    t.deep_mode,
                    t.recursive_depth,
                    t.last_sync_at
                ORDER BY COALESCE(t.author_name, ''), t.chat_id, t.user_id
            """
            ).fetchall()
        return [
            ReportTargetSummary(
                user_id=int(row["user_id"] or 0),
                chat_id=int(row["chat_id"] or 0),
                author_name=row["author_name"],
                chat_title=row["chat_title"],
                last_msg_id=int(row["last_msg_id"] or 0),
                tail_msg_id=int(row["tail_msg_id"] or 0),
                is_complete=bool(int(row["is_complete"] or 0)),
                deep_mode=bool(int(row["deep_mode"] or 0)),
                recursive_depth=int(row["recursive_depth"] or 0),
                last_sync_at=int(row["last_sync_at"] or 0),
                linked_messages=int(row["linked_messages"] or 0),
                own_messages=int(row["own_messages"] or 0),
                context_messages=int(row["context_messages"] or 0),
                missing_parent_messages=int(row["missing_parent_messages"] or 0),
            )
            for row in rows
        ]

    def get_report_retry_summary(
        self, now_ts: Optional[int] = None
    ) -> ReportRetrySummary:
        due_at = now_ts if now_ts is not None else int(datetime.now().timestamp())
        with self._read_connection() as conn:
            row = conn.execute(
                """
                SELECT
                    COUNT(*) AS total_tasks,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) AS pending_tasks,
                    SUM(CASE WHEN status = 'retrying' THEN 1 ELSE 0 END) AS retrying_tasks,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed_tasks,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed_tasks,
                    SUM(
                        CASE
                            WHEN status IN ('pending', 'retrying')
                             AND next_retry_timestamp <= ?
                            THEN 1
                            ELSE 0
                        END
                    ) AS due_tasks
                FROM retry_queue
            """,
                (due_at,),
            ).fetchone()
        return ReportRetrySummary(
            total_tasks=int(row["total_tasks"] or 0),
            pending_tasks=int(row["pending_tasks"] or 0),
            retrying_tasks=int(row["retrying_tasks"] or 0),
            completed_tasks=int(row["completed_tasks"] or 0),
            failed_tasks=int(row["failed_tasks"] or 0),
            due_tasks=int(row["due_tasks"] or 0),
        )

    def get_due_retry_tasks(
        self,
        now_ts: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[RetryTaskRecord]:
        due_at = now_ts if now_ts is not None else int(datetime.now().timestamp())
        limit_clause = f" LIMIT {int(limit)}" if limit else ""
        with self._read_connection() as conn:
            rows = conn.execute(
                f"""
                SELECT * FROM retry_queue
                WHERE status IN ('pending', 'retrying')
                  AND next_retry_timestamp <= ?
                ORDER BY next_retry_timestamp ASC, retry_count ASC, created_at ASC
                {limit_clause}
            """,
                (due_at,),
            ).fetchall()
            return [RetryTaskRecord.coerce(dict(row)) for row in rows]

    def get_retry_tasks(self) -> List[RetryTaskRecord]:
        return self.get_due_retry_tasks()

    def list_retry_tasks(
        self,
        limit: Optional[int] = None,
        include_completed: bool = True,
    ) -> List[RetryTaskRecord]:
        clauses = []
        params: list[Any] = []
        if not include_completed:
            clauses.append("status IN ('pending', 'retrying')")
        where_clause = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        limit_clause = f" LIMIT {int(limit)}" if limit else ""
        with self._read_connection() as conn:
            rows = conn.execute(
                f"""
                SELECT * FROM retry_queue
                {where_clause}
                ORDER BY
                    CASE status
                        WHEN 'pending' THEN 0
                        WHEN 'retrying' THEN 1
                        WHEN 'failed' THEN 2
                        ELSE 3
                    END,
                    next_retry_timestamp ASC,
                    updated_at DESC
                {limit_clause}
            """,
                params,
            ).fetchall()
            return [RetryTaskRecord.coerce(dict(row)) for row in rows]
