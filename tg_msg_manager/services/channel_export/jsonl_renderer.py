import json
from datetime import date, datetime, time
from typing import Any, Dict

from .models import ChannelMediaRecord, ChannelPostRecord


def _make_json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _make_json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_make_json_safe(item) for item in value]
    if hasattr(value, "to_dict") and callable(value.to_dict):
        return _make_json_safe(value.to_dict())
    return repr(value)


def channel_media_to_dict(record: ChannelMediaRecord) -> Dict[str, Any]:
    return {
        "media_id": record.media_id,
        "message_id": record.message_id,
        "media_index": record.media_index,
        "media_type": record.media_type,
        "mime_type": record.mime_type,
        "file_name": record.file_name,
        "file_size": record.file_size,
        "width": record.width,
        "height": record.height,
        "duration": record.duration,
        "local_path": record.local_path,
        "sha256": record.sha256,
        "download_status": record.download_status,
    }


def channel_post_to_dict(record: ChannelPostRecord) -> Dict[str, Any]:
    return {
        "message_id": record.message_id,
        "channel_id": record.channel_id,
        "channel_title": record.channel_title,
        "channel_username": record.channel_username,
        "timestamp": record.timestamp.isoformat(),
        "text": record.text,
        "views": record.views,
        "forwards": record.forwards,
        "replies_count": record.replies_count,
        "reactions": _make_json_safe(record.reactions),
        "media": [channel_media_to_dict(item) for item in record.media],
        "raw_payload": _make_json_safe(record.raw_payload),
    }


class ChannelJsonlRenderer:
    def render_line(self, record: ChannelPostRecord) -> str:
        return json.dumps(
            channel_post_to_dict(record),
            ensure_ascii=False,
            sort_keys=False,
        )
