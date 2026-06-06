from typing import Any, List, Optional

from ...core.models.message import MessageData
from .models import (
    CandidatePoolRequest,
    ContextCandidate,
    ContextClusterState,
    ParentLookupRequest,
)


class ContextRoundDependencies:
    def __init__(
        self,
        *,
        storage: Any,
        cluster_assembler: Any,
        parent_reply_resolver: Any,
        candidate_pool_resolver: Any,
        time_fallback_resolver: Any,
    ):
        self.storage = storage
        self.cluster_assembler = cluster_assembler
        self.parent_reply_resolver = parent_reply_resolver
        self.candidate_pool_resolver = candidate_pool_resolver
        self.time_fallback_resolver = time_fallback_resolver

    def initialize_clusters(
        self, target_messages: List[MessageData]
    ) -> List[ContextClusterState]:
        return self.cluster_assembler.initialize_clusters(target_messages)

    def build_anchors_by_cluster(
        self,
        clusters: List[ContextClusterState],
        round_number: int,
        max_cluster: int,
    ) -> dict[str, List[ContextCandidate]]:
        return self.cluster_assembler.build_anchors_by_cluster(
            clusters, round_number, max_cluster
        )

    async def fetch_parent_messages(
        self,
        *,
        entity: Any,
        chat_id: int,
        anchors_by_cluster: dict[str, List[ContextCandidate]],
    ) -> dict[int, ContextCandidate]:
        return await self.parent_reply_resolver.fetch_parent_messages(
            entity=entity,
            request=ParentLookupRequest(
                chat_id=chat_id,
                anchors_by_cluster=anchors_by_cluster,
            ),
        )

    def associate_parents(
        self,
        *,
        clusters: List[ContextClusterState],
        anchors_by_cluster: dict[str, List[ContextCandidate]],
        parents: dict[int, ContextCandidate],
        max_cluster: int,
    ) -> List[MessageData]:
        return self.cluster_assembler.associate_parents(
            clusters=clusters,
            anchors_by_cluster=anchors_by_cluster,
            parents=parents,
            max_cluster=max_cluster,
        )

    async def fetch_candidate_pool(
        self,
        *,
        entity: Any,
        chat_id: int,
        anchor_ids: List[int],
        scan_before: int,
        scan_after: int,
    ) -> List[ContextCandidate]:
        return await self.candidate_pool_resolver.fetch_candidate_pool(
            entity=entity,
            request=CandidatePoolRequest(
                chat_id=chat_id,
                anchor_ids=anchor_ids,
                scan_before=scan_before,
                scan_after=scan_after,
            ),
        )

    def associate_candidates(
        self,
        *,
        clusters: List[ContextClusterState],
        candidates: List[ContextCandidate],
        round_number: int,
        max_cluster: int,
    ) -> List[MessageData]:
        return self.cluster_assembler.associate_candidates(
            clusters=clusters,
            candidates=candidates,
            round_number=round_number,
            max_cluster=max_cluster,
        )

    @staticmethod
    def scan_before_ids(round_number: int, window_size: int) -> int:
        if round_number == 1:
            return max(8, window_size * 3)
        return max(12, window_size * 4)

    @staticmethod
    def scan_after_ids(round_number: int, window_size: int, max_cluster: int) -> int:
        if round_number == 1:
            return max(60, window_size * 15, max_cluster * 6)
        return max(90, window_size * 20, max_cluster * 8)

    async def apply_time_fallback(
        self,
        *,
        entity: Any,
        chat_id: int,
        clusters: List[ContextClusterState],
        target_id: Optional[int],
        window_size: int,
        max_cluster: int,
        on_progress: Optional[Any],
        flush_new_messages,
    ) -> int:
        return await self.time_fallback_resolver.apply_time_fallback(
            entity=entity,
            chat_id=chat_id,
            clusters=clusters,
            target_id=target_id,
            window_size=window_size,
            max_cluster=max_cluster,
            on_progress=on_progress,
            flush_new_messages=flush_new_messages,
        )

    async def save_messages(
        self,
        messages: List[MessageData],
        *,
        target_id: Optional[int],
    ) -> int:
        return await self.storage.save_messages(
            messages, target_id=target_id, flush=False
        )
