from dataclasses import dataclass
from typing import Any, Optional

from .scan_ranges import ScanRangeResult, resolve_tail_progress_checkpoint


@dataclass(frozen=True)
class ScanCheckpointOutcome:
    completed_heads: list[int]
    completed_tails: list[int]
    tail_progress: Optional[int]
    mark_history_complete: bool


def summarize_scan_checkpoint_outcome(
    *,
    results: list[Any],
    tail_range_count: int,
    is_complete: bool,
    stop_requested: bool,
) -> ScanCheckpointOutcome:
    scan_results = [ScanRangeResult.coerce(result) for result in results]
    completed_heads = [
        result.upper for result in scan_results if result.head_scan_complete
    ]
    tail_results = [result for result in scan_results if result.role == "TAIL"]
    completed_tails = [
        result.lower for result in tail_results if result.tail_scan_complete
    ]
    tail_progress = resolve_tail_progress_checkpoint(tail_results)

    if stop_requested or is_complete or not tail_results:
        return ScanCheckpointOutcome(
            completed_heads=completed_heads,
            completed_tails=completed_tails,
            tail_progress=tail_progress,
            mark_history_complete=False,
        )

    if tail_range_count > 1:
        return ScanCheckpointOutcome(
            completed_heads=completed_heads,
            completed_tails=completed_tails,
            tail_progress=tail_progress,
            mark_history_complete=len(completed_tails) == tail_range_count,
        )

    tails = [result.tail_id for result in tail_results if result.tail_id is not None]
    min_tail = None
    if completed_tails:
        min_tail = min(completed_tails)
    elif tails:
        min_tail = min(tails)

    return ScanCheckpointOutcome(
        completed_heads=completed_heads,
        completed_tails=completed_tails,
        tail_progress=tail_progress,
        mark_history_complete=min_tail is not None and min_tail <= 10,
    )
