from dataclasses import dataclass, field
from time import perf_counter
from typing import Any, AsyncIterator, Awaitable, Callable, Optional

from ...core.telemetry import telemetry
from .progress import SyncProgressStats
from .scan_execution import (
    build_scan_message_stream,
    mark_scan_completion_flags,
    should_skip_scan_message,
)
from .scan_ranges import ScanRange, ScanRangeResult


@dataclass
class ScanWorkerState:
    processed: int = 0
    batch: list[Any] = field(default_factory=list)
    context_batch: list[Any] = field(default_factory=list)
    scan_buffer: list[Any] = field(default_factory=list)
    tail_id: Optional[int] = None
    head_id: int = 0
    head_scan_complete: bool = False
    tail_scan_complete: bool = False


class SyncRangeScanner:
    def __init__(
        self,
        *,
        client: Any,
        storage: Any,
        context_engine: Any,
    ):
        self.client = client
        self.storage = storage
        self.context_engine = context_engine

    def resolve_new_target_link_ids(
        self,
        *,
        chat_id: int,
        uid: int,
        messages: list[Any],
        force_resync: bool,
    ) -> set[int]:
        started_at = perf_counter()
        if force_resync or not messages:
            resolved = {msg.message_id for msg in messages}
            telemetry.track_counter("sync.target_link_lookup.fast_path", len(resolved))
            telemetry.track_duration(
                "sync.target_link_lookup.total", perf_counter() - started_at
            )
            return resolved

        message_ids = [msg.message_id for msg in messages]
        filter_missing = getattr(self.storage, "filter_missing_target_links", None)
        missing = None
        if callable(filter_missing):
            try:
                result = filter_missing(chat_id, uid, message_ids)
            except TypeError:
                result = None
            if isinstance(result, list):
                missing = set(result)

        if missing is None:
            missing = {
                msg.message_id
                for msg in messages
                if not self.storage.has_target_link(chat_id, msg.message_id, uid)
            }
        telemetry.track_counter("sync.target_link_lookup.batches", 1)
        telemetry.track_counter("sync.target_link_lookup.candidates", len(message_ids))
        telemetry.track_counter("sync.target_link_lookup.missing", len(missing))
        telemetry.track_duration(
            "sync.target_link_lookup.total", perf_counter() - started_at
        )
        return missing

    def checkpoint_worker_progress(
        self,
        *,
        chat_id: int,
        uid: int,
        role: str,
        can_checkpoint_tail: bool,
        worker_state: ScanWorkerState,
    ) -> None:
        if role == "TAIL" and can_checkpoint_tail and worker_state.tail_id is not None:
            self.storage.update_sync_tail(
                chat_id, uid, worker_state.tail_id, is_complete=False
            )
        elif role == "HEAD":
            self.storage.update_last_msg_id(chat_id, uid, worker_state.head_id)

    @staticmethod
    def record_processed_scan_message(
        *,
        worker_state: ScanWorkerState,
        progress_stats: SyncProgressStats,
        role: str,
        message_id: int,
    ) -> None:
        worker_state.processed += 1
        progress_stats.processed += 1
        if role == "TAIL":
            worker_state.tail_id = message_id
        else:
            worker_state.head_id = max(worker_state.head_id, message_id)

    async def flush_flat_worker_batch(
        self,
        *,
        chat_id: int,
        uid: int,
        role: str,
        can_checkpoint_tail: bool,
        worker_state: ScanWorkerState,
        progress_stats: SyncProgressStats,
        draw_status: Callable[[str], Awaitable[None]],
    ) -> None:
        if not worker_state.batch:
            return

        batch_started = perf_counter()
        await self.storage.save_messages(worker_state.batch, target_id=uid, flush=False)
        telemetry.track_duration(
            "sync.flat_batch_save.total", perf_counter() - batch_started
        )
        progress_stats.linked += len(worker_state.batch)
        telemetry.track_counter("sync.flat_batches", 1)
        telemetry.track_counter("sync.flat_messages", len(worker_state.batch))
        self.checkpoint_worker_progress(
            chat_id=chat_id,
            uid=uid,
            role=role,
            can_checkpoint_tail=can_checkpoint_tail,
            worker_state=worker_state,
        )
        telemetry.track_messages(len(worker_state.batch))
        worker_state.batch = []
        await draw_status()

    async def flush_deep_worker_batch(
        self,
        *,
        entity: Any,
        chat_id: int,
        uid: int,
        role: str,
        can_checkpoint_tail: bool,
        worker_state: ScanWorkerState,
        progress_stats: SyncProgressStats,
        context_window: int,
        max_cluster: int,
        active_depth: int,
        draw_status: Callable[[str], Awaitable[None]],
        progress_message_id: Optional[int] = None,
    ) -> None:
        if not worker_state.context_batch:
            return

        batch_size_now = len(worker_state.context_batch)
        saved_count = await self.context_engine.extract_batch_context(
            entity,
            worker_state.context_batch,
            target_id=uid,
            window_size=context_window,
            max_cluster=max_cluster,
            recursive_depth=active_depth,
            on_progress=(
                draw_status
                if progress_message_id is None
                else lambda: draw_status(f"(ID: {progress_message_id})")
            ),
        )
        progress_stats.linked += saved_count
        telemetry.track_counter("sync.deep_batches", 1)
        telemetry.track_counter("sync.deep_messages", batch_size_now)
        self.checkpoint_worker_progress(
            chat_id=chat_id,
            uid=uid,
            role=role,
            can_checkpoint_tail=can_checkpoint_tail,
            worker_state=worker_state,
        )
        worker_state.context_batch = []

    async def process_scan_buffer(
        self,
        *,
        entity: Any,
        chat_id: int,
        uid: int,
        role: str,
        force_resync: bool,
        active_deep: bool,
        active_depth: int,
        context_window: int,
        max_cluster: int,
        batch_size: int,
        context_batch_size: int,
        can_checkpoint_tail: bool,
        worker_state: ScanWorkerState,
        progress_stats: SyncProgressStats,
        draw_status: Callable[[str], Awaitable[None]],
    ) -> None:
        if not worker_state.scan_buffer:
            return

        missing_ids = self.resolve_new_target_link_ids(
            chat_id=chat_id,
            uid=uid,
            messages=worker_state.scan_buffer,
            force_resync=force_resync,
        )
        for msg_data in worker_state.scan_buffer:
            is_new = msg_data.message_id in missing_ids
            if not is_new and not force_resync:
                progress_stats.skipped += 1
                if progress_stats.skipped % 100 == 0:
                    await draw_status()
                continue

            if active_deep:
                if self.storage.should_stop():
                    break

                worker_state.context_batch.append(msg_data)
                if len(worker_state.context_batch) >= context_batch_size:
                    if self.storage.should_stop():
                        break

                    await self.flush_deep_worker_batch(
                        entity=entity,
                        chat_id=chat_id,
                        uid=uid,
                        role=role,
                        can_checkpoint_tail=can_checkpoint_tail,
                        worker_state=worker_state,
                        progress_stats=progress_stats,
                        context_window=context_window,
                        max_cluster=max_cluster,
                        active_depth=active_depth,
                        draw_status=draw_status,
                        progress_message_id=msg_data.message_id,
                    )
                    await draw_status()
            else:
                worker_state.batch.append(msg_data)

            self.record_processed_scan_message(
                worker_state=worker_state,
                progress_stats=progress_stats,
                role=role,
                message_id=msg_data.message_id,
            )

            if worker_state.processed % 50 == 0:
                await draw_status()

            if len(worker_state.batch) >= batch_size:
                await self.flush_flat_worker_batch(
                    chat_id=chat_id,
                    uid=uid,
                    role=role,
                    can_checkpoint_tail=can_checkpoint_tail,
                    worker_state=worker_state,
                    progress_stats=progress_stats,
                    draw_status=draw_status,
                )

        worker_state.scan_buffer = []

    @staticmethod
    async def iter_prefetched_messages(messages: list[Any]) -> AsyncIterator[Any]:
        for message in messages:
            yield message

    async def scan_range(
        self,
        *,
        entity: Any,
        scan_range: ScanRange,
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
        prefetched_messages: Optional[list[Any]],
        prefetched_head_complete: bool,
        progress_stats: SyncProgressStats,
        draw_status: Callable[[str], Awaitable[None]],
    ) -> ScanRangeResult:
        worker_state = ScanWorkerState(head_id=head_id)
        message_stream, using_prefetched_messages = build_scan_message_stream(
            client=self.client,
            entity=entity,
            scan_range=scan_range,
            single_worker_limit=single_worker_limit,
            api_from_user=api_from_user,
            prefetched_messages=prefetched_messages,
            iter_prefetched_messages=self.iter_prefetched_messages,
        )
        if using_prefetched_messages:
            telemetry.track_counter("sync.prefetched_head.used", 1)

        async for msg_data in message_stream:
            if self.storage.should_stop():
                break

            if msg_data.message_id < scan_range.lower:
                if scan_range.role == "HEAD" and single_worker_limit is None:
                    worker_state.head_scan_complete = True
                if scan_range.role == "TAIL" and single_worker_limit is None:
                    worker_state.tail_scan_complete = True
                break

            if should_skip_scan_message(
                msg_data=msg_data,
                scan_range=scan_range,
                from_user_id=from_user_id,
                local_sender_filter_id=local_sender_filter_id,
                using_prefetched_messages=using_prefetched_messages,
                force_resync=force_resync,
                tail_id=tail_id,
                head_id=head_id,
            ):
                continue

            worker_state.scan_buffer.append(msg_data)
            if len(worker_state.scan_buffer) >= 100:
                await self.process_scan_buffer(
                    entity=entity,
                    chat_id=chat_id,
                    uid=uid,
                    role=scan_range.role,
                    force_resync=force_resync,
                    active_deep=active_deep,
                    active_depth=active_depth,
                    context_window=context_window,
                    max_cluster=max_cluster,
                    batch_size=batch_size,
                    context_batch_size=context_batch_size,
                    can_checkpoint_tail=can_checkpoint_tail,
                    worker_state=worker_state,
                    progress_stats=progress_stats,
                    draw_status=draw_status,
                )

        mark_scan_completion_flags(
            worker_state=worker_state,
            scan_range=scan_range,
            single_worker_limit=single_worker_limit,
            stop_requested=self.storage.should_stop(),
            using_prefetched_messages=using_prefetched_messages,
            prefetched_head_complete=prefetched_head_complete,
        )

        await self.process_scan_buffer(
            entity=entity,
            chat_id=chat_id,
            uid=uid,
            role=scan_range.role,
            force_resync=force_resync,
            active_deep=active_deep,
            active_depth=active_depth,
            context_window=context_window,
            max_cluster=max_cluster,
            batch_size=batch_size,
            context_batch_size=context_batch_size,
            can_checkpoint_tail=can_checkpoint_tail,
            worker_state=worker_state,
            progress_stats=progress_stats,
            draw_status=draw_status,
        )
        if active_deep:
            await self.flush_deep_worker_batch(
                entity=entity,
                chat_id=chat_id,
                uid=uid,
                role=scan_range.role,
                can_checkpoint_tail=can_checkpoint_tail,
                worker_state=worker_state,
                progress_stats=progress_stats,
                context_window=context_window,
                max_cluster=max_cluster,
                active_depth=active_depth,
                draw_status=draw_status,
            )
        await self.flush_flat_worker_batch(
            chat_id=chat_id,
            uid=uid,
            role=scan_range.role,
            can_checkpoint_tail=can_checkpoint_tail,
            worker_state=worker_state,
            progress_stats=progress_stats,
            draw_status=draw_status,
        )

        return ScanRangeResult(
            processed=worker_state.processed,
            tail_id=worker_state.tail_id,
            head_id=worker_state.head_id,
            head_scan_complete=worker_state.head_scan_complete,
            tail_scan_complete=worker_state.tail_scan_complete,
            upper=scan_range.upper,
            lower=scan_range.lower,
            role=scan_range.role,
        )
