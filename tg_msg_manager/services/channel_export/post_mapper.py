from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from .media_types import normalize_media_type
from .media_policy import (
    MEDIA_MODE_NONE,
    build_media_relative_path,
    initial_download_status,
    validate_media_mode,
)
from .models import ChannelIdentity, ChannelMediaRecord, ChannelPostRecord


def _coerce_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)
    if isinstance(value, str):
        normalized = value.strip()
        if normalized.endswith("Z"):
            normalized = normalized[:-1] + "+00:00"
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError:
            return datetime.fromtimestamp(0, tz=timezone.utc)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed
    return datetime.fromtimestamp(0, tz=timezone.utc)


def _coerce_plain_reactions(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    if isinstance(value, list):
        return {"items": value}
    return {}


def _extract_media_metadata(message: Any) -> Optional[Dict[str, Any]]:
    media_ref = getattr(message, "media_ref", None)
    if isinstance(media_ref, dict):
        return dict(media_ref)
    raw_payload = getattr(message, "raw_payload", {}) or {}
    media_payload = raw_payload.get("media")
    if isinstance(media_payload, dict):
        return dict(media_payload)
    if getattr(message, "media_type", None):
        return {}
    return None


class ChannelPostMapper:
    def __init__(self, media_policy: Any):
        self.media_policy = media_policy

    def map_post(
        self,
        message: Any,
        channel: ChannelIdentity,
        *,
        media_mode: str,
    ) -> ChannelPostRecord:
        normalized_mode = validate_media_mode(media_mode)
        raw_payload = dict(getattr(message, "raw_payload", {}) or {})
        timestamp = _coerce_datetime(
            getattr(message, "timestamp", None)
            or getattr(message, "date", None)
            or raw_payload.get("date")
        )

        text = (
            getattr(message, "text", None)
            or getattr(message, "message", None)
            or raw_payload.get("message")
        )
        views = getattr(message, "views", None)
        if views is None:
            views = raw_payload.get("views")
        forwards = getattr(message, "forwards", None)
        if forwards is None:
            forwards = raw_payload.get("forwards")
        replies_count = getattr(message, "replies_count", None)
        if replies_count is None:
            replies_count = raw_payload.get("replies_count")
        reactions = _coerce_plain_reactions(
            getattr(message, "reactions", None) or raw_payload.get("reactions")
        )

        media_records: Tuple[ChannelMediaRecord, ...] = ()
        if normalized_mode != MEDIA_MODE_NONE:
            media_records = self._map_media_records(
                message=message,
                media_mode=normalized_mode,
            )

        return ChannelPostRecord(
            message_id=int(getattr(message, "message_id")),
            channel_id=channel.channel_id,
            channel_title=channel.title,
            channel_username=channel.username,
            timestamp=timestamp,
            text=text,
            views=views,
            forwards=forwards,
            replies_count=replies_count,
            reactions=reactions,
            media=media_records,
            raw_payload=raw_payload,
        )

    def _map_media_records(
        self,
        *,
        message: Any,
        media_mode: str,
    ) -> Tuple[ChannelMediaRecord, ...]:
        media_metadata = _extract_media_metadata(message)
        if media_metadata is None:
            return ()

        media_type = (
            media_metadata.get("media_type")
            or getattr(message, "media_type", None)
            or media_metadata.get("_")
        )
        mime_type = media_metadata.get("mime_type")
        file_name = media_metadata.get("file_name") or media_metadata.get("filename")
        file_size = media_metadata.get("file_size") or media_metadata.get("size")
        width = media_metadata.get("width")
        height = media_metadata.get("height")
        duration = media_metadata.get("duration")
        media_index = 1
        message_id = int(getattr(message, "message_id"))
        local_path = build_media_relative_path(
            message_id=message_id,
            media_index=media_index,
            media_type=media_type,
            mime_type=mime_type,
            file_name=file_name,
        )
        normalized_media_type = (
            normalize_media_type(media_type, mime_type) or media_type
        )
        return (
            ChannelMediaRecord(
                media_id=f"{message_id}_{media_index:02d}",
                message_id=message_id,
                media_index=media_index,
                media_type=normalized_media_type,
                mime_type=mime_type,
                file_name=file_name,
                file_size=file_size,
                width=width,
                height=height,
                duration=duration,
                local_path=local_path,
                sha256=None,
                download_status=initial_download_status(media_mode),
            ),
        )
