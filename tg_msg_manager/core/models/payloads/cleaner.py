from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class CleanerDialogScanStartedPayload:
    index: int
    total: int
    name: str
    chat_id: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "total": self.total,
            "name": self.name,
            "chat_id": self.chat_id,
        }

    @classmethod
    def coerce(cls, value: Any) -> "CleanerDialogScanStartedPayload":
        if isinstance(value, cls):
            return value
        if isinstance(value, Mapping):
            return cls(
                index=int(value.get("index", 0) or 0),
                total=int(value.get("total", 0) or 0),
                name=str(value.get("name") or ""),
                chat_id=int(value.get("chat_id", 0) or 0),
            )
        raise TypeError(
            f"Unsupported cleaner dialog scan started payload: {type(value)!r}"
        )


@dataclass(frozen=True)
class CleanerDialogMessagesFoundPayload:
    name: str
    chat_id: int
    count: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "chat_id": self.chat_id,
            "count": self.count,
        }

    @classmethod
    def coerce(cls, value: Any) -> "CleanerDialogMessagesFoundPayload":
        if isinstance(value, cls):
            return value
        if isinstance(value, Mapping):
            return cls(
                name=str(value.get("name") or ""),
                chat_id=int(value.get("chat_id", 0) or 0),
                count=int(value.get("count", 0) or 0),
            )
        raise TypeError(
            f"Unsupported cleaner dialog messages found payload: {type(value)!r}"
        )
