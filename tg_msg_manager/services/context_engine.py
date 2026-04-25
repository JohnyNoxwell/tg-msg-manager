import asyncio
import logging
import uuid
from dataclasses import dataclass, field, replace
from datetime import timedelta
from time import perf_counter
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from ..core.models.message import MessageData
from ..core.telemetry import telemetry
from ..core.telegram.interface import TelegramClientInterface
from ..infrastructure.storage.interface import BaseStorage

logger = logging.getLogger(__name__)


MessageKey = Tuple[int, int]
STRUCTURAL_REASONS = {"self", "parent_reply", "reply_to_target", "reply_chain"}


@dataclass(frozen=True)
class _NormalizedContextMessage:
    message: MessageData
    reply_to_id: Optional[int]
    reply_to_top_id: Optional[int]
    forum_topic: bool

    @property
    def key(self) -> MessageKey:
        return (self.message.chat_id, self.message.message_id)

    @property
    def topic_id(self) -> Optional[int]:
        if self.reply_to_top_id:
            return self.reply_to_top_id
        if self.forum_topic:
            return self.message.message_id
        return None


@dataclass
class _ClusterState:
    cluster_id: str
    target: _NormalizedContextMessage
    messages: Dict[MessageKey, _NormalizedContextMessage] = field(default_factory=dict)
    reasons: Dict[MessageKey, str] = field(default_factory=dict)
    structural_count: int = 0

    @property
    def topic_id(self) -> Optional[int]:
        return self.target.topic_id

    def structural_messages(self) -> List[_NormalizedContextMessage]:
        return [
            norm
            for key, norm in self.messages.items()
            if self.reasons.get(key) in STRUCTURAL_REASONS
        ]

    def remaining_slots(self, max_cluster: int) -> int:
        if max_cluster <= 0:
            return 10**9
        return max(0, max_cluster - len(self.messages))


class DeepModeEngine:
    """
    Deep mode that prefers Telegram's structural links over local message-id windows.
    """

    def __init__(
        self,
        client: TelegramClientInterface,
        storage: BaseStorage,
        max_concurrency: int = 15,
    ):
        self.client = client
        self.storage = storage
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self._processed_ids: Set[MessageKey] = set()

    def reset(self):
        """Clears per-run processed state so separate syncs do not leak into each other."""
        self._processed_ids.clear()

    @staticmethod
    def _message_key(chat_id: int, message_id: int) -> MessageKey:
        return (chat_id, message_id)

    async def extract_batch_context(
        self,
        entity: Any,
        target_messages: List[MessageData],
        target_id: Optional[int] = None,
        window_size: int = 3,
        max_cluster: int = 20,
        recursive_depth: int = 3,
        on_progress: Optional[Any] = None,
    ) -> int:
        """
        Builds a deterministic context cluster for each target message.
        """
        if not target_messages or recursive_depth <= 0:
            return 0

        started_at = perf_counter()
        active_depth = min(max(recursive_depth, 1), 3)
        clusters = self._initialize_clusters(target_messages)
        if not clusters:
            return 0

        telemetry.track_counter("deep.extract_batch.calls", 1)
        telemetry.track_counter("deep.extract_batch.targets", len(target_messages))
        telemetry.track_counter("deep.extract_batch.clusters", len(clusters))
        await self.storage.save_messages(
            [cluster.target.message for cluster in clusters],
            target_id=target_id,
            flush=False,
        )
        saved_count = len(clusters)
        if on_progress:
            await on_progress()

        chat_id = clusters[0].target.message.chat_id

        saved_count += await self._expand_structural_round(
            entity,
            chat_id,
            clusters,
            target_id=target_id,
            window_size=window_size,
            max_cluster=max_cluster,
            round_number=1,
            on_progress=on_progress,
        )

        if active_depth >= 2:
            saved_count += await self._expand_structural_round(
                entity,
                chat_id,
                clusters,
                target_id=target_id,
                window_size=window_size,
                max_cluster=max_cluster,
                round_number=2,
                on_progress=on_progress,
            )

        if active_depth >= 3:
            saved_count += await self._apply_time_fallback(
                entity,
                chat_id,
                clusters,
                target_id=target_id,
                window_size=window_size,
                max_cluster=max_cluster,
                on_progress=on_progress,
            )
        telemetry.track_counter("deep.extract_batch.saved_messages", saved_count)
        telemetry.track_duration("deep.extract_batch.total", perf_counter() - started_at)
        return saved_count

    def _initialize_clusters(self, target_messages: List[MessageData]) -> List[_ClusterState]:
        clusters: List[_ClusterState] = []
        for msg in target_messages:
            key = self._message_key(msg.chat_id, msg.message_id)
            if key in self._processed_ids:
                continue

            cluster_id = msg.context_group_id or str(uuid.uuid4())
            clustered = self._with_cluster(msg, cluster_id)
            normalized = self._normalize_message(clustered)
            cluster = _ClusterState(cluster_id=cluster_id, target=normalized)
            cluster.messages[normalized.key] = normalized
            cluster.reasons[normalized.key] = "self"
            clusters.append(cluster)
            self._processed_ids.add(normalized.key)
        return clusters

    async def _expand_structural_round(
        self,
        entity: Any,
        chat_id: int,
        clusters: List[_ClusterState],
        target_id: Optional[int],
        window_size: int,
        max_cluster: int,
        round_number: int,
        on_progress: Optional[Any],
    ) -> int:
        anchors_by_cluster = self._build_anchors_by_cluster(clusters, round_number, max_cluster)
        if not anchors_by_cluster:
            return 0

        round_started = perf_counter()
        parents = await self._fetch_parent_messages(entity, chat_id, anchors_by_cluster)
        parent_additions = self._associate_parents(
            clusters,
            anchors_by_cluster,
            parents,
            max_cluster=max_cluster,
        )
        saved_count = await self._flush_new_messages(parent_additions, target_id=target_id, on_progress=on_progress)

        candidate_messages = await self._fetch_candidate_pool(
            entity,
            chat_id,
            anchor_ids=[
                anchor.message.message_id
                for anchors in anchors_by_cluster.values()
                for anchor in anchors
            ],
            scan_before=self._scan_before_ids(round_number, window_size),
            scan_after=self._scan_after_ids(round_number, window_size, max_cluster),
        )
        candidate_additions = self._associate_candidates(
            clusters,
            candidate_messages,
            round_number=round_number,
            max_cluster=max_cluster,
        )
        saved_count += await self._flush_new_messages(candidate_additions, target_id=target_id, on_progress=on_progress)
        telemetry.track_counter(f"deep.round_{round_number}.clusters", len(anchors_by_cluster))
        telemetry.track_counter(f"deep.round_{round_number}.saved_messages", saved_count)
        telemetry.track_duration(f"deep.round_{round_number}.total", perf_counter() - round_started)
        return saved_count

    def _build_anchors_by_cluster(
        self,
        clusters: List[_ClusterState],
        round_number: int,
        max_cluster: int,
    ) -> Dict[str, List[_NormalizedContextMessage]]:
        anchors_by_cluster: Dict[str, List[_NormalizedContextMessage]] = {}
        for cluster in clusters:
            if cluster.remaining_slots(max_cluster) <= 0:
                continue

            anchors = self._round_anchors(cluster, round_number)
            if anchors:
                anchors_by_cluster[cluster.cluster_id] = anchors
        return anchors_by_cluster

    def _round_anchors(
        self,
        cluster: _ClusterState,
        round_number: int,
    ) -> List[_NormalizedContextMessage]:
        if round_number == 1:
            return [cluster.target]
        return cluster.structural_messages()

    async def _fetch_parent_messages(
        self,
        entity: Any,
        chat_id: int,
        anchors_by_cluster: Dict[str, List[_NormalizedContextMessage]],
    ) -> Dict[int, _NormalizedContextMessage]:
        needed_parent_ids: Set[int] = set()
        for anchors in anchors_by_cluster.values():
            for norm in anchors:
                if norm.reply_to_id:
                    key = self._message_key(chat_id, norm.reply_to_id)
                    if key not in self._processed_ids:
                        needed_parent_ids.add(norm.reply_to_id)

        if not needed_parent_ids:
            return {}

        started_at = perf_counter()
        normalized: Dict[int, _NormalizedContextMessage] = {}
        stored_messages = self._load_stored_messages_by_ids(chat_id, sorted(needed_parent_ids))
        if stored_messages is None:
            storage_hits = 0
            missing_ids: List[int] = []
            for parent_id in sorted(needed_parent_ids):
                stored = await asyncio.to_thread(self.storage.get_message, chat_id, parent_id)
                if stored:
                    normalized[parent_id] = self._normalize_message(stored)
                    storage_hits += 1
                else:
                    missing_ids.append(parent_id)
        else:
            for stored in stored_messages.values():
                normalized[stored.message.message_id] = self._normalize_message(stored)
            storage_hits = len(stored_messages)

            missing_ids = [
                parent_id
                for parent_id in sorted(needed_parent_ids)
                if parent_id not in normalized
            ]

        if missing_ids:
            try:
                async with self.semaphore:
                    fetched = await self.client.get_messages(entity, message_ids=missing_ids)
            except TypeError:
                async with self.semaphore:
                    fetched = await self.client.get_messages(entity, missing_ids)

            for msg in fetched:
                norm = self._normalize_message(msg)
                normalized[norm.message.message_id] = norm

        telemetry.track_counter("deep.parent_lookup.calls", 1)
        telemetry.track_counter("deep.parent_lookup.requested", len(needed_parent_ids))
        telemetry.track_counter("deep.parent_lookup.storage_hits", storage_hits)
        telemetry.track_counter("deep.parent_lookup.live_fetch_ids", len(missing_ids))
        telemetry.track_duration("deep.parent_lookup.total", perf_counter() - started_at)
        return normalized

    def _associate_parents(
        self,
        clusters: List[_ClusterState],
        anchors_by_cluster: Dict[str, List[_NormalizedContextMessage]],
        parents: Dict[int, _NormalizedContextMessage],
        max_cluster: int,
    ) -> List[MessageData]:
        additions: List[MessageData] = []
        clusters_by_id = {cluster.cluster_id: cluster for cluster in clusters}
        for cluster_id, anchors in anchors_by_cluster.items():
            cluster_state = clusters_by_id.get(cluster_id)
            if cluster_state is None:
                continue
            for anchor in anchors:
                if not anchor.reply_to_id:
                    continue
                parent = parents.get(anchor.reply_to_id)
                if not parent:
                    continue
                if self._add_to_cluster(cluster_state, parent, "parent_reply", max_cluster=max_cluster, structural=True):
                    additions.append(self._with_cluster(parent.message, cluster_state.cluster_id))
        return additions

    async def _fetch_candidate_pool(
        self,
        entity: Any,
        chat_id: int,
        anchor_ids: List[int],
        scan_before: int,
        scan_after: int,
    ) -> List[_NormalizedContextMessage]:
        if not anchor_ids:
            return []

        started_at = perf_counter()
        ranges = self._calculate_ranges(anchor_ids, before_ids=scan_before, after_ids=scan_after)
        seen: Set[MessageKey] = set()
        collected: List[_NormalizedContextMessage] = []

        for start_id, end_id in ranges:
            for message in self._load_stored_range(chat_id, start_id, end_id):
                norm = self._normalize_message(message)
                if norm.key in seen:
                    continue
                seen.add(norm.key)
                collected.append(norm)

            for message in await self._fetch_range(entity, start_id, end_id):
                norm = self._normalize_message(message)
                if norm.key in seen:
                    continue
                seen.add(norm.key)
                collected.append(norm)

        stored_replies = self._load_stored_replies(chat_id, anchor_ids)
        for message in stored_replies:
            norm = self._normalize_message(message)
            if norm.key in seen:
                continue
            seen.add(norm.key)
            collected.append(norm)

        collected.sort(key=lambda norm: (norm.message.timestamp, norm.message.message_id))
        telemetry.track_counter("deep.candidate_pool.calls", 1)
        telemetry.track_counter("deep.candidate_pool.ranges", len(ranges))
        telemetry.track_counter("deep.candidate_pool.messages", len(collected))
        telemetry.track_duration("deep.candidate_pool.total", perf_counter() - started_at)
        return collected

    def _associate_candidates(
        self,
        clusters: List[_ClusterState],
        candidates: List[_NormalizedContextMessage],
        round_number: int,
        max_cluster: int,
    ) -> List[MessageData]:
        additions: List[MessageData] = []
        for candidate in candidates:
            if candidate.message.is_service:
                continue

            for cluster in clusters:
                if cluster.remaining_slots(max_cluster) <= 0:
                    continue
                if candidate.key in cluster.messages or candidate.key in self._processed_ids:
                    continue

                reason, structural = self._detect_relation(cluster, candidate, round_number)
                if not reason:
                    continue

                if self._add_to_cluster(cluster, candidate, reason, max_cluster=max_cluster, structural=structural):
                    additions.append(self._with_cluster(candidate.message, cluster.cluster_id))
                    break
        return additions

    def _detect_relation(
        self,
        cluster: _ClusterState,
        candidate: _NormalizedContextMessage,
        round_number: int,
    ) -> Tuple[Optional[str], bool]:
        if candidate.key == cluster.target.key:
            return None, False
        if self._is_topic_mismatch(cluster, candidate):
            return None, False

        structural_ids = {
            norm.message.message_id
            for norm in cluster.structural_messages()
        }
        target_id = cluster.target.message.message_id

        if candidate.reply_to_id == target_id:
            return "reply_to_target", True

        if round_number >= 2 and candidate.reply_to_id in structural_ids:
            return "reply_chain", True

        if round_number >= 2 and cluster.topic_id and candidate.topic_id == cluster.topic_id:
            return "same_topic", False

        return None, False

    async def _apply_time_fallback(
        self,
        entity: Any,
        chat_id: int,
        clusters: List[_ClusterState],
        target_id: Optional[int],
        window_size: int,
        max_cluster: int,
        on_progress: Optional[Any],
    ) -> int:
        fallback_clusters = [
            cluster
            for cluster in clusters
            if cluster.structural_count == 0
            and cluster.target.reply_to_id is None
            and cluster.topic_id is None
            and cluster.remaining_slots(max_cluster) > 0
        ]
        if not fallback_clusters:
            return 0

        started_at = perf_counter()
        additions: List[MessageData] = []
        for cluster in fallback_clusters:
            local_candidates = await self._fetch_candidate_pool(
                entity,
                chat_id,
                anchor_ids=[cluster.target.message.message_id],
                scan_before=max(4, window_size * 2),
                scan_after=max(6, window_size * 3),
            )
            for norm in self._select_time_fallback(cluster, local_candidates, window_size=window_size, max_cluster=max_cluster):
                if self._add_to_cluster(cluster, norm, "time_fallback", max_cluster=max_cluster, structural=False):
                    additions.append(self._with_cluster(norm.message, cluster.cluster_id))

        saved_count = await self._flush_new_messages(additions, target_id=target_id, on_progress=on_progress)
        telemetry.track_counter("deep.time_fallback.clusters", len(fallback_clusters))
        telemetry.track_counter("deep.time_fallback.saved_messages", saved_count)
        telemetry.track_duration("deep.time_fallback.total", perf_counter() - started_at)
        return saved_count

    def _select_time_fallback(
        self,
        cluster: _ClusterState,
        candidates: List[_NormalizedContextMessage],
        window_size: int,
        max_cluster: int,
    ) -> List[_NormalizedContextMessage]:
        ordered = sorted(candidates, key=lambda norm: (norm.message.timestamp, norm.message.message_id))
        target_index = None
        for idx, norm in enumerate(ordered):
            if norm.key == cluster.target.key:
                target_index = idx
                break
        if target_index is None:
            return []

        max_before = max(1, min(window_size, 3))
        max_after = max(2, min(window_size + 1, 4))
        max_gap = timedelta(minutes=2)
        max_total_before = timedelta(minutes=15)
        max_total_after = timedelta(minutes=20)
        selected: List[_NormalizedContextMessage] = []

        def walk(direction: int, limit_count: int, max_total_delta: timedelta):
            last = cluster.target
            added = 0
            skipped = 0
            idx = target_index + direction
            while 0 <= idx < len(ordered) and added < limit_count and cluster.remaining_slots(max_cluster) > len(selected):
                norm = ordered[idx]
                idx += direction
                if norm.key in cluster.messages or norm.key in self._processed_ids or norm.message.is_service:
                    skipped += 1
                    if skipped >= 2:
                        break
                    continue

                current_gap = abs(norm.message.timestamp - last.message.timestamp)
                total_delta = abs(norm.message.timestamp - cluster.target.message.timestamp)
                if current_gap > max_gap or total_delta > max_total_delta:
                    break

                selected.append(norm)
                last = norm
                added += 1
                skipped = 0

        walk(-1, max_before, max_total_before)
        walk(1, max_after, max_total_after)
        selected.sort(key=lambda norm: (norm.message.timestamp, norm.message.message_id))
        return selected

    async def _flush_new_messages(
        self,
        messages: List[MessageData],
        target_id: Optional[int],
        on_progress: Optional[Any],
    ) -> int:
        if not messages:
            return 0
        await self.storage.save_messages(messages, target_id=target_id, flush=False)
        telemetry.track_counter("deep.flush_new_messages.calls", 1)
        telemetry.track_counter("deep.flush_new_messages.messages", len(messages))
        if on_progress:
            await on_progress()
        return len(messages)

    def _add_to_cluster(
        self,
        cluster: _ClusterState,
        norm: _NormalizedContextMessage,
        reason: str,
        max_cluster: int,
        structural: bool,
    ) -> bool:
        if norm.key in cluster.messages or norm.key in self._processed_ids:
            return False
        if norm.message.is_service:
            return False
        if cluster.remaining_slots(max_cluster) <= 0:
            return False
        if self._is_topic_mismatch(cluster, norm):
            return False

        cluster.messages[norm.key] = norm
        cluster.reasons[norm.key] = reason
        if structural:
            cluster.structural_count += 1
        self._processed_ids.add(norm.key)
        logger.debug(
            "Deep cluster %s added message %s via %s",
            cluster.cluster_id,
            norm.message.message_id,
            reason,
        )
        return True

    def _is_topic_mismatch(self, cluster: _ClusterState, norm: _NormalizedContextMessage) -> bool:
        if cluster.topic_id is None or norm.topic_id is None:
            return False
        return cluster.topic_id != norm.topic_id

    def _normalize_message(self, msg: MessageData) -> _NormalizedContextMessage:
        raw = msg.raw_payload or {}
        reply_to = raw.get("reply_to") if isinstance(raw, dict) else {}
        if not isinstance(reply_to, dict):
            reply_to = {}

        reply_to_id = msg.reply_to_id or reply_to.get("reply_to_msg_id")
        reply_to_top_id = reply_to.get("reply_to_top_id")
        forum_topic = bool(reply_to.get("forum_topic"))

        return _NormalizedContextMessage(
            message=msg,
            reply_to_id=reply_to_id,
            reply_to_top_id=reply_to_top_id,
            forum_topic=forum_topic,
        )

    async def _fetch_range(self, entity: Any, start_id: int, end_id: int) -> List[MessageData]:
        started_at = perf_counter()
        results: List[MessageData] = []
        async with self.semaphore:
            async for msg_data in self.client.iter_messages(
                entity,
                limit=(end_id - start_id + 1),
                offset_id=end_id + 1,
            ):
                if msg_data.message_id < start_id:
                    break
                results.append(msg_data)
        telemetry.track_counter("deep.fetch_range.calls", 1)
        telemetry.track_counter("deep.fetch_range.messages", len(results))
        telemetry.track_duration("deep.fetch_range.total", perf_counter() - started_at)
        return results

    def _load_stored_range(self, chat_id: int, start_id: int, end_id: int) -> List[MessageData]:
        getter = getattr(self.storage, "get_messages_in_id_range", None)
        if not callable(getter):
            return []
        started_at = perf_counter()
        try:
            result = getter(chat_id, start_id, end_id)
        except TypeError:
            return []
        rows = result if isinstance(result, list) else []
        telemetry.track_counter("deep.load_stored_range.calls", 1)
        telemetry.track_counter("deep.load_stored_range.messages", len(rows))
        telemetry.track_duration("deep.load_stored_range.total", perf_counter() - started_at)
        return rows

    def _load_stored_messages_by_ids(self, chat_id: int, message_ids: List[int]) -> Optional[Dict[int, MessageData]]:
        getter = getattr(self.storage, "get_messages_by_ids", None)
        if not callable(getter):
            return None
        try:
            result = getter(chat_id, message_ids)
        except TypeError:
            return None
        if not isinstance(result, list):
            return None
        return {message.message_id: message for message in result}

    def _load_stored_replies(self, chat_id: int, reply_to_ids: Iterable[int]) -> List[MessageData]:
        getter = getattr(self.storage, "get_messages_replying_to", None)
        if not callable(getter):
            return []
        started_at = perf_counter()
        try:
            result = getter(chat_id, list(reply_to_ids))
        except TypeError:
            return []
        rows = result if isinstance(result, list) else []
        telemetry.track_counter("deep.load_stored_replies.calls", 1)
        telemetry.track_counter("deep.load_stored_replies.messages", len(rows))
        telemetry.track_duration("deep.load_stored_replies.total", perf_counter() - started_at)
        return rows

    def _calculate_ranges(self, ids: List[int], before_ids: int, after_ids: int) -> List[Tuple[int, int]]:
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

    def _scan_before_ids(self, round_number: int, window_size: int) -> int:
        if round_number == 1:
            return max(8, window_size * 3)
        return max(12, window_size * 4)

    def _scan_after_ids(self, round_number: int, window_size: int, max_cluster: int) -> int:
        if round_number == 1:
            return max(60, window_size * 15, max_cluster * 6)
        return max(90, window_size * 20, max_cluster * 8)

    def _with_cluster(self, msg: MessageData, cluster_id: str) -> MessageData:
        return replace(msg, context_group_id=cluster_id)

    async def extract_context(
        self,
        entity: Any,
        target_msg: MessageData,
        window_size: int = 5,
        max_cluster: int = 10,
    ) -> str:
        self.reset()
        cluster_id = target_msg.context_group_id or str(uuid.uuid4())
        clustered = self._with_cluster(target_msg, cluster_id)
        await self.extract_batch_context(
            entity,
            [clustered],
            window_size=window_size,
            max_cluster=max_cluster,
            recursive_depth=3,
        )
        return cluster_id
