import os
from typing import Optional

from ...core.models.message import MessageData
from ...core.models.payloads.private_archive import PrivateArchiveMediaStats


class PrivateArchiveMediaPolicy:
    def media_category(self, media_type: Optional[str]) -> str:
        if not media_type:
            return "documents"
        normalized = media_type.lower()
        if "photo" in normalized:
            return "photos"
        if "video" in normalized:
            return "videos"
        if "voice" in normalized or "audio" in normalized:
            return "voices"
        return "documents"

    def should_download(self, message: MessageData) -> bool:
        return bool(
            message.media_type and getattr(message, "media_ref", None) is not None
        )

    def target_path(self, *, media_dir: str, message: MessageData) -> str:
        category = self.media_category(message.media_type)
        target_dir = os.path.join(media_dir, category)
        os.makedirs(target_dir, exist_ok=True)
        return os.path.join(target_dir, f"{message.message_id}")

    def track_media_stats(
        self, stats: PrivateArchiveMediaStats, media_type: Optional[str]
    ) -> None:
        stats.increment(media_type)
