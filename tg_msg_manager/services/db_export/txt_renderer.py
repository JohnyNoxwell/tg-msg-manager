from typing import Any, Dict, Optional

from ...core.models.message import MessageData
from ..rendering import LegacyTxtRenderer


class DBExportTxtRenderer:
    def __init__(self, legacy_renderer: Optional[LegacyTxtRenderer] = None):
        self.legacy_renderer = legacy_renderer or LegacyTxtRenderer()

    def format_block(
        self,
        *,
        message: MessageData,
        msg_lookup: Dict[int, MessageData],
        last_date: Any,
        last_author_id: Optional[int],
    ) -> tuple[str, Any, Optional[int]]:
        return self.legacy_renderer.format_block(
            message=message,
            msg_lookup=msg_lookup,
            last_date=last_date,
            last_author_id=last_author_id,
        )

    def format_message(self, message: MessageData) -> str:
        dt_str = message.timestamp.strftime("%Y-%m-%d][%H:%M:%S")
        reply_str = (
            f" (в ответ на {message.reply_to_id})" if message.reply_to_id else ""
        )
        fwd_str = f" [FWD from {message.fwd_from_id}]" if message.fwd_from_id else ""
        media_str = f" [{message.media_type}]" if message.media_type else ""
        author = message.author_name or f"User_{message.user_id}"
        header = (
            f"[{dt_str}] <{author} ({message.user_id})>{reply_str}{fwd_str}{media_str}:"
        )
        return f"{header}\n{message.text or '(пусто)'}"
