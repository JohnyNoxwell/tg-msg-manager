import asyncio
from time import perf_counter
from typing import Any, Awaitable, Callable, List

from ...core.telemetry import telemetry
from ..sync.range_scanner import SyncRangeScanner
from ..sync.tracked_runner import TrackedSyncRunner


class SyncFetchOrchestrator:
    def __init__(self, *, client: Any, storage: Any, context_engine: Any):
        self.client = client
        self.storage = storage
        self.range_scanner = SyncRangeScanner(
            client=client,
            storage=storage,
            context_engine=context_engine,
        )

    async def scan_range(self, **kwargs: Any):
        return await self.range_scanner.scan_range(**kwargs)

    async def prefetch_chat_head_messages(
        self,
        entity: Any,
        current_max: int,
        lower_bound: int,
    ) -> tuple[List[Any], bool]:
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

    async def run_sync_ranges(
        self,
        *,
        execution_plan: Any,
        draw_status: Callable[[str], Awaitable[None]],
        scan_range_factory,
        scan_kwargs: dict[str, Any],
    ) -> tuple[int, list[Any]]:
        results = await asyncio.gather(
            *[
                scan_range_factory(
                    scan_range=scan_range,
                    draw_status=draw_status,
                    **scan_kwargs,
                )
                for scan_range in execution_plan.ranges
            ]
        )
        return sum(result.processed for result in results), results

    async def run_tracked_targets(
        self,
        items: list,
        *,
        emit_event,
        sync_chat,
        ensure_user_stats_entry,
        prefetch_chat_head_messages,
        enqueue_retry_task,
    ):
        runner = TrackedSyncRunner(
            client=self.client,
            storage=self.storage,
            emit_event=emit_event,
            sync_chat=sync_chat,
            ensure_user_stats_entry=ensure_user_stats_entry,
            prefetch_chat_head_messages=prefetch_chat_head_messages,
            enqueue_retry_task=enqueue_retry_task,
        )
        started_at = perf_counter()
        try:
            return await runner.run(items)
        finally:
            telemetry.track_duration(
                "sync.tracked_runner.total", perf_counter() - started_at
            )
