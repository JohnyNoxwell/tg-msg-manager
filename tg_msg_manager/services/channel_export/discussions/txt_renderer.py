from datetime import datetime, timezone

from .models import ChannelDiscussionCommentRecord

SEPARATOR = "--------------------"
NO_TEXT_PLACEHOLDER = "<NO TEXT>"


def _format_timestamp(value: datetime) -> str:
    if value.tzinfo is None:
        normalized = value.replace(tzinfo=timezone.utc)
    else:
        normalized = value.astimezone(timezone.utc)
    return normalized.strftime("%Y-%m-%d %H:%M:%S UTC")


def _format_author(record: ChannelDiscussionCommentRecord) -> str:
    name = record.author_name or "Unknown author"
    details = []
    if record.author_id is not None:
        details.append(f"ID: {record.author_id}")
    if record.username:
        details.append(f"username: {record.username}")
    if not details:
        return name
    return f"{name} ({', '.join(details)})"


class ChannelDiscussionTxtRenderer:
    def render_comment_block(self, record: ChannelDiscussionCommentRecord) -> str:
        lines = [
            (
                f"--- Channel post {record.channel_message_id} / "
                f"discussion root {record.discussion_root_message_id} ---"
            ),
            f"[{_format_timestamp(record.timestamp)}] {_format_author(record)}:",
            record.text if record.text else NO_TEXT_PLACEHOLDER,
        ]
        if record.reply_to_id is not None:
            lines.append(f"reply_to_id={record.reply_to_id}")
        lines.append(SEPARATOR)
        return "\n".join(lines)
