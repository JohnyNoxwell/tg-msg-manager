from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional


@dataclass(frozen=True)
class RenderMessage:
    message_id: int
    chat_id: int
    user_id: int
    author_name: Optional[str]
    timestamp: datetime
    text: Optional[str]
    reply_to_id: Optional[int] = None
    media_type: Optional[str] = None
    fwd_from_id: Optional[int] = None
    context_group_id: Optional[str] = None

    @classmethod
    def coerce(cls, value: Any) -> "RenderMessage":
        if isinstance(value, cls):
            return value

        getter = (
            value.get
            if hasattr(value, "get")
            else lambda key, default=None: getattr(value, key, default)
        )
        timestamp = getter("timestamp")
        if not isinstance(timestamp, datetime):
            timestamp = datetime.fromtimestamp(int(timestamp or 0), tz=timezone.utc)

        reply_to_id = getter("reply_to_id")
        return cls(
            message_id=int(getter("message_id")),
            chat_id=int(getter("chat_id")),
            user_id=int(getter("user_id")),
            author_name=getter("author_name"),
            timestamp=timestamp,
            text=getter("text"),
            reply_to_id=int(reply_to_id) if reply_to_id is not None else None,
            media_type=getter("media_type"),
            fwd_from_id=getter("fwd_from_id"),
            context_group_id=(
                str(getter("context_group_id"))
                if getter("context_group_id") is not None
                else None
            ),
        )


@dataclass(frozen=True)
class TxtRenderOptions:
    profile: str
    target_user_id: Optional[int] = None
    target_author_name: Optional[str] = None
    chat_id: Optional[int] = None
    chat_title: Optional[str] = None
    include_ids: bool = True
    max_reply_excerpt_chars: int = 80
