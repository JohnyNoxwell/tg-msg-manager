import os

from ...utils.ui import UI
from .models import ArchiveContext
from .source_resolver import PrivateArchiveSourceDescriptor


class PrivateArchivePlanner:
    def __init__(self, *, base_dir: str):
        self.base_dir = base_dir

    def folder_name(self, descriptor: PrivateArchiveSourceDescriptor) -> str:
        name = UI.format_name(
            {
                "first_name": descriptor.first_name,
                "last_name": descriptor.last_name,
                "username": descriptor.username,
                "user_id": descriptor.user_id,
            }
        )
        safe_name = (
            "".join(c for c in name if c.isalnum() or c in (" ", "_"))
            .strip()
            .replace(" ", "_")
        )
        return f"{safe_name}_{descriptor.user_id}"

    def build_context(
        self, descriptor: PrivateArchiveSourceDescriptor
    ) -> ArchiveContext:
        folder_name = self.folder_name(descriptor)
        user_dir = os.path.join(self.base_dir, folder_name)
        media_dir = os.path.join(user_dir, "media")
        chat_log_path = os.path.join(user_dir, "chat_log.txt")
        return ArchiveContext(
            user_id=descriptor.user_id,
            target_name=descriptor.target_name,
            user_dir=user_dir,
            media_dir=media_dir,
            chat_log_path=chat_log_path,
        )
