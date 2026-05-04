from dataclasses import dataclass
from typing import Optional

from .scan_ranges import ScanRange, build_scan_ranges


@dataclass(frozen=True)
class SyncExecutionPlan:
    current_max: int
    batch_size: int
    context_batch_size: int
    single_worker_limit: Optional[int]
    ranges: list[ScanRange]
    tail_range_count: int
    can_checkpoint_tail: bool


def build_sync_execution_plan(
    *,
    current_max: int,
    head_id: int,
    tail_id: int,
    is_complete: bool,
    limit: Optional[int],
    allow_history: bool,
    batch_size: int = 200,
    context_batch_size: int = 50,
) -> SyncExecutionPlan:
    ranges = build_scan_ranges(
        current_max=current_max,
        head_id=head_id,
        tail_id=tail_id,
        is_complete=is_complete,
        limit=limit,
        allow_history=allow_history,
    )
    tail_range_count = sum(1 for item in ranges if item.role == "TAIL")
    return SyncExecutionPlan(
        current_max=current_max,
        batch_size=batch_size,
        context_batch_size=context_batch_size,
        single_worker_limit=limit,
        ranges=ranges,
        tail_range_count=tail_range_count,
        can_checkpoint_tail=tail_range_count <= 1,
    )


def should_finalize_terminal_history_without_ranges(
    *,
    resume_history: bool,
    is_complete: bool,
    tail_id: int,
    current_max: int,
    head_id: int,
    stop_requested: bool,
) -> bool:
    return (
        resume_history
        and not is_complete
        and tail_id <= 1
        and current_max <= head_id
        and not stop_requested
    )
