from typing import Optional, Protocol, runtime_checkable

from ....core.models.message import MessageData
from .common import MessageWriteStorage


@runtime_checkable
class ContextStorage(MessageWriteStorage, Protocol):
    def get_message(self, chat_id: int, message_id: int) -> Optional[MessageData]:
        """Retrieves a single stored message for deep-mode reply stitching."""
