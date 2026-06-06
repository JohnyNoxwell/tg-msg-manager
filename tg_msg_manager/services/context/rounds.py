from time import perf_counter
from typing import Any, List, Optional

from ...core.models.message import MessageData
from ...core.telemetry import telemetry
from .round_dependencies import ContextRoundDependencies
from .scope_policy import ContextScopePolicy


class DeepContextRoundRunner:
    def __init__(self, dependencies: ContextRoundDependencies):
        self.dependencies = dependencies

    async def extract_batch_context(
        self,
        entity: Any,
        target_messages: List[MessageData],
        *,
        target_id: Optional[int] = None,
        window_size: int = 3,
        max_cluster: int = 20,
        recursive_depth: int = 3,
        on_progress: Optional[Any] = None,
    ) -> int:
        if not target_messages or recursive_depth <= 0:
            return 0

        started_at = perf_counter()
        scope_policy = ContextScopePolicy(
            window_size=window_size,
            max_cluster=max_cluster,
            recursive_depth=recursive_depth,
        )
        clusters = self.dependencies.initialize_clusters(target_messages)
        if not clusters:
            return 0

        telemetry.track_counter("deep.extract_batch.calls", 1)
        telemetry.track_counter("deep.extract_batch.targets", len(target_messages))
        telemetry.track_counter("deep.extract_batch.clusters", len(clusters))
        await self.dependencies.save_messages(
            [cluster.target.message for cluster in clusters], target_id=target_id
        )
        saved_count = len(clusters)
        if on_progress:
            await on_progress()

        chat_id = clusters[0].target.message.chat_id
        saved_count += await self._expand_structural_round(
            entity=entity,
            chat_id=chat_id,
            clusters=clusters,
            target_id=target_id,
            window_size=scope_policy.window_size,
            max_cluster=scope_policy.max_cluster,
            round_number=1,
            on_progress=on_progress,
        )
        if scope_policy.active_depth >= 2:
            saved_count += await self._expand_structural_round(
                entity=entity,
                chat_id=chat_id,
                clusters=clusters,
                target_id=target_id,
                window_size=scope_policy.window_size,
                max_cluster=scope_policy.max_cluster,
                round_number=2,
                on_progress=on_progress,
            )
        if scope_policy.active_depth >= 3:
            saved_count += await self._apply_time_fallback(
                entity=entity,
                chat_id=chat_id,
                clusters=clusters,
                target_id=target_id,
                window_size=scope_policy.window_size,
                max_cluster=scope_policy.max_cluster,
                on_progress=on_progress,
            )
        telemetry.track_counter("deep.extract_batch.saved_messages", saved_count)
        telemetry.track_duration(
            "deep.extract_batch.total", perf_counter() - started_at
        )
        return saved_count

    async def _expand_structural_round(
        self,
        *,
        entity: Any,
        chat_id: int,
        clusters,
        target_id: Optional[int],
        window_size: int,
        max_cluster: int,
        round_number: int,
        on_progress: Optional[Any],
    ) -> int:
        anchors_by_cluster = self.dependencies.build_anchors_by_cluster(
            clusters, round_number, max_cluster
        )
        if not anchors_by_cluster:
            return 0

        round_started = perf_counter()
        saved_count = await self._save_round_parent_messages(
            entity=entity,
            chat_id=chat_id,
            clusters=clusters,
            anchors_by_cluster=anchors_by_cluster,
            target_id=target_id,
            max_cluster=max_cluster,
            on_progress=on_progress,
        )
        saved_count += await self._save_round_candidate_messages(
            entity=entity,
            chat_id=chat_id,
            clusters=clusters,
            anchors_by_cluster=anchors_by_cluster,
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
        *,
        entity: Any,
        chat_id: int,
        clusters,
        anchors_by_cluster,
        target_id: Optional[int],
        max_cluster: int,
        on_progress: Optional[Any],
    ) -> int:
        parents = await self.dependencies.fetch_parent_messages(
            entity=entity,
            chat_id=chat_id,
            anchors_by_cluster=anchors_by_cluster,
        )
        parent_additions = self.dependencies.associate_parents(
            clusters=clusters,
            anchors_by_cluster=anchors_by_cluster,
            parents=parents,
            max_cluster=max_cluster,
        )
        return await self._flush_new_messages(
            parent_additions, target_id=target_id, on_progress=on_progress
        )

    async def _save_round_candidate_messages(
        self,
        *,
        entity: Any,
        chat_id: int,
        clusters,
        anchors_by_cluster,
        target_id: Optional[int],
        window_size: int,
        round_number: int,
        max_cluster: int,
        on_progress: Optional[Any],
    ) -> int:
        candidate_messages = await self.dependencies.fetch_candidate_pool(
            entity=entity,
            chat_id=chat_id,
            anchor_ids=[
                anchor.message.message_id
                for anchors in anchors_by_cluster.values()
                for anchor in anchors
            ],
            scan_before=self.dependencies.scan_before_ids(round_number, window_size),
            scan_after=self.dependencies.scan_after_ids(
                round_number, window_size, max_cluster
            ),
        )
        candidate_additions = self.dependencies.associate_candidates(
            clusters=clusters,
            candidates=candidate_messages,
            round_number=round_number,
            max_cluster=max_cluster,
        )
        return await self._flush_new_messages(
            candidate_additions, target_id=target_id, on_progress=on_progress
        )

    async def _apply_time_fallback(
        self,
        *,
        entity: Any,
        chat_id: int,
        clusters,
        target_id: Optional[int],
        window_size: int,
        max_cluster: int,
        on_progress: Optional[Any],
    ) -> int:
        return await self.dependencies.apply_time_fallback(
            entity=entity,
            chat_id=chat_id,
            clusters=clusters,
            target_id=target_id,
            window_size=window_size,
            max_cluster=max_cluster,
            on_progress=on_progress,
            flush_new_messages=self._flush_new_messages,
        )

    async def _flush_new_messages(
        self,
        messages: List[MessageData],
        *,
        target_id: Optional[int],
        on_progress: Optional[Any],
    ) -> int:
        if not messages:
            return 0
        saved_count = await self.dependencies.save_messages(
            messages, target_id=target_id
        )
        if on_progress:
            await on_progress()
        return saved_count
