from time import perf_counter
from typing import List, Optional

from ....core.models.message import MessageData
from ....core.telemetry import telemetry
from ..records import (
    ExportRunRecord,
    ExportTargetRecord,
    UserExportRow,
    UserExportSummary,
)
from .common import SQLiteReadCommonMixin


class SQLiteExportReadMixin(SQLiteReadCommonMixin):
    def get_export_target(self, user_id: int) -> Optional[ExportTargetRecord]:
        with self._read_connection() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM export_targets
                WHERE target_user_id = ?
            """,
                (user_id,),
            ).fetchone()
            return ExportTargetRecord.coerce(dict(row)) if row else None

    def list_export_runs(
        self, user_id: int, limit: Optional[int] = None
    ) -> List[ExportRunRecord]:
        query = """
            SELECT *
            FROM export_runs
            WHERE target_user_id = ?
            ORDER BY started_at DESC, id DESC
        """
        params: list[object] = [user_id]
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)

        with self._read_connection() as conn:
            rows = conn.execute(query, tuple(params)).fetchall()
            return [ExportRunRecord.coerce(dict(row)) for row in rows]

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
