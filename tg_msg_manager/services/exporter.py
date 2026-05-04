import asyncio
import logging
from dataclasses import dataclass
from time import perf_counter
from typing import Optional, Any, Set, List, Awaitable, Callable
from ..core.models.service_payloads import (
    ExportDialogScanStartedPayload,
    ExportDialogSearchScanningPayload,
    ExportDialogSearchStartedPayload,
    ExportGlobalExportFinishedPayload,
    ExportSyncFinishedPayload,
    ExportSyncProgressPayload,
    ExportSyncStartedPayload,
    ExportSyncSummaryPayload,
    ExportTargetedDialogSearchStartedPayload,
)
from ..core.models.sync_report import TrackedSyncUserStat
from ..core.models.sync_report import TrackedSyncRunReport
from ..core.telegram.interface import TelegramClientInterface
from ..core.service_events import ExportEvents, ServiceEventSink, emit_service_event
from ..infrastructure.storage.interface import ExportStorage
from ..infrastructure.storage.records import (
    PrimaryTarget,
    SyncStatus,
)
from ..core.context import set_chat_id
from ..core.telemetry import telemetry
from .context_engine import DeepModeEngine
from .sync.scan_ranges import (
    ScanRange as _ScanRange,
    ScanRangeResult as _ScanRangeResult,
    build_scan_ranges as _build_scan_ranges_impl,
    resolve_tail_progress_checkpoint as _resolve_tail_progress_checkpoint_impl,
)
from .sync.checkpoints import summarize_scan_checkpoint_outcome
from .sync.execution_plan import (
    build_sync_execution_plan,
    should_finalize_terminal_history_without_ranges,
)
from .sync.finalization import build_sync_chat_final_state
from .sync.dialog_targets import (
    filter_group_dialog_entities,
    resolve_targeted_dialog_entities,
)
from .sync.progress import SyncProgressReporter, SyncProgressStats
from .sync.range_scanner import SyncRangeScanner
from .sync.targets import (
    resolve_active_sync_mode,
    resolve_status_kind,
    resolve_sync_target_identity,
)
from .retry_worker import enqueue_sync_target_retry_task
from .sync.tracked_runner import TrackedSyncRunner
from ..utils.ui import UI

logger = logging.getLogger(__name__)


@dataclass
class _SyncTargetContext:
    chat_id: int
    chat_title: str
    uid: int
    status: SyncStatus
    api_from_user: Optional[Any]
    local_sender_filter_id: Optional[int]
    active_deep: bool
    active_depth: int
    head_id: int
    tail_id: int
    is_complete: bool
    header_payload: ExportSyncStartedPayload


class ExportService:
    """
    Orchestrates the export and synchronization of Telegram messages.
    Links the API abstraction layer with the Storage layer.
    """

    def __init__(
        self,
        client: TelegramClientInterface,
        storage: ExportStorage,
        event_sink: ServiceEventSink = None,
    ):
        self.client = client
        self.storage = storage
        self.context_engine = DeepModeEngine(client, storage)
        self.event_sink = event_sink
        self.range_scanner = SyncRangeScanner(
            client=client,
            storage=storage,
            context_engine=self.context_engine,
        )

    def _emit_event(self, event_name: str, **payload: Any) -> None:
        emit_service_event(self.event_sink, event_name, **payload)

    # UI.format_name handles entity formatting

    def request_stop(self):
        """Sets the shutdown event to signal workers to stop."""
        self.storage.request_stop()

    async def try_fetch_missing_reply(
        self, chat_id: int, missing_reply_to_id: int
    ) -> None:
        """
        Placeholder hook for future targeted backfill of missing reply parents.

        The SQLite hardening stage only records missing reply references; it does
        not auto-fetch them during normal export/update paths.
        """
        del chat_id, missing_reply_to_id
        return None

    def _build_scan_ranges(
        self,
        current_max: int,
        head_id: int,
        tail_id: int,
        is_complete: bool,
        limit: Optional[int] = None,
        history_workers: int = 4,
        allow_history: bool = True,
    ) -> List[_ScanRange]:
        return _build_scan_ranges_impl(
            current_max=current_max,
            head_id=head_id,
            tail_id=tail_id,
            is_complete=is_complete,
            limit=limit,
            history_workers=history_workers,
            allow_history=allow_history,
        )

    @staticmethod
    def _resolve_tail_progress_checkpoint(
        tail_results: List[Any],
    ) -> Optional[int]:
        """
        Resolve the lowest contiguous history point we can safely checkpoint.

        Tail workers scan disjoint descending ranges. After interruption we must not
        claim progress for lower ranges if an earlier (higher) range was never
        covered, otherwise resume could skip history gaps. We therefore only advance
        the tail checkpoint across the highest contiguous prefix of completed or
        partially processed ranges.
        """
        return _resolve_tail_progress_checkpoint_impl(tail_results)

    def _build_sync_header_payload(
        self,
        *,
        chat_title: str,
        user_label: str,
        active_deep: bool,
        active_depth: int,
        status_kind: Optional[str],
    ) -> ExportSyncStartedPayload:
        return ExportSyncStartedPayload(
            chat_title=chat_title,
            user_label=user_label,
            deep_mode=active_deep,
            depth=active_depth if active_deep else 0,
            status_kind=status_kind,
        )

    def _emit_sync_progress_payload(self, payload: ExportSyncProgressPayload) -> None:
        self._emit_event(
            ExportEvents.SYNC_PROGRESS,
            **payload.as_dict(),
        )

    async def _prepare_sync_target(
        self,
        entity: Any,
        *,
        from_user_id: Optional[int],
        deep_mode: bool,
        recursive_depth: int,
        force_resync: bool,
        resume_history: bool,
        resolve_user_entity: bool,
    ) -> _SyncTargetContext:
        chat_id = getattr(entity, "id", 0)
        chat_title = UI.format_name(entity)
        set_chat_id(chat_id)
        self.storage.upsert_chat(
            chat_id, chat_title, chat_type=getattr(entity, "_", None)
        )

        uid = from_user_id or chat_id
        status = SyncStatus.coerce(self.storage.get_sync_status(chat_id, uid))
        resolved_target = await resolve_sync_target_identity(
            entity=entity,
            from_user_id=from_user_id,
            resolve_user_entity=resolve_user_entity,
            status=status,
            client=self.client,
            storage=self.storage,
        )

        saved_deep = status.deep_mode
        saved_depth = status.recursive_depth
        active_deep, active_depth = resolve_active_sync_mode(
            deep_mode=deep_mode,
            saved_deep=saved_deep,
            recursive_depth=recursive_depth,
            saved_depth=saved_depth,
        )

        head_id = 0 if force_resync else status.last_msg_id
        tail_id = 0 if force_resync else status.tail_msg_id
        is_complete = False if force_resync else status.is_complete

        self.storage.register_target(
            resolved_target.uid,
            resolved_target.target_name,
            chat_id,
            deep_mode=active_deep,
            recursive_depth=active_depth,
        )

        if active_deep:
            self.context_engine.reset()

        status_kind = resolve_status_kind(
            resume_history=resume_history,
            tail_id=tail_id,
            is_complete=bool(is_complete),
            head_id=head_id,
        )

        return _SyncTargetContext(
            chat_id=chat_id,
            chat_title=chat_title,
            uid=resolved_target.uid,
            status=status,
            api_from_user=resolved_target.api_from_user,
            local_sender_filter_id=resolved_target.local_sender_filter_id,
            active_deep=active_deep,
            active_depth=active_depth,
            head_id=head_id,
            tail_id=tail_id,
            is_complete=is_complete,
            header_payload=self._build_sync_header_payload(
                chat_title=chat_title,
                user_label=resolved_target.user_label,
                active_deep=active_deep,
                active_depth=active_depth,
                status_kind=status_kind,
            ),
        )

    def _apply_sync_scan_results(
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
        self._emit_event(ExportEvents.HISTORY_FULLY_SYNCED)

    async def _scan_range(
        self,
        *,
        entity: Any,
        scan_range: _ScanRange,
        chat_id: int,
        uid: int,
        head_id: int,
        tail_id: int,
        api_from_user: Optional[Any],
        from_user_id: Optional[int],
        local_sender_filter_id: Optional[int],
        force_resync: bool,
        active_deep: bool,
        active_depth: int,
        context_window: int,
        max_cluster: int,
        batch_size: int,
        context_batch_size: int,
        single_worker_limit: Optional[int],
        can_checkpoint_tail: bool,
        prefetched_messages: Optional[List[Any]],
        prefetched_head_complete: bool,
        progress_stats: SyncProgressStats,
        draw_status,
    ) -> _ScanRangeResult:
        return await self.range_scanner.scan_range(
            entity=entity,
            scan_range=scan_range,
            chat_id=chat_id,
            uid=uid,
            head_id=head_id,
            tail_id=tail_id,
            api_from_user=api_from_user,
            from_user_id=from_user_id,
            local_sender_filter_id=local_sender_filter_id,
            force_resync=force_resync,
            active_deep=active_deep,
            active_depth=active_depth,
            context_window=context_window,
            max_cluster=max_cluster,
            batch_size=batch_size,
            context_batch_size=context_batch_size,
            single_worker_limit=single_worker_limit,
            can_checkpoint_tail=can_checkpoint_tail,
            prefetched_messages=prefetched_messages,
            prefetched_head_complete=prefetched_head_complete,
            progress_stats=progress_stats,
            draw_status=draw_status,
        )

    async def _prefetch_chat_head_messages(
        self,
        entity: Any,
        current_max: int,
        lower_bound: int,
    ) -> tuple[List[Any], bool]:
        """
        Fetch a shared HEAD slice once for a chat and reuse it across many targets.
        Returns the collected messages in descending order and whether the slice
        fully covered the requested lower bound.
        """
        if current_max < lower_bound or current_max <= 0:
            return [], False

        collected: List[Any] = []
        complete = False
        async for msg_data in self.client.iter_messages(
            entity,
            offset_id=current_max + 1,
        ):
            if self.storage.should_stop():
                break
            if msg_data.message_id < lower_bound:
                complete = True
                break
            collected.append(msg_data)
        else:
            complete = True

        telemetry.track_counter("sync.shared_head_prefetch.calls", 1)
        telemetry.track_counter("sync.shared_head_prefetch.messages", len(collected))
        if complete:
            telemetry.track_counter("sync.shared_head_prefetch.complete", 1)
        return collected, complete

    async def _run_sync_ranges(
        self,
        *,
        entity: Any,
        execution_plan: Any,
        chat_id: int,
        uid: int,
        head_id: int,
        tail_id: int,
        api_from_user: Optional[Any],
        from_user_id: Optional[int],
        local_sender_filter_id: Optional[int],
        force_resync: bool,
        active_deep: bool,
        active_depth: int,
        context_window: int,
        max_cluster: int,
        prefetched_messages: Optional[List[Any]],
        prefetched_head_complete: bool,
        progress_stats: SyncProgressStats,
        draw_status: Callable[[str], Awaitable[None]],
    ) -> tuple[int, list[_ScanRangeResult]]:
        results = await asyncio.gather(
            *[
                self._scan_range(
                    entity=entity,
                    scan_range=scan_range,
                    chat_id=chat_id,
                    uid=uid,
                    head_id=head_id,
                    tail_id=tail_id,
                    api_from_user=api_from_user,
                    from_user_id=from_user_id,
                    local_sender_filter_id=local_sender_filter_id,
                    force_resync=force_resync,
                    active_deep=active_deep,
                    active_depth=active_depth,
                    context_window=context_window,
                    max_cluster=max_cluster,
                    batch_size=execution_plan.batch_size,
                    context_batch_size=execution_plan.context_batch_size,
                    single_worker_limit=execution_plan.single_worker_limit,
                    can_checkpoint_tail=execution_plan.can_checkpoint_tail,
                    prefetched_messages=prefetched_messages,
                    prefetched_head_complete=prefetched_head_complete,
                    progress_stats=progress_stats,
                    draw_status=draw_status,
                )
                for scan_range in execution_plan.ranges
            ]
        )
        total_processed = sum(result.processed for result in results)
        return total_processed, results

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
        finished_payload = ExportSyncFinishedPayload(db_count=final_state.db_count)
        self._emit_event(ExportEvents.SYNC_FINISHED, **finished_payload.as_dict())

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
            summary_payload = ExportSyncSummaryPayload(
                title=UI.format_name(entity),
                own_messages=final_state.breakdown.own_messages,
                with_context=final_state.breakdown.with_context,
            )
            self._emit_event(
                ExportEvents.SYNC_SUMMARY,
                **summary_payload.as_dict(),
            )

        return total_processed

    def _resolve_target_report_name(
        self,
        *,
        from_user_id: int,
        target_status: SyncStatus,
    ) -> str:
        name = target_status.author_name or f"ID:{from_user_id}"
        if not target_status.author_name or target_status.author_name.startswith("ID:"):
            user_info = self.storage.get_user(from_user_id)
            if user_info:
                first = user_info.get("first_name") or ""
                last = user_info.get("last_name") or ""
                name = f"{first} {last}".strip() or user_info.get("username") or name
        return name

    def _ensure_user_stats_entry(
        self,
        *,
        user_stats: TrackedSyncRunReport,
        from_user_id: int,
        target_status: SyncStatus,
    ) -> None:
        if from_user_id in user_stats:
            return

        user_stats[from_user_id] = TrackedSyncUserStat(
            name=self._resolve_target_report_name(
                from_user_id=from_user_id,
                target_status=target_status,
            ),
        )

    def _enqueue_tracked_sync_retry_task(self, plan: Any, exc: Exception) -> None:
        enqueue_sync_target_retry_task(
            self.storage,
            chat_id=plan.chat_id,
            user_id=plan.from_user_id,
            error=exc,
        )

    async def sync_chat(
        self,
        entity: Any,
        from_user_id: Optional[int] = None,
        limit: Optional[int] = None,
        deep_mode: bool = False,
        force_resync: bool = False,
        context_window: int = 3,
        max_cluster: int = 20,
        recursive_depth: int = 0,
        resume_history: bool = True,
        current_max_hint: Optional[int] = None,
        prefetched_messages: Optional[List[Any]] = None,
        prefetched_head_complete: bool = False,
        resolve_user_entity: bool = True,
        emit_summary: bool = True,
    ):
        """
        Synchronizes a specific chat with a clean real-time global status counter.
        Now supports Resume and Dual-Sync (New + Historical).
        """
        sync_started = perf_counter()
        sync_ctx = await self._prepare_sync_target(
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
        api_from_user = sync_ctx.api_from_user
        local_sender_filter_id = sync_ctx.local_sender_filter_id
        active_deep = sync_ctx.active_deep
        active_depth = sync_ctx.active_depth
        head_id = sync_ctx.head_id
        tail_id = sync_ctx.tail_id
        is_complete = sync_ctx.is_complete
        self._emit_event(
            ExportEvents.SYNC_CHAT_STARTED, **sync_ctx.header_payload.as_dict()
        )

        # 5. Determine Scan Boundaries
        # Get the latest message to determine current max
        current_max = current_max_hint
        if current_max is None:
            latest_msg = await self.client.get_messages(entity, limit=1)
            current_max = latest_msg[0].message_id if latest_msg else 1000000

        execution_plan = build_sync_execution_plan(
            current_max=current_max,
            head_id=head_id,
            tail_id=tail_id,
            is_complete=bool(is_complete),
            limit=limit,
            allow_history=resume_history or force_resync,
        )

        if not execution_plan.ranges:
            if should_finalize_terminal_history_without_ranges(
                resume_history=resume_history,
                is_complete=bool(is_complete),
                tail_id=tail_id,
                current_max=current_max,
                head_id=head_id,
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
            emit_progress=self._emit_sync_progress_payload,
        )
        progress_reporter.start()

        try:
            total_processed, results = await self._run_sync_ranges(
                entity=entity,
                execution_plan=execution_plan,
                chat_id=chat_id,
                uid=uid,
                head_id=head_id,
                tail_id=tail_id,
                api_from_user=api_from_user,
                from_user_id=from_user_id,
                local_sender_filter_id=local_sender_filter_id,
                force_resync=force_resync,
                active_deep=active_deep,
                active_depth=active_depth,
                context_window=context_window,
                max_cluster=max_cluster,
                prefetched_messages=prefetched_messages,
                prefetched_head_complete=prefetched_head_complete,
                progress_stats=progress_stats,
                draw_status=progress_reporter.draw_status,
            )
            self._apply_sync_scan_results(
                chat_id=chat_id,
                uid=uid,
                results=results,
                tail_range_count=execution_plan.tail_range_count,
                is_complete=bool(is_complete),
            )
        finally:
            await progress_reporter.finalize()

        return await self._finalize_sync_chat(
            entity=entity,
            chat_id=chat_id,
            uid=uid,
            active_deep=active_deep,
            active_depth=active_depth,
            execution_plan=execution_plan,
            progress_stats=progress_stats,
            total_processed=total_processed,
            sync_started=sync_started,
            emit_summary=emit_summary,
        )

    async def sync_all_dialogs_for_user(
        self,
        from_user_id: int,
        target_chat_ids: Optional[Set[Any]] = None,
        limit: Optional[int] = None,
        deep_mode: bool = False,
        force_resync: bool = False,
        context_window: int = 3,
        max_cluster: int = 20,
        recursive_depth: int = 3,
    ):
        """
        Scans specified dialogs (from config or all) for a specific user's messages.
        """
        if target_chat_ids:
            started_at = perf_counter()
            targeted_payload = ExportTargetedDialogSearchStartedPayload(
                from_user_id=from_user_id,
                dialog_count=len(target_chat_ids),
            )
            self._emit_event(
                ExportEvents.TARGETED_DIALOG_SEARCH_STARTED,
                **targeted_payload.as_dict(),
            )
            targets = await resolve_targeted_dialog_entities(
                client=self.client,
                target_chat_ids=target_chat_ids,
            )
        else:
            started_at = perf_counter()
            search_started_payload = ExportDialogSearchStartedPayload(
                from_user_id=from_user_id
            )
            self._emit_event(
                ExportEvents.DIALOG_SEARCH_STARTED,
                **search_started_payload.as_dict(),
            )
            dialogs = await self.client.get_dialogs()
            targets = filter_group_dialog_entities(dialogs)

        scanning_payload = ExportDialogSearchScanningPayload(dialog_count=len(targets))
        self._emit_event(
            ExportEvents.DIALOG_SEARCH_SCANNING, **scanning_payload.as_dict()
        )

        total_processed = 0

        for i, dialog in enumerate(targets):
            try:
                dialog_title = UI.format_name(dialog)
                scan_started_payload = ExportDialogScanStartedPayload(
                    index=i + 1,
                    total=len(targets),
                    dialog_title=dialog_title,
                )
                self._emit_event(
                    ExportEvents.DIALOG_SCAN_STARTED,
                    **scan_started_payload.as_dict(),
                )

                processed = await self.sync_chat(
                    dialog,
                    from_user_id=from_user_id,
                    limit=limit,
                    deep_mode=deep_mode,
                    force_resync=force_resync,
                    context_window=context_window,
                    max_cluster=max_cluster,
                    recursive_depth=recursive_depth,
                    emit_summary=False,
                )
                total_processed += processed
                # Small pause to be friendly
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(
                    f"Error scanning dialog {getattr(dialog, 'name', 'Unknown')}: {e}"
                )

        global_finished_payload = ExportGlobalExportFinishedPayload(
            total_processed=total_processed
        )
        self._emit_event(
            ExportEvents.GLOBAL_EXPORT_FINISHED,
            **global_finished_payload.as_dict(),
        )
        telemetry.track_counter("sync.dialogs.scanned", len(targets))
        telemetry.track_duration(
            "sync.dialogs_for_user.total", perf_counter() - started_at
        )
        return total_processed

    async def sync_all_outdated(
        self, threshold_seconds: int = 86400
    ) -> TrackedSyncRunReport:
        """Runs synchronization for all chats that haven't been updated in a while or are incomplete."""
        outdated = self.storage.get_outdated_chats(threshold_seconds=threshold_seconds)
        return await self._sync_target_items(outdated)

    async def sync_all_tracked(self) -> TrackedSyncRunReport:
        """Runs synchronization for every tracked primary target."""
        targets = self.storage.get_primary_targets()
        items = [
            (target.chat_id, target.user_id)
            for target in (PrimaryTarget.coerce(item) for item in targets)
        ]
        return await self._sync_target_items(items)

    async def _sync_target_items(self, items: list) -> TrackedSyncRunReport:
        """Synchronize a list of target tuples in `(chat_id, user_id)` form."""
        runner = TrackedSyncRunner(
            client=self.client,
            storage=self.storage,
            emit_event=self._emit_event,
            sync_chat=self.sync_chat,
            ensure_user_stats_entry=self._ensure_user_stats_entry,
            prefetch_chat_head_messages=self._prefetch_chat_head_messages,
            enqueue_retry_task=self._enqueue_tracked_sync_retry_task,
        )
        return await runner.run(items)
