import json
from typing import Any, Dict

from .models import ChannelMediaRecord


def media_record_to_dict(record: ChannelMediaRecord) -> Dict[str, Any]:
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
        "error": record.error,
    }


class ChannelMediaManifestWriter:
    def render_line(self, record: ChannelMediaRecord) -> str:
        return json.dumps(media_record_to_dict(record), ensure_ascii=False)
