from pathlib import Path

from .models import ChannelExportPlan, ChannelIdentity

MEDIA_SUBDIRECTORIES = (
    "photos",
    "videos",
    "documents",
    "audio",
    "voice",
    "animations",
    "thumbnails",
)


def sanitize_path_part(value: str, *, fallback: str = "unknown") -> str:
    stripped = (value or "").strip()
    if not stripped:
        return fallback

    has_prefix_at = stripped.startswith("@")
    sanitized_chars = []
    for char in stripped:
        if char in {"/", "\\"}:
            continue
        if ord(char) < 32 or ord(char) == 127:
            continue
        if char.isspace():
            sanitized_chars.append("_")
            continue
        if char.isalnum() or char in {"@", ".", "_", "-"}:
            sanitized_chars.append(char)
            continue
        sanitized_chars.append("_")

    sanitized = "".join(sanitized_chars).strip("._-@")
    if has_prefix_at and sanitized:
        sanitized = "@" + sanitized.lstrip("@")
    sanitized = sanitized[:120].rstrip("._-")
    return sanitized or fallback


def build_channel_directory_name(channel: ChannelIdentity) -> str:
    if channel.username:
        username = sanitize_path_part(channel.username, fallback="channel")
        username = username if username.startswith("@") else f"@{username.lstrip('@')}"
        return f"{username}__{channel.channel_id}"
    if channel.title:
        title = sanitize_path_part(channel.title, fallback="channel")
        return f"{title}__channel_{channel.channel_id}"
    return f"channel_{channel.channel_id}"


class ChannelExportPlanBuilder:
    def build(self, base_dir: Path, channel: ChannelIdentity) -> ChannelExportPlan:
        output_dir = Path(base_dir) / build_channel_directory_name(channel)
        media_dir = output_dir / "media"

        output_dir.mkdir(parents=True, exist_ok=True)
        media_dir.mkdir(parents=True, exist_ok=True)
        for subdirectory in MEDIA_SUBDIRECTORIES:
            (media_dir / subdirectory).mkdir(parents=True, exist_ok=True)

        return ChannelExportPlan(
            output_dir=output_dir,
            manifest_path=output_dir / "manifest.json",
            messages_jsonl_path=output_dir / "messages.jsonl",
            messages_txt_path=output_dir / "messages.txt",
            media_manifest_path=output_dir / "media_manifest.jsonl",
            state_path=output_dir / "channel_export_state.json",
            media_dir=media_dir,
        )
