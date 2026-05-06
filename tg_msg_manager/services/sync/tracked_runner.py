import logging
from time import perf_counter
from typing import Any, Awaitable, Callable, Optional

from ...core.models.payloads.export import ExportTrackedUpdateStartedPayload
from ...core.models.sync_report import TrackedSyncRunReport, TrackedSyncUserStat
from ...core.service_events import ExportEvents
from ...core.telemetry import telemetry
from ...infrastructure.storage.records import TargetMessageBreakdown
from .tracked_targets import TrackedSyncPlanner

logger = logging.getLogger(__name__)


class TrackedSyncRunner:
    def __init__(
        self,
        *,
        client: Any,
        storage: Any,
        emit_event: Callable[..., None],
        sync_chat: Callable[..., Awaitable[int]],
        ensure_user_stats_entry: Callable[..., None],
        prefetch_chat_head_messages: Callable[..., Awaitable[tuple[list[Any], bool]]],
        enqueue_retry_task: Optional[Callable[[Any, Exception], None]] = None,
    ):
        self.client = client
        self.storage = storage
        self.emit_event = emit_event
        self.sync_chat = sync_chat
        self.ensure_user_stats_entry = ensure_user_stats_entry
        self.prefetch_chat_head_messages = prefetch_chat_head_messages
        self.enqueue_retry_task = enqueue_retry_task

    def _load_target_message_breakdown(
        self,
        *,
        chat_id: int,
        user_id: int,
    ) -> TargetMessageBreakdown:
        getter = getattr(self.storage, "get_target_message_breakdown", None)
        if not callable(getter):
            return TargetMessageBreakdown()
        return TargetMessageBreakdown.coerce(getter(chat_id, user_id))

    @staticmethod
    def _apply_breakdown_delta(
        *,
        stat: TrackedSyncUserStat,
        before: TargetMessageBreakdown,
        after: TargetMessageBreakdown,
    ) -> None:
        stat.own_messages = max(0, after.own_messages - before.own_messages)
        stat.with_context = max(0, after.with_context - before.with_context)

    @staticmethod
    def _finalize_user_message_breakdowns(
        *,
        user_stats: TrackedSyncRunReport,
    ) -> None:
        for stat in user_stats.values():
            if not stat.dirty and stat.count <= 0:
                continue
            if stat.own_messages <= 0:
                stat.own_messages = stat.count
            if stat.with_context < stat.own_messages:
                stat.with_context = stat.own_messages

    async def run(self, items: list[Any]) -> TrackedSyncRunReport:
        user_stats = TrackedSyncRunReport()
        entity_cache: dict[int, Any] = {}
        current_max_cache: dict[int, int] = {}
        shared_prefetch_cache: dict[int, tuple[list[Any], bool]] = {}
        status_cache: dict[tuple[int, int], Any] = {}

        if not items:
            return user_stats

        tracked_update_payload = ExportTrackedUpdateStartedPayload(
            target_count=len(items)
        )
        self.emit_event(
            ExportEvents.TRACKED_UPDATE_STARTED,
            **tracked_update_payload.as_dict(),
        )

        started_at = perf_counter()
        telemetry.track_counter("sync.tracked_items.total", len(items))
        items_by_chat: dict[int, list[int]] = {}
        planner = TrackedSyncPlanner(
            client=self.client,
            storage=self.storage,
            prefetch_chat_head_messages=self.prefetch_chat_head_messages,
        )
        for item in items:
            chat_id, from_user_id = planner.normalize_target_item(item)
            items_by_chat.setdefault(chat_id, []).append(from_user_id)

        await planner.prime_shared_head_prefetch_cache(
            items_by_chat=items_by_chat,
            entity_cache=entity_cache,
            current_max_cache=current_max_cache,
            shared_prefetch_cache=shared_prefetch_cache,
            status_cache=status_cache,
        )

        for item in items:
            plan = await planner.plan_target(
                item,
                entity_cache=entity_cache,
                current_max_cache=current_max_cache,
                shared_prefetch_cache=shared_prefetch_cache,
                status_cache=status_cache,
            )
            if plan is None:
                continue

            if (
                isinstance(plan.current_max, int)
                and isinstance(plan.last_msg_id, int)
                and plan.current_max <= plan.last_msg_id
                and plan.is_complete
            ):
                telemetry.track_counter("sync.tracked_items.skipped_up_to_date", 1)
                self.ensure_user_stats_entry(
                    user_stats=user_stats,
                    from_user_id=plan.from_user_id,
                    target_status=plan.target_status,
                )
                continue

            breakdown_before = self._load_target_message_breakdown(
                chat_id=plan.chat_id,
                user_id=plan.from_user_id,
            )
            try:
                processed = await self.sync_chat(
                    plan.entity,
                    from_user_id=plan.effective_from_user_id,
                    resume_history=not plan.is_complete,
                    current_max_hint=plan.current_max,
                    prefetched_messages=plan.prefetched_messages,
                    prefetched_head_complete=plan.prefetched_head_complete,
                    resolve_user_entity=False,
                    emit_summary=False,
                )
            except Exception as exc:
                logger.warning(
                    "Tracked sync failed for chat=%s user=%s: %s",
                    plan.chat_id,
                    plan.from_user_id,
                    exc,
                )
                if self.enqueue_retry_task is not None:
                    self.enqueue_retry_task(plan, exc)
                self.ensure_user_stats_entry(
                    user_stats=user_stats,
                    from_user_id=plan.from_user_id,
                    target_status=plan.target_status,
                )
                continue

            self.ensure_user_stats_entry(
                user_stats=user_stats,
                from_user_id=plan.from_user_id,
                target_status=plan.target_status,
            )
            stat = TrackedSyncUserStat.coerce(user_stats[plan.from_user_id])
            stat.count += processed
            if processed > 0:
                breakdown_after = self._load_target_message_breakdown(
                    chat_id=plan.chat_id,
                    user_id=plan.from_user_id,
                )
                self._apply_breakdown_delta(
                    stat=stat,
                    before=breakdown_before,
                    after=breakdown_after,
                )
                stat.dirty = True
                telemetry.track_counter("sync.tracked_items.changed", 1)
            user_stats[plan.from_user_id] = stat

        telemetry.track_duration("sync.all_tracked.total", perf_counter() - started_at)
        self._finalize_user_message_breakdowns(user_stats=user_stats)
        telemetry.log_summary("Tracked sync telemetry summary")
        return user_stats
