import json
import sqlite3
from datetime import datetime, timezone
from typing import Iterable, List

from ....core.models.message import MessageData


class SQLiteReadCommonMixin:
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
