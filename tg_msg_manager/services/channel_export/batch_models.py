from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple


BATCH_STATUS_UPDATED = "updated"
BATCH_STATUS_NO_NEW_POSTS = "no_new_posts"
BATCH_STATUS_FAILED = "failed"


@dataclass(frozen=True)
class ChannelBatchUpdateItem:
    dataset_dir: Path
    channel: str
    status: str
    posts_exported: int = 0
    error: Optional[str] = None


@dataclass(frozen=True)
class ChannelBatchUpdateResult:
    items: Tuple[ChannelBatchUpdateItem, ...]

    @property
    def updated_count(self) -> int:
        return sum(item.status == BATCH_STATUS_UPDATED for item in self.items)

    @property
    def no_new_posts_count(self) -> int:
        return sum(item.status == BATCH_STATUS_NO_NEW_POSTS for item in self.items)

    @property
    def failed_count(self) -> int:
        return sum(item.status == BATCH_STATUS_FAILED for item in self.items)
