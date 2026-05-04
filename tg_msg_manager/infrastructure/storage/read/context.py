from typing import List

from ....core.models.message import MessageData
from .common import SQLiteReadCommonMixin


class SQLiteContextReadMixin(SQLiteReadCommonMixin):
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
