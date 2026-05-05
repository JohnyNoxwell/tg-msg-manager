from typing import Set

from .models import MessageKey


class ProcessedMessageDeduplicator:
    def __init__(self):
        self.processed_ids: Set[MessageKey] = set()

    def reset(self) -> None:
        self.processed_ids.clear()
