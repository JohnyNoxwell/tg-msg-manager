from typing import Iterable, Optional

from ...infrastructure.storage.contracts.target_names_storage import TargetNamesStorage
from ...infrastructure.storage.records import (
    TargetNameSnapshotRecord,
    TargetNameTargetRecord,
)
from .models import (
    TARGET_NAME_FIELDS,
    TargetNameCurrent,
    TargetNameHistoryItem,
    TargetNamesResult,
)


def query_target_names(
    storage: TargetNamesStorage, target: str, *, field: str = "all"
) -> TargetNamesResult:
    fields = _selected_fields(field)
    resolution = storage.resolve_target_name_target(target)
    if resolution.status != "found":
        return TargetNamesResult(
            status=resolution.status,
            target=resolution.target,
            matches=resolution.matches,
        )

    resolved = resolution.matches[0]
    snapshots = storage.get_target_name_snapshots(resolved)
    return TargetNamesResult(
        status="found",
        target=resolution.target,
        target_type=resolved.target_type,
        current=_current_from_target(resolved),
        history=tuple(_derive_history(snapshots, fields)),
        matches=resolution.matches,
    )


def _selected_fields(field: str) -> tuple[str, ...]:
    if field == "all":
        return TARGET_NAME_FIELDS
    if field not in TARGET_NAME_FIELDS:
        raise ValueError(f"Unsupported target name field: {field}")
    return (field,)


def _current_from_target(target: TargetNameTargetRecord) -> TargetNameCurrent:
    return TargetNameCurrent(
        username=_clean_text(target.current_username),
        display_name=_clean_text(target.current_display_name),
        title=_clean_text(target.current_title),
        first_seen=target.first_seen,
        last_seen=target.last_seen,
    )


def _derive_history(
    snapshots: Iterable[TargetNameSnapshotRecord], fields: tuple[str, ...]
) -> list[TargetNameHistoryItem]:
    previous: dict[str, Optional[str]] = {}
    history: list[TargetNameHistoryItem] = []
    ordered = sorted(snapshots, key=lambda item: (item.observed_at, item.target_id))

    for snapshot in ordered:
        for field in fields:
            value = _clean_text(getattr(snapshot, field))
            if value is None:
                continue
            if field in previous and previous[field] == value:
                continue
            old_value = previous.get(field)
            history.append(
                TargetNameHistoryItem(
                    observed_at=snapshot.observed_at,
                    field=field,
                    old_value=old_value,
                    new_value=value,
                )
            )
            previous[field] = value

    return sorted(
        history,
        key=lambda item: (item.observed_at, TARGET_NAME_FIELDS.index(item.field)),
    )


def _clean_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
