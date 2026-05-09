import json
from datetime import date, datetime, time
from typing import Any, Dict

from .models import (
    ChannelDiscussionCommentRecord,
    ChannelDiscussionMetadataRecord,
    ChannelDiscussionThreadRecord,
)


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


def discussion_comment_to_dict(
    record: ChannelDiscussionCommentRecord,
) -> Dict[str, Any]:
    return {
        "message_id": record.message_id,
        "discussion_chat_id": record.discussion_chat_id,
        "channel_id": record.channel_id,
        "channel_message_id": record.channel_message_id,
        "discussion_root_message_id": record.discussion_root_message_id,
        "author_id": record.author_id,
        "author_name": record.author_name,
        "username": record.username,
        "timestamp": record.timestamp.isoformat(),
        "text": record.text,
        "reply_to_id": record.reply_to_id,
        "media": [_make_json_safe(item) for item in record.media],
        "reactions": _make_json_safe(record.reactions),
        "raw_payload": _make_json_safe(record.raw_payload),
    }


def discussion_thread_to_dict(record: ChannelDiscussionThreadRecord) -> Dict[str, Any]:
    return {
        "channel_id": record.channel_id,
        "channel_username": record.channel_username,
        "channel_message_id": record.channel_message_id,
        "discussion_chat_id": record.discussion_chat_id,
        "discussion_root_message_id": record.discussion_root_message_id,
        "comments_count": record.comments_count,
        "exported_comments_count": record.exported_comments_count,
        "status": record.status,
        "error": record.error,
    }


def discussion_metadata_to_dict(
    record: ChannelDiscussionMetadataRecord,
) -> Dict[str, Any]:
    return {
        "channel_id": record.channel_id,
        "channel_message_id": record.channel_message_id,
        "has_comments": record.has_comments,
        "discussion_chat_id": record.discussion_chat_id,
        "replies_count": record.replies_count,
        "comments_exported": record.comments_exported,
        "source": record.source,
    }


class ChannelDiscussionJsonlRenderer:
    def render_comment_line(self, record: ChannelDiscussionCommentRecord) -> str:
        return json.dumps(
            discussion_comment_to_dict(record),
            ensure_ascii=False,
            sort_keys=False,
        )

    def render_thread_line(self, record: ChannelDiscussionThreadRecord) -> str:
        return json.dumps(
            discussion_thread_to_dict(record),
            ensure_ascii=False,
            sort_keys=False,
        )

    def render_metadata_line(self, record: ChannelDiscussionMetadataRecord) -> str:
        return json.dumps(
            discussion_metadata_to_dict(record),
            ensure_ascii=False,
            sort_keys=False,
        )
