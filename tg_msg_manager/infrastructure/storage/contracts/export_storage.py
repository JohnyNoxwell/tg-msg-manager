from typing import Protocol, runtime_checkable

from .common import (
    MessageReadStorage,
    MessageWriteStorage,
    StopAwareStorage,
    SyncStateStorage,
    TargetLinkReadStorage,
    TargetRegistryStorage,
    UserReadStorage,
)


@runtime_checkable
class ExportStorage(
    MessageWriteStorage,
    MessageReadStorage,
    UserReadStorage,
    TargetLinkReadStorage,
    TargetRegistryStorage,
    SyncStateStorage,
    StopAwareStorage,
    Protocol,
):
    async def flush(self) -> None:
        """Waits until queued writes are persisted."""
