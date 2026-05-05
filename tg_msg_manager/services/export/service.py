from typing import Any, List, Optional, Set

from ...core.telegram.interface import TelegramClientInterface
from ...core.service_events import ServiceEventSink
from ...infrastructure.storage.contracts.export_storage import ExportStorage
from ...infrastructure.storage.records import PrimaryTarget, SyncStatus
from ..context.engine import DeepModeEngine
from ..retry_worker import enqueue_sync_target_retry_task
from .chat_sync import SyncChatCoordinator
from .checkpoint_manager import SyncCheckpointManager
from .dialog_sync import DialogSyncCoordinator
from .event_emitter import ExportEventEmitter
from .fetch_orchestrator import SyncFetchOrchestrator
from .planner import SyncPlanner
from .target_resolver import SyncTargetResolver


class ExportService:
    """
    Thin orchestration facade for sync/export workflows.
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
        self.event_emitter = ExportEventEmitter(event_sink)
        self.planner = SyncPlanner()
        self.target_resolver = SyncTargetResolver(
            client=client,
            storage=storage,
            context_engine=self.context_engine,
        )
        self.fetch_orchestrator = SyncFetchOrchestrator(
            client=client,
            storage=storage,
            context_engine=self.context_engine,
        )
        self.checkpoint_manager = SyncCheckpointManager(
            storage=storage,
            emit_event=self._emit_event,
        )
        self.chat_sync = SyncChatCoordinator(
            client=client,
            storage=storage,
            planner=self.planner,
            target_resolver=self.target_resolver,
            fetch_orchestrator=self.fetch_orchestrator,
            checkpoint_manager=self.checkpoint_manager,
            emit_event=self._emit_event,
            emit_sync_progress=self.event_emitter.emit_sync_progress,
        )
        self.dialog_sync = DialogSyncCoordinator(
            client=client,
            emit_event=self._emit_event,
            sync_chat=lambda *args, **kwargs: self.sync_chat(*args, **kwargs),
        )

    def _emit_event(self, event_name: str, **payload: Any) -> None:
        self.event_emitter.emit(event_name, **payload)

    def request_stop(self):
        self.storage.request_stop()

    async def try_fetch_missing_reply(
        self, chat_id: int, missing_reply_to_id: int
    ) -> None:
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
    ):
        return self.planner.build_scan_ranges(
            current_max=current_max,
            head_id=head_id,
            tail_id=tail_id,
            is_complete=is_complete,
            limit=limit,
            history_workers=history_workers,
            allow_history=allow_history,
        )

    @staticmethod
    def _resolve_tail_progress_checkpoint(tail_results: List[Any]) -> Optional[int]:
        return SyncPlanner.resolve_tail_progress_checkpoint(tail_results)

    async def _prefetch_chat_head_messages(
        self,
        entity: Any,
        current_max: int,
        lower_bound: int,
    ):
        return await self.fetch_orchestrator.prefetch_chat_head_messages(
            entity,
            current_max=current_max,
            lower_bound=lower_bound,
        )

    def _resolve_target_report_name(
        self,
        *,
        from_user_id: int,
        target_status: SyncStatus,
    ) -> str:
        return self.target_resolver.resolve_target_report_name(
            from_user_id=from_user_id,
            target_status=target_status,
        )

    def _ensure_user_stats_entry(
        self,
        *,
        user_stats,
        from_user_id: int,
        target_status: SyncStatus,
    ) -> None:
        self.target_resolver.ensure_user_stats_entry(
            user_stats=user_stats,
            from_user_id=from_user_id,
            target_status=target_status,
        )

    def _enqueue_tracked_sync_retry_task(self, plan: Any, exc: Exception) -> None:
        enqueue_sync_target_retry_task(
            self.storage,
            chat_id=plan.chat_id,
            user_id=plan.from_user_id,
            error=exc,
        )

    async def sync_chat(self, entity: Any, **kwargs: Any):
        return await self.chat_sync.sync_chat(entity, **kwargs)

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
        return await self.dialog_sync.sync_all_dialogs_for_user(
            from_user_id,
            target_chat_ids=target_chat_ids,
            limit=limit,
            deep_mode=deep_mode,
            force_resync=force_resync,
            context_window=context_window,
            max_cluster=max_cluster,
            recursive_depth=recursive_depth,
        )

    async def sync_all_outdated(self, threshold_seconds: int = 86400):
        return await self._sync_target_items(
            self.storage.get_outdated_chats(threshold_seconds=threshold_seconds)
        )

    async def sync_all_tracked(self):
        items = [
            (target.chat_id, target.user_id)
            for target in (
                PrimaryTarget.coerce(item)
                for item in self.storage.get_primary_targets()
            )
        ]
        return await self._sync_target_items(items)

    async def _sync_target_items(self, items: list):
        return await self.fetch_orchestrator.run_tracked_targets(
            items,
            emit_event=self._emit_event,
            sync_chat=self.sync_chat,
            ensure_user_stats_entry=self._ensure_user_stats_entry,
            prefetch_chat_head_messages=self._prefetch_chat_head_messages,
            enqueue_retry_task=self._enqueue_tracked_sync_retry_task,
        )
