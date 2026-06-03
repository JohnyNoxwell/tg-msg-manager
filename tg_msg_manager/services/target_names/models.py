from dataclasses import dataclass
from typing import Optional, Tuple

from ...infrastructure.storage.records import TargetNameTargetRecord


TARGET_NAME_FIELDS = ("username", "display_name", "title")


@dataclass(frozen=True)
class TargetNameCurrent:
    username: Optional[str] = None
    display_name: Optional[str] = None
    title: Optional[str] = None
    first_seen: Optional[int] = None
    last_seen: Optional[int] = None


@dataclass(frozen=True)
class TargetNameHistoryItem:
    observed_at: int
    field: str
    old_value: Optional[str]
    new_value: Optional[str]


@dataclass(frozen=True)
class TargetNamesResult:
    status: str
    target: str
    target_type: Optional[str] = None
    current: Optional[TargetNameCurrent] = None
    history: Tuple[TargetNameHistoryItem, ...] = ()
    matches: Tuple[TargetNameTargetRecord, ...] = ()

    @property
    def is_found(self) -> bool:
        return self.status == "found"
