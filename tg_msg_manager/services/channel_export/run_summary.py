from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .models import ChannelPostRecord


@dataclass(frozen=True)
class ChannelRunSummary:
    message_ids: tuple[int, ...]
    first_message_id: Optional[int]
    last_message_id: Optional[int]
    first_message_timestamp: Optional[datetime]
    last_message_timestamp: Optional[datetime]
    message_count: int


class ChannelRunSummaryBuilder:
    def __init__(self) -> None:
        self._message_ids: list[int] = []
        self._first_message_id: Optional[int] = None
        self._last_message_id: Optional[int] = None
        self._first_message_timestamp: Optional[datetime] = None
        self._last_message_timestamp: Optional[datetime] = None

    def record(self, post: ChannelPostRecord) -> None:
        if self._first_message_id is None:
            self._first_message_id = post.message_id
            self._first_message_timestamp = post.timestamp
        self._message_ids.append(post.message_id)
        self._last_message_id = post.message_id
        self._last_message_timestamp = post.timestamp

    def build(self) -> ChannelRunSummary:
        return ChannelRunSummary(
            message_ids=tuple(self._message_ids),
            first_message_id=self._first_message_id,
            last_message_id=self._last_message_id,
            first_message_timestamp=self._first_message_timestamp,
            last_message_timestamp=self._last_message_timestamp,
            message_count=len(self._message_ids),
        )
