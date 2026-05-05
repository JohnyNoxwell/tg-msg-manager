from typing import Any, List, Optional

from ..sync.execution_plan import (
    build_sync_execution_plan,
    should_finalize_terminal_history_without_ranges,
)
from ..sync.scan_ranges import (
    ScanRange,
    build_scan_ranges as build_scan_ranges_impl,
    resolve_tail_progress_checkpoint as resolve_tail_progress_checkpoint_impl,
)


class SyncPlanner:
    def build_scan_ranges(
        self,
        *,
        current_max: int,
        head_id: int,
        tail_id: int,
        is_complete: bool,
        limit: Optional[int] = None,
        history_workers: int = 4,
        allow_history: bool = True,
    ) -> List[ScanRange]:
        return build_scan_ranges_impl(
            current_max=current_max,
            head_id=head_id,
            tail_id=tail_id,
            is_complete=is_complete,
            limit=limit,
            history_workers=history_workers,
            allow_history=allow_history,
        )

    @staticmethod
    def resolve_tail_progress_checkpoint(tail_results: List[Any]) -> Optional[int]:
        return resolve_tail_progress_checkpoint_impl(tail_results)

    @staticmethod
    def build_execution_plan(
        *,
        current_max: int,
        head_id: int,
        tail_id: int,
        is_complete: bool,
        limit: Optional[int],
        allow_history: bool,
    ) -> Any:
        return build_sync_execution_plan(
            current_max=current_max,
            head_id=head_id,
            tail_id=tail_id,
            is_complete=is_complete,
            limit=limit,
            allow_history=allow_history,
        )

    @staticmethod
    def should_finalize_without_ranges(
        *,
        resume_history: bool,
        is_complete: bool,
        tail_id: int,
        current_max: int,
        head_id: int,
        stop_requested: bool,
    ) -> bool:
        return should_finalize_terminal_history_without_ranges(
            resume_history=resume_history,
            is_complete=is_complete,
            tail_id=tail_id,
            current_max=current_max,
            head_id=head_id,
            stop_requested=stop_requested,
        )
