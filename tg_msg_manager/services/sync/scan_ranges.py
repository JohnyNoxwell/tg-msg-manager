from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class ScanRange:
    upper: int
    lower: int
    role: str


@dataclass(frozen=True)
class ScanRangeResult:
    processed: int
    tail_id: Optional[int]
    head_id: int
    head_scan_complete: bool
    tail_scan_complete: bool
    upper: int
    lower: int
    role: str

    @classmethod
    def coerce(cls, value: Any) -> "ScanRangeResult":
        if isinstance(value, cls):
            return value
        if isinstance(value, dict):
            return cls(
                processed=int(value.get("processed", 0)),
                tail_id=value.get("tail_id", value.get("tail")),
                head_id=int(value.get("head_id", value.get("head", 0))),
                head_scan_complete=bool(value.get("head_scan_complete", False)),
                tail_scan_complete=bool(value.get("tail_scan_complete", False)),
                upper=int(value["upper"]),
                lower=int(value["lower"]),
                role=str(value.get("role", "TAIL")),
            )
        raise TypeError(f"Unsupported scan range result payload: {type(value)!r}")


def _partition_descending_ranges(
    upper_id: int,
    lower_id: int,
    parts: int,
    role: str,
) -> list[ScanRange]:
    if upper_id < lower_id or upper_id <= 0 or parts <= 0:
        return []

    total = upper_id - lower_id + 1
    step = max(1, (total + parts - 1) // parts)
    ranges: list[ScanRange] = []
    current_upper = upper_id

    while current_upper >= lower_id:
        current_lower = max(lower_id, current_upper - step + 1)
        ranges.append(ScanRange(upper=current_upper, lower=current_lower, role=role))
        current_upper = current_lower - 1

    return ranges


def build_scan_ranges(
    *,
    current_max: int,
    head_id: int,
    tail_id: int,
    is_complete: bool,
    limit: Optional[int] = None,
    history_workers: int = 4,
    allow_history: bool = True,
) -> list[ScanRange]:
    if current_max <= 0:
        return []

    first_full_sync = head_id <= 0 and tail_id <= 0 and not is_complete
    if limit is not None:
        if current_max > head_id and head_id > 0:
            return [ScanRange(upper=current_max, lower=head_id + 1, role="HEAD")]
        history_upper = (
            current_max
            if first_full_sync
            else (tail_id - 1 if tail_id > 0 else head_id - 1)
        )
        if allow_history and history_upper >= 1 and not is_complete:
            return [ScanRange(upper=history_upper, lower=1, role="TAIL")]
        return []

    if first_full_sync and allow_history:
        return _partition_descending_ranges(current_max, 1, history_workers, "TAIL")

    ranges: list[ScanRange] = []
    if current_max > head_id and head_id > 0:
        ranges.append(ScanRange(upper=current_max, lower=head_id + 1, role="HEAD"))

    if allow_history and not is_complete:
        history_upper = tail_id - 1 if tail_id > 0 else head_id - 1
        if history_upper >= 1:
            ranges.extend(
                _partition_descending_ranges(history_upper, 1, history_workers, "TAIL")
            )

    if not ranges and current_max > head_id:
        ranges.append(
            ScanRange(upper=current_max, lower=max(1, head_id + 1), role="HEAD")
        )

    return ranges


def resolve_tail_progress_checkpoint(tail_results: list[Any]) -> Optional[int]:
    if not tail_results:
        return None

    ordered = sorted(
        (ScanRangeResult.coerce(result) for result in tail_results),
        key=lambda item: item.upper,
        reverse=True,
    )
    checkpoint = None
    for result in ordered:
        if result.tail_scan_complete:
            checkpoint = result.lower
            continue

        tail_cursor = result.tail_id
        if tail_cursor is not None:
            checkpoint = tail_cursor
        break

    return checkpoint
