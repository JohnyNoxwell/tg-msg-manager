import logging
from time import perf_counter
from typing import Any, Optional

from ...core.models.service_payloads import (
    ExportSyncFinishedPayload,
    ExportSyncSummaryPayload,
)
from ...core.service_events import ExportEvents
from ...core.telemetry import telemetry
from ...utils.ui import UI
from ..sync.finalization import build_sync_chat_final_state
from ..sync.progress import SyncProgressReporter, SyncProgressStats

logger = logging.getLogger(__name__)


class SyncChatCoordinator:
    def __init__(
        self,
        *,
        client: Any,
        storage: Any,
        planner: Any,
        target_resolver: Any,
        fetch_orchestrator: Any,
        checkpoint_manager: Any,
        emit_event,
        emit_sync_progress,
    ):
        self.client = client
        self.storage = storage
        self.planner = planner
        self.target_resolver = target_resolver
        self.fetch_orchestrator = fetch_orchestrator
        self.checkpoint_manager = checkpoint_manager
        self.emit_event = emit_event
        self.emit_sync_progress = emit_sync_progress

    async def sync_chat(
        self,
        entity: Any,
        *,
        from_user_id: Optional[int] = None,
        limit: Optional[int] = None,
        deep_mode: bool = False,
        force_resync: bool = False,
        context_window: int = 3,
        max_cluster: int = 20,
        recursive_depth: int = 0,
        resume_history: bool = True,
        current_max_hint: Optional[int] = None,
        prefetched_messages=None,
        prefetched_head_complete: bool = False,
        resolve_user_entity: bool = True,
        emit_summary: bool = True,
    ) -> int:
        sync_started = perf_counter()
        sync_ctx = await self.target_resolver.prepare_sync_target(
            entity,
            from_user_id=from_user_id,
            deep_mode=deep_mode,
            recursive_depth=recursive_depth,
            force_resync=force_resync,
            resume_history=resume_history,
            resolve_user_entity=resolve_user_entity,
        )
        chat_id = sync_ctx.chat_id
        uid = sync_ctx.uid
        self.emit_event(
            ExportEvents.SYNC_CHAT_STARTED,
            **sync_ctx.header_payload.as_dict(),
        )

        current_max = current_max_hint
        if current_max is None:
            latest_msg = await self.client.get_messages(entity, limit=1)
            current_max = latest_msg[0].message_id if latest_msg else 1000000

        execution_plan = self.planner.build_execution_plan(
            current_max=current_max,
            head_id=sync_ctx.head_id,
            tail_id=sync_ctx.tail_id,
            is_complete=bool(sync_ctx.is_complete),
            limit=limit,
            allow_history=resume_history or force_resync,
        )

        if not execution_plan.ranges:
            if self.planner.should_finalize_without_ranges(
                resume_history=resume_history,
                is_complete=bool(sync_ctx.is_complete),
                tail_id=sync_ctx.tail_id,
                current_max=current_max,
                head_id=sync_ctx.head_id,
                stop_requested=self.storage.should_stop(),
            ):
                self.storage.update_sync_tail(chat_id, uid, 0, is_complete=True)
                self.storage.update_last_sync_at(chat_id, uid)
            return 0

        initial_db_total = self.storage.get_message_count(chat_id, target_id=uid)
        progress_stats = SyncProgressStats()
        progress_reporter = SyncProgressReporter(
            initial_db_total=initial_db_total,
            progress_stats=progress_stats,
            emit_progress=self.emit_sync_progress,
        )
        progress_reporter.start()

        try:
            total_processed, results = await self.fetch_orchestrator.run_sync_ranges(
                execution_plan=execution_plan,
                draw_status=progress_reporter.draw_status,
                scan_range_factory=self.fetch_orchestrator.scan_range,
                scan_kwargs={
                    "entity": entity,
                    "chat_id": chat_id,
                    "uid": uid,
                    "head_id": sync_ctx.head_id,
                    "tail_id": sync_ctx.tail_id,
                    "api_from_user": sync_ctx.api_from_user,
                    "from_user_id": from_user_id,
                    "local_sender_filter_id": sync_ctx.local_sender_filter_id,
                    "force_resync": force_resync,
                    "active_deep": sync_ctx.active_deep,
                    "active_depth": sync_ctx.active_depth,
                    "context_window": context_window,
                    "max_cluster": max_cluster,
                    "batch_size": execution_plan.batch_size,
                    "context_batch_size": execution_plan.context_batch_size,
                    "single_worker_limit": execution_plan.single_worker_limit,
                    "can_checkpoint_tail": execution_plan.can_checkpoint_tail,
                    "prefetched_messages": prefetched_messages,
                    "prefetched_head_complete": prefetched_head_complete,
                    "progress_stats": progress_stats,
                },
            )
            self.checkpoint_manager.apply_scan_results(
                chat_id=chat_id,
                uid=uid,
                results=results,
                tail_range_count=execution_plan.tail_range_count,
                is_complete=bool(sync_ctx.is_complete),
            )
        finally:
            await progress_reporter.finalize()

        return await self._finalize_sync_chat(
            entity=entity,
            chat_id=chat_id,
            uid=uid,
            active_deep=sync_ctx.active_deep,
            active_depth=sync_ctx.active_depth,
            execution_plan=execution_plan,
            progress_stats=progress_stats,
            total_processed=total_processed,
            sync_started=sync_started,
            emit_summary=emit_summary,
        )

    async def _finalize_sync_chat(
        self,
        *,
        entity: Any,
        chat_id: int,
        uid: int,
        active_deep: bool,
        active_depth: int,
        execution_plan: Any,
        progress_stats: SyncProgressStats,
        total_processed: int,
        sync_started: float,
        emit_summary: bool,
    ) -> int:
        flush_started = perf_counter()
        await self.storage.flush()
        telemetry.track_duration(
            "sync.storage_flush.total", perf_counter() - flush_started
        )

        final_state = build_sync_chat_final_state(
            storage=self.storage,
            chat_id=chat_id,
            uid=uid,
        )
        self.emit_event(
            ExportEvents.SYNC_FINISHED,
            **ExportSyncFinishedPayload(db_count=final_state.db_count).as_dict(),
        )

        if final_state.should_mark_synced:
            self.storage.update_last_sync_at(chat_id, uid)

        elapsed_seconds = perf_counter() - sync_started
        telemetry.track_duration("sync.chat.total", elapsed_seconds)
        telemetry.track_counter("sync.chat.processed_messages", total_processed)
        telemetry.track_counter("sync.chat.linked_messages", progress_stats.linked)
        telemetry.track_counter("sync.chat.skipped_messages", progress_stats.skipped)
        logger.info(
            "Chat sync complete",
            extra={
                "event": "sync_chat_complete",
                "metrics": {
                    "chat_id": chat_id,
                    "target_id": uid,
                    "processed": total_processed,
                    "linked": progress_stats.linked,
                    "skipped": progress_stats.skipped,
                    "mode": "deep" if active_deep else "flat",
                    "depth": active_depth if active_deep else 0,
                    "elapsed_seconds": round(elapsed_seconds, 3),
                    "ranges": len(execution_plan.ranges),
                },
            },
        )
        if emit_summary:
            self.emit_event(
                ExportEvents.SYNC_SUMMARY,
                **ExportSyncSummaryPayload(
                    title=UI.format_name(entity),
                    own_messages=final_state.breakdown.own_messages,
                    with_context=final_state.breakdown.with_context,
                ).as_dict(),
            )
        return total_processed
