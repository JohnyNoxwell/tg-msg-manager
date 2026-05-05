from typing import Protocol, runtime_checkable

from .common import CleanupStorage, MessageReadStorage


@runtime_checkable
class CleanerStorage(MessageReadStorage, CleanupStorage, Protocol):
    """Storage contract required by CleanerService."""
