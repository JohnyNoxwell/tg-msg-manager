from time import perf_counter
from typing import List, Optional

from ....core.models.message import MessageData
from ....core.telemetry import telemetry
from .common import SQLiteReadCommonMixin


class SQLiteMessageReadMixin(SQLiteReadCommonMixin):
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
