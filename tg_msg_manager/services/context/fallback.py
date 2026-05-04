from datetime import timedelta
from time import perf_counter
from typing import Any, List, Optional

from ...core.models.message import MessageData
from ...core.telemetry import telemetry
from .clustering import ContextClusterAssembler
from .models import CandidatePoolRequest, ContextCandidate, ContextClusterState
from .resolvers import CandidatePoolResolver


class TimeFallbackResolver:
    def __init__(
        self,
        *,
        candidate_pool_resolver: CandidatePoolResolver,
        cluster_assembler: ContextClusterAssembler,
        processed_ids,
    ):
        self.candidate_pool_resolver = candidate_pool_resolver
        self.cluster_assembler = cluster_assembler
        self.processed_ids = processed_ids

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
            local_candidates = await self.candidate_pool_resolver.fetch_candidate_pool(
                entity=entity,
                request=CandidatePoolRequest(
                    chat_id=chat_id,
                    anchor_ids=[cluster.target.message.message_id],
                    scan_before=max(4, window_size * 2),
                    scan_after=max(6, window_size * 3),
                ),
            )
            for norm in self.select_time_fallback(
                cluster,
                local_candidates,
                window_size=window_size,
                max_cluster=max_cluster,
            ):
                if self.cluster_assembler.add_to_cluster(
                    cluster,
                    norm,
                    "time_fallback",
                    max_cluster=max_cluster,
                    structural=False,
                ):
                    additions.append(
                        self.cluster_assembler.with_cluster(
                            norm.message, cluster.cluster_id
                        )
                    )

        saved_count = await flush_new_messages(
            additions, target_id=target_id, on_progress=on_progress
        )
        telemetry.track_counter("deep.time_fallback.clusters", len(fallback_clusters))
        telemetry.track_counter("deep.time_fallback.saved_messages", saved_count)
        telemetry.track_duration(
            "deep.time_fallback.total", perf_counter() - started_at
        )
        return saved_count

    def select_time_fallback(
        self,
        cluster: ContextClusterState,
        candidates: List[ContextCandidate],
        *,
        window_size: int,
        max_cluster: int,
    ) -> List[ContextCandidate]:
        ordered = sorted(
            candidates,
            key=lambda norm: (norm.message.timestamp, norm.message.message_id),
        )
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
        selected: List[ContextCandidate] = []

        def walk(direction: int, limit_count: int, max_total_delta: timedelta) -> None:
            last = cluster.target
            added = 0
            skipped = 0
            idx = target_index + direction
            while (
                0 <= idx < len(ordered)
                and added < limit_count
                and cluster.remaining_slots(max_cluster) > len(selected)
            ):
                norm = ordered[idx]
                idx += direction
                if (
                    norm.key in cluster.messages
                    or norm.key in self.processed_ids
                    or norm.message.is_service
                ):
                    skipped += 1
                    if skipped >= 2:
                        break
                    continue

                current_gap = abs(norm.message.timestamp - last.message.timestamp)
                total_delta = abs(
                    norm.message.timestamp - cluster.target.message.timestamp
                )
                if current_gap > max_gap or total_delta > max_total_delta:
                    break

                selected.append(norm)
                last = norm
                added += 1
                skipped = 0

        walk(-1, max_before, max_total_before)
        walk(1, max_after, max_total_after)
        selected.sort(
            key=lambda norm: (norm.message.timestamp, norm.message.message_id)
        )
        return selected
