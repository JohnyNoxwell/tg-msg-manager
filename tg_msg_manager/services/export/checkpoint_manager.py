from typing import Any, List

from ...core.service_events import ExportEvents
from ...core.telemetry import telemetry
from ..sync.checkpoints import summarize_scan_checkpoint_outcome


class SyncCheckpointManager:
    def __init__(self, *, storage: Any, emit_event):
        self.storage = storage
        self.emit_event = emit_event

    def apply_scan_results(
        self,
        *,
        chat_id: int,
        uid: int,
        results: List[Any],
        tail_range_count: int,
        is_complete: bool,
    ) -> None:
        outcome = summarize_scan_checkpoint_outcome(
            results=results,
            tail_range_count=tail_range_count,
            is_complete=is_complete,
            stop_requested=self.storage.should_stop(),
        )
        if outcome.completed_heads:
            self.storage.update_last_msg_id(chat_id, uid, max(outcome.completed_heads))
            telemetry.track_counter(
                "sync.head_ranges_completed", len(outcome.completed_heads)
            )

        if outcome.tail_progress is not None:
            self.storage.update_sync_tail(
                chat_id, uid, outcome.tail_progress, is_complete=False
            )
        if outcome.completed_tails:
            telemetry.track_counter(
                "sync.tail_ranges_completed", len(outcome.completed_tails)
            )

        if not outcome.mark_history_complete:
            return

        self.storage.update_sync_tail(chat_id, uid, 0, is_complete=True)
        self.emit_event(ExportEvents.HISTORY_FULLY_SYNCED)
