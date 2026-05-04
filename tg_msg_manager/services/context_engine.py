import asyncio
import uuid
from time import perf_counter
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from ..core.models.message import MessageData
from ..core.telemetry import telemetry
from ..core.telegram.interface import TelegramClientInterface
from ..infrastructure.storage.interface import ContextStorage
from .context import (
    CandidatePoolRequest,
    CandidatePoolResolver,
    ContextCandidate,
    ContextClusterAssembler,
    ContextClusterState,
    LiveContextResolver,
    MessageKey,
    ParentLookupRequest,
    ParentReplyResolver,
    StorageContextResolver,
    TimeFallbackResolver,
)

_NormalizedContextMessage = ContextCandidate
_ClusterState = ContextClusterState


class DeepModeEngine:
    """
    Deep mode that prefers Telegram's structural links over local message-id windows.
    """

    def __init__(
        self,
        client: TelegramClientInterface,
        storage: ContextStorage,
        max_concurrency: int = 15,
    ):
        self.client = client
        self.storage = storage
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self._processed_ids: Set[MessageKey] = set()
        self.storage_resolver = StorageContextResolver(
            storage=storage,
            normalize_message=self._normalize_message,
        )
        self.live_resolver = LiveContextResolver(
            client=client,
            semaphore=self.semaphore,
            normalize_message=self._normalize_message,
        )
        self.cluster_assembler = ContextClusterAssembler(
            processed_ids=self._processed_ids,
            message_key=self._message_key,
            normalize_message=self._normalize_message,
        )
        self.parent_reply_resolver = ParentReplyResolver(
            storage_resolver=self.storage_resolver,
            live_resolver=self.live_resolver,
            message_key=self._message_key,
            processed_ids=self._processed_ids,
        )
        self.candidate_pool_resolver = CandidatePoolResolver(
            storage_resolver=self.storage_resolver,
            live_resolver=self.live_resolver,
            normalize_message=self._normalize_message,
        )
        self.time_fallback_resolver = TimeFallbackResolver(
            candidate_pool_resolver=self.candidate_pool_resolver,
            cluster_assembler=self.cluster_assembler,
            processed_ids=self._processed_ids,
        )

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
        telemetry.track_duration(
            "deep.extract_batch.total", perf_counter() - started_at
        )
        return saved_count

    def _initialize_clusters(
        self, target_messages: List[MessageData]
    ) -> List[_ClusterState]:
        return self.cluster_assembler.initialize_clusters(target_messages)

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
        anchors_by_cluster = self._build_anchors_by_cluster(
            clusters, round_number, max_cluster
        )
        if not anchors_by_cluster:
            return 0

        round_started = perf_counter()
        saved_count = await self._save_round_parent_messages(
            entity,
            chat_id,
            clusters,
            anchors_by_cluster,
            target_id=target_id,
            max_cluster=max_cluster,
            on_progress=on_progress,
        )
        saved_count += await self._save_round_candidate_messages(
            entity,
            chat_id,
            clusters,
            anchors_by_cluster,
            target_id=target_id,
            window_size=window_size,
            round_number=round_number,
            max_cluster=max_cluster,
            on_progress=on_progress,
        )
        telemetry.track_counter(
            f"deep.round_{round_number}.clusters", len(anchors_by_cluster)
        )
        telemetry.track_counter(
            f"deep.round_{round_number}.saved_messages", saved_count
        )
        telemetry.track_duration(
            f"deep.round_{round_number}.total", perf_counter() - round_started
        )
        return saved_count

    async def _save_round_parent_messages(
        self,
        entity: Any,
        chat_id: int,
        clusters: List[_ClusterState],
        anchors_by_cluster: Dict[str, List[_NormalizedContextMessage]],
        target_id: Optional[int],
        max_cluster: int,
        on_progress: Optional[Any],
    ) -> int:
        parents = await self._fetch_parent_messages(entity, chat_id, anchors_by_cluster)
        parent_additions = self._associate_parents(
            clusters,
            anchors_by_cluster,
            parents,
            max_cluster=max_cluster,
        )
        return await self._flush_new_messages(
            parent_additions, target_id=target_id, on_progress=on_progress
        )

    async def _save_round_candidate_messages(
        self,
        entity: Any,
        chat_id: int,
        clusters: List[_ClusterState],
        anchors_by_cluster: Dict[str, List[_NormalizedContextMessage]],
        target_id: Optional[int],
        window_size: int,
        round_number: int,
        max_cluster: int,
        on_progress: Optional[Any],
    ) -> int:
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
        return await self._flush_new_messages(
            candidate_additions, target_id=target_id, on_progress=on_progress
        )

    def _build_anchors_by_cluster(
        self,
        clusters: List[_ClusterState],
        round_number: int,
        max_cluster: int,
    ) -> Dict[str, List[_NormalizedContextMessage]]:
        return self.cluster_assembler.build_anchors_by_cluster(
            clusters,
            round_number,
            max_cluster,
        )

    def _round_anchors(
        self,
        cluster: _ClusterState,
        round_number: int,
    ) -> List[_NormalizedContextMessage]:
        return self.cluster_assembler.round_anchors(cluster, round_number)

    async def _fetch_parent_messages(
        self,
        entity: Any,
        chat_id: int,
        anchors_by_cluster: Dict[str, List[_NormalizedContextMessage]],
    ) -> Dict[int, _NormalizedContextMessage]:
        return await self.parent_reply_resolver.fetch_parent_messages(
            entity=entity,
            request=ParentLookupRequest(
                chat_id=chat_id,
                anchors_by_cluster=anchors_by_cluster,
            ),
        )

    def _collect_needed_parent_ids(
        self,
        chat_id: int,
        anchors_by_cluster: Dict[str, List[_NormalizedContextMessage]],
    ) -> List[int]:
        return self.parent_reply_resolver.collect_needed_parent_ids(
            chat_id=chat_id,
            anchors_by_cluster=anchors_by_cluster,
        )

    async def _load_parent_messages_from_storage(
        self,
        chat_id: int,
        parent_ids: List[int],
    ) -> Tuple[Dict[int, _NormalizedContextMessage], int, List[int]]:
        return await self.storage_resolver.load_parent_messages_by_ids(
            chat_id=chat_id,
            parent_ids=parent_ids,
        )

    async def _fetch_live_parent_messages(
        self,
        entity: Any,
        missing_ids: List[int],
    ) -> Dict[int, _NormalizedContextMessage]:
        return await self.live_resolver.fetch_parent_messages_by_ids(
            entity=entity,
            missing_ids=missing_ids,
        )

    def _associate_parents(
        self,
        clusters: List[_ClusterState],
        anchors_by_cluster: Dict[str, List[_NormalizedContextMessage]],
        parents: Dict[int, _NormalizedContextMessage],
        max_cluster: int,
    ) -> List[MessageData]:
        return self.cluster_assembler.associate_parents(
            clusters=clusters,
            anchors_by_cluster=anchors_by_cluster,
            parents=parents,
            max_cluster=max_cluster,
        )

    async def _fetch_candidate_pool(
        self,
        entity: Any,
        chat_id: int,
        anchor_ids: List[int],
        scan_before: int,
        scan_after: int,
    ) -> List[_NormalizedContextMessage]:
        return await self.candidate_pool_resolver.fetch_candidate_pool(
            entity=entity,
            request=CandidatePoolRequest(
                chat_id=chat_id,
                anchor_ids=anchor_ids,
                scan_before=scan_before,
                scan_after=scan_after,
            ),
        )

    async def _collect_range_candidates(
        self,
        entity: Any,
        chat_id: int,
        start_id: int,
        end_id: int,
        stored_reply_count: int,
    ) -> List[_NormalizedContextMessage]:
        return await self.candidate_pool_resolver.collect_range_candidates(
            entity=entity,
            chat_id=chat_id,
            start_id=start_id,
            end_id=end_id,
            stored_reply_count=stored_reply_count,
        )

    async def _fetch_live_range_fill(
        self,
        entity: Any,
        *,
        start_id: int,
        end_id: int,
        range_width: int,
        stored_count: int,
        missing_ids: List[int],
        stored_reply_count: int,
    ) -> List[MessageData]:
        return await self.candidate_pool_resolver.fetch_live_range_fill(
            entity=entity,
            start_id=start_id,
            end_id=end_id,
            range_width=range_width,
            stored_count=stored_count,
            missing_ids=missing_ids,
            stored_reply_count=stored_reply_count,
        )

    def _merge_message_candidates(
        self,
        collected: List[_NormalizedContextMessage],
        seen: Set[MessageKey],
        messages: Iterable[MessageData],
    ) -> None:
        self.candidate_pool_resolver.merge_message_candidates(
            collected,
            seen,
            messages,
            semantic_source="range_scan",
            retrieval_source="compat",
        )

    @staticmethod
    def _merge_normalized_candidates(
        collected: List[_NormalizedContextMessage],
        seen: Set[MessageKey],
        messages: Iterable[_NormalizedContextMessage],
    ) -> None:
        CandidatePoolResolver.merge_normalized_candidates(collected, seen, messages)

    @staticmethod
    def _append_normalized_candidate(
        collected: List[_NormalizedContextMessage],
        seen: Set[MessageKey],
        norm: _NormalizedContextMessage,
    ) -> None:
        CandidatePoolResolver.append_normalized_candidate(collected, seen, norm)

    @staticmethod
    def _should_selective_live_fill(
        range_width: int,
        stored_count: int,
        missing_count: int,
        stored_reply_count: int = 0,
    ) -> bool:
        return CandidatePoolResolver.should_selective_live_fill(
            range_width,
            stored_count,
            missing_count,
            stored_reply_count=stored_reply_count,
        )

    @staticmethod
    def _should_compact_live_fill(
        range_width: int,
        stored_count: int,
        missing_ids: List[int],
    ) -> bool:
        return CandidatePoolResolver.should_compact_live_fill(
            range_width,
            stored_count,
            missing_ids,
        )

    @staticmethod
    def _build_missing_subranges(
        missing_ids: List[int],
        pad_before: int = 1,
        pad_after: int = 2,
        merge_gap: int = 3,
    ) -> List[Tuple[int, int]]:
        return CandidatePoolResolver.build_missing_subranges(
            missing_ids,
            pad_before=pad_before,
            pad_after=pad_after,
            merge_gap=merge_gap,
        )

    @staticmethod
    def _track_range_coverage(
        range_width: int, stored_count: int, missing_count: int
    ) -> None:
        CandidatePoolResolver.track_range_coverage(
            range_width,
            stored_count,
            missing_count,
        )

    def _associate_candidates(
        self,
        clusters: List[_ClusterState],
        candidates: List[_NormalizedContextMessage],
        round_number: int,
        max_cluster: int,
    ) -> List[MessageData]:
        return self.cluster_assembler.associate_candidates(
            clusters=clusters,
            candidates=candidates,
            round_number=round_number,
            max_cluster=max_cluster,
        )

    def _build_candidate_indexes(
        self,
        clusters: List[_ClusterState],
        round_number: int,
        max_cluster: int,
    ) -> Tuple[
        Dict[int, List[_ClusterState]],
        Dict[int, List[_ClusterState]],
        Dict[int, List[_ClusterState]],
    ]:
        return self.cluster_assembler.build_candidate_indexes(
            clusters,
            round_number=round_number,
            max_cluster=max_cluster,
        )

    def _candidate_clusters(
        self,
        candidate: _NormalizedContextMessage,
        round_number: int,
        target_index: Dict[int, List[_ClusterState]],
        structural_index: Dict[int, List[_ClusterState]],
        topic_index: Dict[int, List[_ClusterState]],
    ) -> List[_ClusterState]:
        return self.cluster_assembler.candidate_clusters(
            candidate,
            round_number=round_number,
            target_index=target_index,
            structural_index=structural_index,
            topic_index=topic_index,
        )

    def _detect_relation(
        self,
        cluster: _ClusterState,
        candidate: _NormalizedContextMessage,
        round_number: int,
    ) -> Tuple[Optional[str], bool]:
        return self.cluster_assembler.detect_relation(
            cluster,
            candidate,
            round_number,
        )

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
        return await self.time_fallback_resolver.apply_time_fallback(
            entity=entity,
            chat_id=chat_id,
            clusters=clusters,
            target_id=target_id,
            window_size=window_size,
            max_cluster=max_cluster,
            on_progress=on_progress,
            flush_new_messages=self._flush_new_messages,
        )

    def _select_time_fallback(
        self,
        cluster: _ClusterState,
        candidates: List[_NormalizedContextMessage],
        window_size: int,
        max_cluster: int,
    ) -> List[_NormalizedContextMessage]:
        return self.time_fallback_resolver.select_time_fallback(
            cluster,
            candidates,
            window_size=window_size,
            max_cluster=max_cluster,
        )

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
        return self.cluster_assembler.add_to_cluster(
            cluster,
            norm,
            reason,
            max_cluster=max_cluster,
            structural=structural,
        )

    def _is_topic_mismatch(
        self, cluster: _ClusterState, norm: _NormalizedContextMessage
    ) -> bool:
        return self.cluster_assembler.is_topic_mismatch(cluster, norm)

    def _normalize_message(
        self,
        msg: MessageData,
        *,
        semantic_source: str = "normalized",
        retrieval_source: str = "unknown",
    ) -> _NormalizedContextMessage:
        raw = msg.raw_payload or {}
        reply_to = raw.get("reply_to") if isinstance(raw, dict) else {}
        if not isinstance(reply_to, dict):
            reply_to = {}

        reply_to_id = msg.reply_to_id or reply_to.get("reply_to_msg_id")
        reply_to_top_id = reply_to.get("reply_to_top_id")
        forum_topic = bool(reply_to.get("forum_topic"))

        return ContextCandidate(
            message=msg,
            reply_to_id=reply_to_id,
            reply_to_top_id=reply_to_top_id,
            forum_topic=forum_topic,
            semantic_source=semantic_source,
            retrieval_source=retrieval_source,
        )

    async def _fetch_range(
        self, entity: Any, start_id: int, end_id: int
    ) -> List[MessageData]:
        return await self.live_resolver.fetch_range(
            entity=entity,
            start_id=start_id,
            end_id=end_id,
            retrieval_source="compat",
        )

    async def _fetch_ranges(
        self, entity: Any, ranges: List[Tuple[int, int]]
    ) -> List[MessageData]:
        return await self.live_resolver.fetch_ranges(
            entity=entity,
            ranges=ranges,
            retrieval_source="compat",
        )

    async def _fetch_missing_ids(
        self, entity: Any, message_ids: List[int]
    ) -> List[MessageData]:
        return await self.live_resolver.fetch_missing_ids(
            entity=entity,
            message_ids=message_ids,
        )

    def _load_stored_range(
        self, chat_id: int, start_id: int, end_id: int
    ) -> List[MessageData]:
        return self.storage_resolver.load_stored_range(
            chat_id=chat_id,
            start_id=start_id,
            end_id=end_id,
        )

    def _load_stored_messages_by_ids(
        self, chat_id: int, message_ids: List[int]
    ) -> Optional[Dict[int, MessageData]]:
        return self.storage_resolver.load_stored_messages_by_ids(chat_id, message_ids)

    def _load_stored_replies(
        self, chat_id: int, reply_to_ids: Iterable[int]
    ) -> List[MessageData]:
        return self.storage_resolver.load_stored_replies(
            chat_id=chat_id,
            reply_to_ids=reply_to_ids,
        )

    def _calculate_ranges(
        self, ids: List[int], before_ids: int, after_ids: int
    ) -> List[Tuple[int, int]]:
        return self.candidate_pool_resolver.calculate_ranges(
            ids,
            before_ids=before_ids,
            after_ids=after_ids,
        )

    def _scan_before_ids(self, round_number: int, window_size: int) -> int:
        if round_number == 1:
            return max(8, window_size * 3)
        return max(12, window_size * 4)

    def _scan_after_ids(
        self, round_number: int, window_size: int, max_cluster: int
    ) -> int:
        if round_number == 1:
            return max(60, window_size * 15, max_cluster * 6)
        return max(90, window_size * 20, max_cluster * 8)

    def _with_cluster(self, msg: MessageData, cluster_id: str) -> MessageData:
        return self.cluster_assembler.with_cluster(msg, cluster_id)

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
