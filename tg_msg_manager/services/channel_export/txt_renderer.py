from datetime import datetime, timezone

from .models import ChannelMediaRecord, ChannelPostRecord

SEPARATOR = "--------------------"
NO_TEXT_PLACEHOLDER = "<NO TEXT>"


def _format_timestamp(value: datetime) -> str:
    if value.tzinfo is None:
        normalized = value.replace(tzinfo=timezone.utc)
    else:
        normalized = value.astimezone(timezone.utc)
    return normalized.strftime("%Y-%m-%d %H:%M:%S UTC")


def _format_channel_label(record: ChannelPostRecord) -> str:
    title = (record.channel_title or "").strip()
    username = (record.channel_username or "").strip()
    if username and not username.startswith("@"):
        username = f"@{username}"
    if title and username:
        return f"{title} ({username})"
    if title:
        return title
    if username:
        return username
    return f"channel_id={record.channel_id}"


def _format_media_line(record: ChannelMediaRecord) -> str:
    media_kind = (
        record.media_type.lower()
        if record.media_type
        else (record.mime_type or "unknown")
    )
    local_path = record.local_path or "<no local path>"
    return f"- {media_kind}: {local_path} [{record.download_status}]"


class ChannelTxtRenderer:
    def render_block(self, record: ChannelPostRecord) -> str:
        lines = [
            (
                f"[{_format_timestamp(record.timestamp)}] "
                f"{_format_channel_label(record)} | message_id={record.message_id}"
            ),
            record.text if record.text else NO_TEXT_PLACEHOLDER,
        ]

        if record.media:
            lines.append("")
            lines.append("Media:")
            lines.extend(_format_media_line(item) for item in record.media)

        lines.append(SEPARATOR)
        return "\n".join(lines)
