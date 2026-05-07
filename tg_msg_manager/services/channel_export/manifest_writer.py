import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from .models import ChannelIdentity


def _isoformat_or_none(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None
    return value.isoformat()


def _detect_formats(included_files: Tuple[str, ...]) -> list[str]:
    formats = []
    for file_name in included_files:
        if file_name.endswith(".jsonl") and "jsonl" not in formats:
            formats.append("jsonl")
        elif file_name.endswith(".txt") and "txt" not in formats:
            formats.append("txt")
        elif file_name.endswith(".json") and "json" not in formats:
            formats.append("json")
    return formats


def build_manifest(
    *,
    channel: ChannelIdentity,
    message_count: int,
    media_count: int,
    downloaded_media_count: int,
    skipped_media_count: int,
    date_from: Optional[datetime],
    date_to: Optional[datetime],
    media_mode: str,
    included_files: Tuple[str, ...],
    status: str = "completed",
) -> Dict[str, Any]:
    return {
        "dataset_type": "direct_channel_export",
        "schema_version": "1.0",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "source": {
            "type": "channel",
            "id": channel.channel_id,
            "username": channel.username,
            "title": channel.title,
        },
        "export": {
            "message_count": message_count,
            "media_count": media_count,
            "downloaded_media_count": downloaded_media_count,
            "skipped_media_count": skipped_media_count,
            "date_from": _isoformat_or_none(date_from),
            "date_to": _isoformat_or_none(date_to),
            "formats": _detect_formats(included_files),
            "media_mode": media_mode,
            "included_files": list(included_files),
        },
        "status": status,
    }


class ChannelManifestWriter:
    def write(self, path: Path, manifest: Dict[str, Any]) -> None:
        target_path = Path(path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
