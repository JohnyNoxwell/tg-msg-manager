from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class ExportSyncStartedPayload:
    chat_title: str
    user_label: str = ""
    deep_mode: bool = False
    depth: int = 0
    status_kind: Optional[str] = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "chat_title": self.chat_title,
            "user_label": self.user_label,
            "deep_mode": self.deep_mode,
            "depth": self.depth,
            "status_kind": self.status_kind,
        }

    @classmethod
    def coerce(cls, value: Any) -> "ExportSyncStartedPayload":
        if isinstance(value, cls):
            return value
        if isinstance(value, Mapping):
            return cls(
                chat_title=str(value.get("chat_title") or ""),
                user_label=str(value.get("user_label") or ""),
                deep_mode=bool(value.get("deep_mode", False)),
                depth=int(value.get("depth", 0) or 0),
                status_kind=value.get("status_kind"),
            )
        raise TypeError(f"Unsupported export sync started payload: {type(value)!r}")


@dataclass(frozen=True)
class ExportSyncSummaryPayload:
    title: str
    own_messages: int
    with_context: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "own_messages": self.own_messages,
            "with_context": self.with_context,
        }

    @classmethod
    def coerce(cls, value: Any) -> "ExportSyncSummaryPayload":
        if isinstance(value, cls):
            return value
        if isinstance(value, Mapping):
            return cls(
                title=str(value.get("title") or ""),
                own_messages=int(value.get("own_messages", 0) or 0),
                with_context=int(value.get("with_context", 0) or 0),
            )
        raise TypeError(f"Unsupported export sync summary payload: {type(value)!r}")


@dataclass(frozen=True)
class ExportSyncProgressPayload:
    db_total: int
    extra: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "db_total": self.db_total,
            "extra": self.extra,
        }

    @classmethod
    def coerce(cls, value: Any) -> "ExportSyncProgressPayload":
        if isinstance(value, cls):
            return value
        if isinstance(value, Mapping):
            return cls(
                db_total=int(value.get("db_total", 0) or 0),
                extra=str(value.get("extra") or ""),
            )
        raise TypeError(f"Unsupported export sync progress payload: {type(value)!r}")


@dataclass(frozen=True)
class ExportSyncFinishedPayload:
    db_count: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "db_count": self.db_count,
        }

    @classmethod
    def coerce(cls, value: Any) -> "ExportSyncFinishedPayload":
        if isinstance(value, cls):
            return value
        if isinstance(value, Mapping):
            return cls(db_count=int(value.get("db_count", 0) or 0))
        raise TypeError(f"Unsupported export sync finished payload: {type(value)!r}")


@dataclass(frozen=True)
class ExportTargetedDialogSearchStartedPayload:
    from_user_id: int
    dialog_count: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "from_user_id": self.from_user_id,
            "dialog_count": self.dialog_count,
        }

    @classmethod
    def coerce(cls, value: Any) -> "ExportTargetedDialogSearchStartedPayload":
        if isinstance(value, cls):
            return value
        if isinstance(value, Mapping):
            return cls(
                from_user_id=int(value.get("from_user_id", 0) or 0),
                dialog_count=int(value.get("dialog_count", 0) or 0),
            )
        raise TypeError(
            f"Unsupported targeted dialog search started payload: {type(value)!r}"
        )


@dataclass(frozen=True)
class ExportDialogSearchStartedPayload:
    from_user_id: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "from_user_id": self.from_user_id,
        }

    @classmethod
    def coerce(cls, value: Any) -> "ExportDialogSearchStartedPayload":
        if isinstance(value, cls):
            return value
        if isinstance(value, Mapping):
            return cls(from_user_id=int(value.get("from_user_id", 0) or 0))
        raise TypeError(f"Unsupported dialog search started payload: {type(value)!r}")


@dataclass(frozen=True)
class ExportDialogSearchScanningPayload:
    dialog_count: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "dialog_count": self.dialog_count,
        }

    @classmethod
    def coerce(cls, value: Any) -> "ExportDialogSearchScanningPayload":
        if isinstance(value, cls):
            return value
        if isinstance(value, Mapping):
            return cls(dialog_count=int(value.get("dialog_count", 0) or 0))
        raise TypeError(f"Unsupported dialog search scanning payload: {type(value)!r}")


@dataclass(frozen=True)
class ExportDialogScanStartedPayload:
    index: int
    total: int
    dialog_title: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "total": self.total,
            "dialog_title": self.dialog_title,
        }

    @classmethod
    def coerce(cls, value: Any) -> "ExportDialogScanStartedPayload":
        if isinstance(value, cls):
            return value
        if isinstance(value, Mapping):
            return cls(
                index=int(value.get("index", 0) or 0),
                total=int(value.get("total", 0) or 0),
                dialog_title=str(value.get("dialog_title") or ""),
            )
        raise TypeError(f"Unsupported dialog scan started payload: {type(value)!r}")


@dataclass(frozen=True)
class ExportGlobalExportFinishedPayload:
    total_processed: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "total_processed": self.total_processed,
        }

    @classmethod
    def coerce(cls, value: Any) -> "ExportGlobalExportFinishedPayload":
        if isinstance(value, cls):
            return value
        if isinstance(value, Mapping):
            return cls(total_processed=int(value.get("total_processed", 0) or 0))
        raise TypeError(f"Unsupported global export finished payload: {type(value)!r}")


@dataclass(frozen=True)
class ExportTrackedUpdateStartedPayload:
    target_count: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "target_count": self.target_count,
        }

    @classmethod
    def coerce(cls, value: Any) -> "ExportTrackedUpdateStartedPayload":
        if isinstance(value, cls):
            return value
        if isinstance(value, Mapping):
            return cls(target_count=int(value.get("target_count", 0) or 0))
        raise TypeError(f"Unsupported tracked update started payload: {type(value)!r}")
