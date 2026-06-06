import asyncio
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import ANY, AsyncMock

from tg_msg_manager.services.context.fetchers import StorageContextResolver
from tg_msg_manager.services.context.models import CandidatePoolRequest
from tg_msg_manager.services.context.resolvers import CandidatePoolResolver


def _message(message_id: int, *, seconds: int = 0) -> SimpleNamespace:
    return SimpleNamespace(
        chat_id=1,
        message_id=message_id,
        timestamp=datetime(2025, 1, 1) + timedelta(seconds=seconds),
    )


def _normalize(message, *, semantic_source="unknown", retrieval_source="unknown"):
    return SimpleNamespace(
        key=(message.chat_id, message.message_id),
        message=message,
        semantic_source=semantic_source,
        retrieval_source=retrieval_source,
    )


class _StorageResolver:
    def __init__(self, *, stored_range, stored_replies):
        self.stored_range = stored_range
        self.stored_replies = stored_replies

    def load_stored_range(self, **_kwargs):
        return self.stored_range

    def load_stored_replies(self, **_kwargs):
        return self.stored_replies


def test_candidate_pool_merges_ranges_deduplicates_and_sorts_candidates():
    async def run():
        stored_anchor = _message(10, seconds=10)
        stored_reply = _message(12, seconds=30)
        live_fill = _message(11, seconds=20)
        storage = _StorageResolver(
            stored_range=[stored_anchor, stored_reply],
            stored_replies=[stored_reply],
        )
        live = SimpleNamespace(
            fetch_missing_ids=AsyncMock(return_value=[live_fill]),
        )
        resolver = CandidatePoolResolver(
            storage_resolver=storage,
            live_resolver=live,
            normalize_message=_normalize,
        )

        candidates = await resolver.fetch_candidate_pool(
            entity=object(),
            request=CandidatePoolRequest(
                chat_id=1,
                anchor_ids=[10],
                scan_before=0,
                scan_after=2,
            ),
        )

        assert [candidate.message.message_id for candidate in candidates] == [
            10,
            11,
            12,
        ]
        assert candidates[1].retrieval_source == "live"
        assert candidates[2].semantic_source == "range_scan"
        live.fetch_missing_ids.assert_awaited_once_with(
            entity=ANY,
            message_ids=[11],
        )

    asyncio.run(run())


def test_candidate_pool_range_calculation_merges_overlaps_and_clamps_lower_bound():
    assert CandidatePoolResolver.calculate_ranges(
        [2, 10, 12],
        before_ids=4,
        after_ids=2,
    ) == [(1, 4), (6, 14)]


def test_storage_context_resolver_treats_absent_optional_methods_as_no_local_data():
    resolver = StorageContextResolver(
        storage=object(),
        normalize_message=_normalize,
    )

    assert resolver.load_stored_range(chat_id=1, start_id=1, end_id=3) == []
    assert resolver.load_stored_replies(chat_id=1, reply_to_ids=[2]) == []
    assert resolver.load_stored_messages_by_ids(1, [2]) is None
