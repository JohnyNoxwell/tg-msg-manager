import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from tg_msg_manager.services.sync.progress import SyncProgressStats
from tg_msg_manager.services.sync.range_scanner import ScanWorkerState, SyncRangeScanner
from tg_msg_manager.services.sync.scan_ranges import ScanRange


def _message(message_id: int) -> SimpleNamespace:
    return SimpleNamespace(message_id=message_id)


class _StorageWithoutBatchLookup:
    def __init__(self, linked_ids=()):
        self.linked_ids = set(linked_ids)
        self.saved_batches = []
        self.last_msg_ids = []

    def has_target_link(self, _chat_id, message_id, _uid):
        return message_id in self.linked_ids

    def should_stop(self):
        return False

    async def save_messages(self, messages, *, target_id, flush):
        self.saved_batches.append((list(messages), target_id, flush))

    def update_last_msg_id(self, chat_id, uid, message_id):
        self.last_msg_ids.append((chat_id, uid, message_id))


class _AsyncIterator:
    def __init__(self, items):
        self.items = list(items)

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self.items:
            raise StopAsyncIteration
        return self.items.pop(0)


def _scanner(storage, client=None):
    return SyncRangeScanner(
        client=client or object(),
        storage=storage,
        context_engine=object(),
    )


def test_target_link_lookup_falls_back_when_optional_batch_method_is_absent():
    storage = _StorageWithoutBatchLookup(linked_ids={2})

    missing = _scanner(storage).resolve_new_target_link_ids(
        chat_id=1,
        uid=9,
        messages=[_message(1), _message(2), _message(3)],
        force_resync=False,
    )

    assert missing == {1, 3}


def test_force_resync_fast_path_does_not_require_storage_lookup_methods():
    missing = _scanner(object()).resolve_new_target_link_ids(
        chat_id=1,
        uid=9,
        messages=[_message(4), _message(5)],
        force_resync=True,
    )

    assert missing == {4, 5}


def test_scan_buffer_skips_existing_links_flushes_batch_and_updates_head():
    async def run():
        storage = _StorageWithoutBatchLookup(linked_ids={2})
        scanner = _scanner(storage)
        state = ScanWorkerState(scan_buffer=[_message(1), _message(2), _message(3)])
        stats = SyncProgressStats()
        draw_status = AsyncMock()

        await scanner.process_scan_buffer(
            entity=object(),
            chat_id=1,
            uid=9,
            role="HEAD",
            force_resync=False,
            active_deep=False,
            active_depth=1,
            context_window=3,
            max_cluster=20,
            batch_size=2,
            context_batch_size=2,
            can_checkpoint_tail=False,
            worker_state=state,
            progress_stats=stats,
            draw_status=draw_status,
        )

        saved_ids = [
            [message.message_id for message in batch[0]]
            for batch in storage.saved_batches
        ]
        assert saved_ids == [[1, 3]]
        assert storage.last_msg_ids == [(1, 9, 3)]
        assert (stats.processed, stats.skipped, stats.linked) == (2, 1, 2)
        assert state.scan_buffer == []
        assert state.batch == []
        assert state.head_id == 3

    asyncio.run(run())


def test_scan_range_stops_below_lower_bound_and_marks_head_complete():
    async def run():
        storage = _StorageWithoutBatchLookup()
        client = SimpleNamespace(
            iter_messages=lambda *_args, **_kwargs: _AsyncIterator(
                [_message(5), _message(4), _message(2)]
            )
        )
        stats = SyncProgressStats()

        result = await _scanner(storage, client).scan_range(
            entity=object(),
            scan_range=ScanRange(upper=5, lower=3, role="HEAD"),
            chat_id=1,
            uid=9,
            head_id=0,
            tail_id=0,
            api_from_user=None,
            from_user_id=None,
            local_sender_filter_id=None,
            force_resync=True,
            active_deep=False,
            active_depth=1,
            context_window=3,
            max_cluster=20,
            batch_size=10,
            context_batch_size=2,
            single_worker_limit=None,
            can_checkpoint_tail=False,
            prefetched_messages=None,
            prefetched_head_complete=False,
            progress_stats=stats,
            draw_status=AsyncMock(),
        )

        assert result.processed == 2
        assert result.head_id == 5
        assert result.head_scan_complete is True
        assert [message.message_id for message in storage.saved_batches[0][0]] == [5, 4]

    asyncio.run(run())
