import logging
from time import perf_counter
from typing import Any, Iterable, List, Set, Tuple

from ...core.models.message import MessageData
from ...core.telemetry import telemetry
from .fetchers import LiveContextResolver, StorageContextResolver
from .models import CandidatePoolRequest, ContextCandidate, ParentLookupRequest

logger = logging.getLogger(__name__)


class ParentReplyResolver:
    def __init__(
        self,
        *,
        storage_resolver: StorageContextResolver,
        live_resolver: LiveContextResolver,
        message_key,
        processed_ids,
    ):
        self.storage_resolver = storage_resolver
        self.live_resolver = live_resolver
        self.message_key = message_key
        self.processed_ids = processed_ids

    def collect_needed_parent_ids(
        self,
        *,
        chat_id: int,
        anchors_by_cluster,
    ) -> List[int]:
        needed_parent_ids: Set[int] = set()
        for anchors in anchors_by_cluster.values():
            for norm in anchors:
                if not norm.reply_to_id:
                    continue
                key = self.message_key(chat_id, norm.reply_to_id)
                if key not in self.processed_ids:
                    needed_parent_ids.add(norm.reply_to_id)
        return sorted(needed_parent_ids)

    async def fetch_parent_messages(
        self,
        *,
        entity: Any,
        request: ParentLookupRequest,
    ) -> dict[int, ContextCandidate]:
        needed_parent_ids = self.collect_needed_parent_ids(
            chat_id=request.chat_id,
            anchors_by_cluster=request.anchors_by_cluster,
        )
        if not needed_parent_ids:
            return {}

        started_at = perf_counter()
        (
            normalized,
            storage_hits,
            missing_ids,
        ) = await self.storage_resolver.load_parent_messages_by_ids(
            chat_id=request.chat_id,
            parent_ids=needed_parent_ids,
        )

        if missing_ids:
            try:
                normalized.update(
                    await self.live_resolver.fetch_parent_messages_by_ids(
                        entity=entity,
                        missing_ids=missing_ids,
                    )
                )
            except Exception as exc:
                logger.warning(
                    "Deep parent live fetch failed for %s: %s", missing_ids, exc
                )
                telemetry.track_counter("deep.parent_lookup.live_failures", 1)

        telemetry.track_counter("deep.parent_lookup.calls", 1)
        telemetry.track_counter("deep.parent_lookup.requested", len(needed_parent_ids))
        telemetry.track_counter("deep.parent_lookup.storage_hits", storage_hits)
        telemetry.track_counter("deep.parent_lookup.live_fetch_ids", len(missing_ids))
        telemetry.track_duration(
            "deep.parent_lookup.total", perf_counter() - started_at
        )
        return normalized


class CandidatePoolResolver:
    def __init__(
        self,
        *,
        storage_resolver: StorageContextResolver,
        live_resolver: LiveContextResolver,
        normalize_message,
    ):
        self.storage_resolver = storage_resolver
        self.live_resolver = live_resolver
        self.normalize_message = normalize_message

    async def fetch_candidate_pool(
        self,
        *,
        entity: Any,
        request: CandidatePoolRequest,
    ) -> List[ContextCandidate]:
        if not request.anchor_ids:
            return []

        started_at = perf_counter()
        ranges = self.calculate_ranges(
            request.anchor_ids,
            before_ids=request.scan_before,
            after_ids=request.scan_after,
        )
        seen = set()
        collected: List[ContextCandidate] = []
        stored_replies = self.storage_resolver.load_stored_replies(
            chat_id=request.chat_id,
            reply_to_ids=request.anchor_ids,
        )

        for start_id, end_id in ranges:
            self.merge_normalized_candidates(
                collected,
                seen,
                await self.collect_range_candidates(
                    entity=entity,
                    chat_id=request.chat_id,
                    start_id=start_id,
                    end_id=end_id,
                    stored_reply_count=len(stored_replies),
                ),
            )

        for message in stored_replies:
            self.append_normalized_candidate(
                collected,
                seen,
                self.normalize_message(
                    message,
                    semantic_source="child_reply",
                    retrieval_source="storage",
                ),
            )

        collected.sort(
            key=lambda norm: (norm.message.timestamp, norm.message.message_id)
        )
        telemetry.track_counter("deep.candidate_pool.calls", 1)
        telemetry.track_counter("deep.candidate_pool.ranges", len(ranges))
        telemetry.track_counter("deep.candidate_pool.messages", len(collected))
        telemetry.track_duration(
            "deep.candidate_pool.total", perf_counter() - started_at
        )
        return collected

    async def collect_range_candidates(
        self,
        *,
        entity: Any,
        chat_id: int,
        start_id: int,
        end_id: int,
        stored_reply_count: int,
    ) -> List[ContextCandidate]:
        stored_messages = self.storage_resolver.load_stored_range(
            chat_id=chat_id,
            start_id=start_id,
            end_id=end_id,
        )
        stored_ids = {message.message_id for message in stored_messages}
        range_width = end_id - start_id + 1
        missing_ids = [
            message_id
            for message_id in range(start_id, end_id + 1)
            if message_id not in stored_ids
        ]
        self.track_range_coverage(range_width, len(stored_ids), len(missing_ids))

        range_seen = set()
        collected: List[ContextCandidate] = []
        self.merge_message_candidates(
            collected,
            range_seen,
            stored_messages,
            semantic_source="range_scan",
            retrieval_source="storage",
        )
        self.merge_message_candidates(
            collected,
            range_seen,
            await self.fetch_live_range_fill(
                entity=entity,
                start_id=start_id,
                end_id=end_id,
                range_width=range_width,
                stored_count=len(stored_ids),
                missing_ids=missing_ids,
                stored_reply_count=stored_reply_count,
            ),
            semantic_source="range_scan",
            retrieval_source="live",
        )
        return collected

    async def fetch_live_range_fill(
        self,
        *,
        entity: Any,
        start_id: int,
        end_id: int,
        range_width: int,
        stored_count: int,
        missing_ids: List[int],
        stored_reply_count: int,
    ) -> List[MessageData]:
        if not missing_ids:
            telemetry.track_counter("deep.fetch_range.local_only.calls", 1)
            return []

        if self.should_selective_live_fill(
            range_width,
            stored_count,
            len(missing_ids),
            stored_reply_count=stored_reply_count,
        ):
            telemetry.track_counter("deep.fetch_range.selective_fill.calls", 1)
            telemetry.track_counter(
                "deep.fetch_range.selective_fill.ids", len(missing_ids)
            )
            try:
                return await self.live_resolver.fetch_missing_ids(
                    entity=entity,
                    message_ids=missing_ids,
                )
            except Exception as exc:
                logger.warning(
                    "Deep selective live fill failed for %s: %s", missing_ids, exc
                )
                telemetry.track_counter("deep.fetch_range.live_failures", 1)
                return []

        if self.should_compact_live_fill(range_width, stored_count, missing_ids):
            compact_ranges = self.build_missing_subranges(missing_ids)
            telemetry.track_counter("deep.fetch_range.compact_fill.calls", 1)
            telemetry.track_counter(
                "deep.fetch_range.compact_fill.ranges", len(compact_ranges)
            )
            telemetry.track_counter(
                "deep.fetch_range.compact_fill.width",
                sum(
                    (compact_end - compact_start + 1)
                    for compact_start, compact_end in compact_ranges
                ),
            )
            try:
                return await self.live_resolver.fetch_ranges(
                    entity=entity,
                    ranges=compact_ranges,
                    retrieval_source="compact",
                )
            except Exception as exc:
                logger.warning(
                    "Deep compact live fill failed for %s: %s", compact_ranges, exc
                )
                telemetry.track_counter("deep.fetch_range.live_failures", 1)
                return []

        telemetry.track_counter("deep.fetch_range.full_scan.calls", 1)
        telemetry.track_counter("deep.fetch_range.full_scan.width", range_width)
        try:
            return await self.live_resolver.fetch_range(
                entity=entity,
                start_id=start_id,
                end_id=end_id,
                retrieval_source="full",
            )
        except Exception as exc:
            logger.warning(
                "Deep full-range live fill failed for %s-%s: %s",
                start_id,
                end_id,
                exc,
            )
            telemetry.track_counter("deep.fetch_range.live_failures", 1)
            return []

    def merge_message_candidates(
        self,
        collected: List[ContextCandidate],
        seen: set,
        messages: Iterable[MessageData],
        *,
        semantic_source: str,
        retrieval_source: str,
    ) -> None:
        for message in messages:
            self.append_normalized_candidate(
                collected,
                seen,
                self.normalize_message(
                    message,
                    semantic_source=semantic_source,
                    retrieval_source=retrieval_source,
                ),
            )

    @staticmethod
    def merge_normalized_candidates(
        collected: List[ContextCandidate],
        seen: set,
        messages: Iterable[ContextCandidate],
    ) -> None:
        for message in messages:
            CandidatePoolResolver.append_normalized_candidate(collected, seen, message)

    @staticmethod
    def append_normalized_candidate(
        collected: List[ContextCandidate],
        seen: set,
        norm: ContextCandidate,
    ) -> None:
        if norm.key in seen:
            return
        seen.add(norm.key)
        collected.append(norm)

    @staticmethod
    def should_selective_live_fill(
        range_width: int,
        stored_count: int,
        missing_count: int,
        stored_reply_count: int = 0,
    ) -> bool:
        if missing_count <= 0 or stored_count <= 0 or range_width <= 0:
            return False

        coverage = stored_count / range_width
        if missing_count <= 25:
            return True
        if coverage >= 0.65 and missing_count <= 200:
            return True
        return stored_reply_count > 0 and coverage >= 0.5 and missing_count <= 120

    @staticmethod
    def should_compact_live_fill(
        range_width: int,
        stored_count: int,
        missing_ids: List[int],
    ) -> bool:
        if range_width <= 0 or stored_count <= 0 or not missing_ids:
            return False
        if len(missing_ids) <= 25:
            return False

        compact_ranges = CandidatePoolResolver.build_missing_subranges(missing_ids)
        compact_width = sum(
            (end_id - start_id + 1) for start_id, end_id in compact_ranges
        )
        coverage = stored_count / range_width

        if len(compact_ranges) > 10:
            return False
        if compact_width >= range_width:
            return False
        if compact_width <= max(40, range_width // 3):
            return True
        return coverage >= 0.35 and compact_width <= int(range_width * 0.55)

    @staticmethod
    def build_missing_subranges(
        missing_ids: List[int],
        pad_before: int = 1,
        pad_after: int = 2,
        merge_gap: int = 3,
    ) -> List[Tuple[int, int]]:
        if not missing_ids:
            return []

        sorted_ids = sorted(
            set(message_id for message_id in missing_ids if message_id > 0)
        )
        if not sorted_ids:
            return []

        ranges: List[Tuple[int, int]] = []
        start_id = max(1, sorted_ids[0] - pad_before)
        end_id = sorted_ids[0] + pad_after

        for message_id in sorted_ids[1:]:
            next_start = max(1, message_id - pad_before)
            next_end = message_id + pad_after
            if next_start <= end_id + merge_gap:
                end_id = max(end_id, next_end)
            else:
                ranges.append((start_id, end_id))
                start_id, end_id = next_start, next_end

        ranges.append((start_id, end_id))
        return ranges

    @staticmethod
    def track_range_coverage(
        range_width: int, stored_count: int, missing_count: int
    ) -> None:
        telemetry.track_counter("deep.fetch_range.range_width", range_width)
        telemetry.track_counter("deep.fetch_range.stored_hits", stored_count)
        telemetry.track_counter("deep.fetch_range.missing_ids", missing_count)

        if range_width <= 0:
            return

        coverage_pct = int((stored_count * 100) / range_width)
        if coverage_pct >= 100:
            telemetry.track_counter("deep.fetch_range.coverage_100.calls", 1)
        elif coverage_pct >= 80:
            telemetry.track_counter("deep.fetch_range.coverage_ge_80.calls", 1)
        elif coverage_pct >= 50:
            telemetry.track_counter("deep.fetch_range.coverage_ge_50.calls", 1)
        else:
            telemetry.track_counter("deep.fetch_range.coverage_lt_50.calls", 1)

    @staticmethod
    def calculate_ranges(
        ids: List[int],
        *,
        before_ids: int,
        after_ids: int,
    ) -> List[Tuple[int, int]]:
        if not ids:
            return []

        adjusted = sorted(
            (max(1, message_id - before_ids), message_id + after_ids)
            for message_id in ids
        )
        ranges: List[Tuple[int, int]] = []
        curr_start, curr_end = adjusted[0]
        for next_start, next_end in adjusted[1:]:
            if next_start <= curr_end + 1:
                curr_end = max(curr_end, next_end)
            else:
                ranges.append((curr_start, curr_end))
                curr_start, curr_end = next_start, next_end
        ranges.append((curr_start, curr_end))
        return ranges
