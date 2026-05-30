from typing import Protocol, runtime_checkable

from .common import (
    MessageReadStorage,
    MessageWriteStorage,
    StorageLifecycle,
    TargetRegistryStorage,
)


@runtime_checkable
class PrivateArchiveStorage(
    MessageWriteStorage,
    MessageReadStorage,
    TargetRegistryStorage,
    StorageLifecycle,
    Protocol,
):
    def update_last_sync_at(self, chat_id: int, user_id: int) -> None:
        """Marks the PM archive target as freshly synced."""
