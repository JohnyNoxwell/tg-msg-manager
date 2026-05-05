from typing import Protocol, runtime_checkable

from .common import (
    MessageReadStorage,
    MessageWriteStorage,
    StopAwareStorage,
    SyncStateStorage,
    TargetRegistryStorage,
)


@runtime_checkable
class SyncStorage(
    MessageWriteStorage,
    MessageReadStorage,
    TargetRegistryStorage,
    SyncStateStorage,
    StopAwareStorage,
    Protocol,
):
    """Storage contract for Telegram sync/update use cases."""
