from typing import List, Optional

from ..records import (
    TargetNameResolutionRecord,
    TargetNameSnapshotRecord,
    TargetNameTargetRecord,
)
from .common import SQLiteReadCommonMixin


class SQLiteTargetNamesReadMixin(SQLiteReadCommonMixin):
    def resolve_target_name_target(self, target: str) -> TargetNameResolutionRecord:
        query = str(target).strip()
        matches: list[TargetNameTargetRecord] = []

        with self._read_connection() as conn:
            numeric_id = _parse_numeric_target(query)
            if numeric_id is not None:
                user = _read_user_target(conn, numeric_id)
                if user:
                    matches.append(user)
                chat = _read_chat_target(conn, numeric_id)
                if chat:
                    matches.append(chat)
            else:
                username = _normalize_username(query)
                if username:
                    rows = conn.execute(
                        """
                        SELECT DISTINCT user_id
                        FROM (
                            SELECT user_id
                            FROM users
                            WHERE LOWER(TRIM(username)) = ?
                            UNION
                            SELECT user_id
                            FROM user_identity_history
                            WHERE LOWER(TRIM(username)) = ?
                        )
                        ORDER BY user_id ASC
                    """,
                        (username, username),
                    ).fetchall()
                    matches.extend(
                        item
                        for row in rows
                        if (item := _read_user_target(conn, int(row["user_id"])))
                    )

        if not matches:
            return TargetNameResolutionRecord(status="not_found", target=query)
        if len(matches) > 1:
            return TargetNameResolutionRecord(
                status="ambiguous",
                target=query,
                matches=tuple(matches),
            )
        return TargetNameResolutionRecord(
            status="found",
            target=query,
            matches=(matches[0],),
        )

    def get_target_name_snapshots(
        self, target: TargetNameTargetRecord
    ) -> List[TargetNameSnapshotRecord]:
        if target.target_type != "user":
            return []

        with self._read_connection() as conn:
            rows = conn.execute(
                """
                SELECT
                    user_id AS target_id,
                    'user' AS target_type,
                    observed_at,
                    username,
                    author_name AS display_name,
                    NULL AS title
                FROM user_identity_history
                WHERE user_id = ?
                ORDER BY observed_at ASC, COALESCE(source_message_id, 0) ASC
            """,
                (target.target_id,),
            ).fetchall()
            return [TargetNameSnapshotRecord.coerce(dict(row)) for row in rows]


def _parse_numeric_target(value: str) -> Optional[int]:
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _normalize_username(value: str) -> Optional[str]:
    text = value.strip()
    if text.startswith("@"):
        text = text[1:]
    text = text.strip().lower()
    return text or None


def _read_user_target(conn, user_id: int) -> Optional[TargetNameTargetRecord]:
    exists = conn.execute(
        """
        SELECT 1
        FROM users
        WHERE user_id = ?
        UNION
        SELECT 1
        FROM sync_targets
        WHERE user_id = ?
        UNION
        SELECT 1
        FROM user_identity_history
        WHERE user_id = ?
        LIMIT 1
    """,
        (user_id, user_id, user_id),
    ).fetchone()
    if not exists:
        return None

    row = conn.execute(
        """
        SELECT
            ? AS target_id,
            'user' AS target_type,
            COALESCE(
                NULLIF(TRIM(u.username), ''),
                (
                    SELECT NULLIF(TRIM(h.username), '')
                    FROM user_identity_history h
                    WHERE h.user_id = ?
                      AND COALESCE(TRIM(h.username), '') != ''
                    ORDER BY h.observed_at DESC, COALESCE(h.source_message_id, 0) DESC
                    LIMIT 1
                )
            ) AS current_username,
            COALESCE(
                NULLIF(TRIM(u.current_author_name), ''),
                (
                    SELECT NULLIF(TRIM(h.author_name), '')
                    FROM user_identity_history h
                    WHERE h.user_id = ?
                      AND COALESCE(TRIM(h.author_name), '') != ''
                    ORDER BY h.observed_at DESC, COALESCE(h.source_message_id, 0) DESC
                    LIMIT 1
                ),
                (
                    SELECT NULLIF(TRIM(t.author_name), '')
                    FROM sync_targets t
                    WHERE t.user_id = ?
                      AND COALESCE(TRIM(t.author_name), '') != ''
                    ORDER BY COALESCE(NULLIF(t.last_sync_at, 0), NULLIF(t.added_at, 0), 0) DESC,
                             t.chat_id DESC
                    LIMIT 1
                )
            ) AS current_display_name,
            NULL AS current_title,
            (
                SELECT MIN(observed_at)
                FROM user_identity_history
                WHERE user_id = ?
            ) AS history_first_seen,
            (
                SELECT MAX(observed_at)
                FROM user_identity_history
                WHERE user_id = ?
            ) AS history_last_seen,
            (
                SELECT MIN(added_at)
                FROM sync_targets
                WHERE user_id = ?
            ) AS target_first_seen,
            (
                SELECT MAX(COALESCE(NULLIF(last_sync_at, 0), NULLIF(added_at, 0), 0))
                FROM sync_targets
                WHERE user_id = ?
            ) AS target_last_seen
        FROM (SELECT 1) seed
        LEFT JOIN users u ON u.user_id = ?
    """,
        (
            user_id,
            user_id,
            user_id,
            user_id,
            user_id,
            user_id,
            user_id,
            user_id,
            user_id,
        ),
    ).fetchone()
    if not row:
        return None

    data = dict(row)
    data["first_seen"] = _min_known(
        data["history_first_seen"], data["target_first_seen"]
    )
    data["last_seen"] = _max_known(data["history_last_seen"], data["target_last_seen"])
    return TargetNameTargetRecord.coerce(data)


def _read_chat_target(conn, chat_id: int) -> Optional[TargetNameTargetRecord]:
    row = conn.execute(
        """
        SELECT
            chat_id AS target_id,
            COALESCE(NULLIF(TRIM(type), ''), 'chat') AS target_type,
            NULL AS current_username,
            NULL AS current_display_name,
            title AS current_title,
            NULL AS first_seen,
            NULL AS last_seen
        FROM chats
        WHERE chat_id = ?
    """,
        (chat_id,),
    ).fetchone()
    return TargetNameTargetRecord.coerce(dict(row)) if row else None


def _min_known(*values):
    known = [int(value) for value in values if value is not None]
    return min(known) if known else None


def _max_known(*values):
    known = [int(value) for value in values if value is not None]
    return max(known) if known else None
