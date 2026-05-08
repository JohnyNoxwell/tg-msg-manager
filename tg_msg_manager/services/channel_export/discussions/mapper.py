from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from .models import ChannelDiscussionCommentRecord

DEFAULT_TIMESTAMP = datetime(1970, 1, 1, tzinfo=timezone.utc)


class ChannelDiscussionMapper:
    def map_comment(
        self,
        comment: Any,
        *,
        channel_post_record: Any,
        discussion_chat_id: int,
        discussion_root_message_id: Optional[int],
    ) -> ChannelDiscussionCommentRecord:
        sender = getattr(comment, "sender", None)
        return ChannelDiscussionCommentRecord(
            message_id=self._extract_int(comment, "message_id", "id") or 0,
            discussion_chat_id=discussion_chat_id,
            channel_id=channel_post_record.channel_id,
            channel_message_id=channel_post_record.message_id,
            discussion_root_message_id=discussion_root_message_id,
            author_id=self._extract_author_id(comment, sender),
            author_name=self._extract_author_name(comment, sender),
            username=self._extract_username(comment, sender),
            timestamp=self._extract_timestamp(comment),
            text=self._extract_text(comment),
            reply_to_id=self._extract_reply_to_id(comment),
            media=self._extract_media_metadata(comment),
            reactions=self._extract_mapping(comment, "reactions"),
            raw_payload=self._extract_raw_payload(comment),
        )

    @staticmethod
    def _extract_int(obj: Any, *attributes: str) -> Optional[int]:
        for attribute in attributes:
            value = getattr(obj, attribute, None)
            if value is not None:
                return int(value)
        return None

    def _extract_author_id(self, comment: Any, sender: Any) -> Optional[int]:
        value = self._extract_int(comment, "author_id", "user_id", "sender_id")
        if value is not None:
            return value
        if sender is not None:
            return self._extract_int(sender, "id", "user_id")
        return None

    @staticmethod
    def _extract_author_name(comment: Any, sender: Any) -> Optional[str]:
        explicit = getattr(comment, "author_name", None)
        if explicit:
            return str(explicit)
        if sender is None:
            return None
        for attribute in ("name", "title"):
            value = getattr(sender, attribute, None)
            if value:
                return str(value)
        first_name = getattr(sender, "first_name", None)
        last_name = getattr(sender, "last_name", None)
        full_name = " ".join(part for part in (first_name, last_name) if part).strip()
        return full_name or None

    @staticmethod
    def _extract_username(comment: Any, sender: Any) -> Optional[str]:
        value = getattr(comment, "username", None)
        if value:
            return str(value)
        if sender is not None:
            sender_username = getattr(sender, "username", None)
            if sender_username:
                return str(sender_username)
        return None

    @staticmethod
    def _extract_timestamp(comment: Any) -> datetime:
        value = getattr(comment, "timestamp", None) or getattr(comment, "date", None)
        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)
            return value
        return DEFAULT_TIMESTAMP

    @staticmethod
    def _extract_text(comment: Any) -> Optional[str]:
        value = getattr(comment, "text", None)
        if value is None:
            value = getattr(comment, "message", None)
        return str(value) if value is not None else None

    @staticmethod
    def _extract_reply_to_id(comment: Any) -> Optional[int]:
        value = getattr(comment, "reply_to_id", None)
        if value is not None:
            return int(value)
        reply_to = getattr(comment, "reply_to", None)
        value = getattr(reply_to, "reply_to_msg_id", None)
        return int(value) if value is not None else None

    def _extract_media_metadata(self, comment: Any) -> Tuple[Dict[str, Any], ...]:
        media = getattr(comment, "media", None)
        media_type = getattr(comment, "media_type", None)
        if media is None and media_type is None:
            return ()
        if isinstance(media, dict):
            return (self._media_dict_from_mapping(media, media_type),)
        return (
            {
                "media_type": media_type or type(media).__name__,
                "mime_type": getattr(media, "mime_type", None),
                "file_name": getattr(media, "file_name", None),
                "file_size": getattr(media, "file_size", None),
                "width": getattr(media, "width", None),
                "height": getattr(media, "height", None),
                "duration": getattr(media, "duration", None),
                "download_status": "metadata_only",
            },
        )

    @staticmethod
    def _media_dict_from_mapping(
        media: Dict[str, Any],
        media_type: Optional[str],
    ) -> Dict[str, Any]:
        return {
            "media_type": media_type or media.get("media_type"),
            "mime_type": media.get("mime_type"),
            "file_name": media.get("file_name"),
            "file_size": media.get("file_size"),
            "width": media.get("width"),
            "height": media.get("height"),
            "duration": media.get("duration"),
            "download_status": "metadata_only",
        }

    @staticmethod
    def _extract_mapping(comment: Any, attribute: str) -> Dict[str, Any]:
        value = getattr(comment, attribute, None)
        return dict(value) if isinstance(value, dict) else {}

    @staticmethod
    def _extract_raw_payload(comment: Any) -> Dict[str, Any]:
        value = getattr(comment, "raw_payload", None)
        if isinstance(value, dict):
            return dict(value)
        to_dict = getattr(comment, "to_dict", None)
        if callable(to_dict):
            payload = to_dict()
            return dict(payload) if isinstance(payload, dict) else {}
        return {}
