import logging
import uuid
from dataclasses import replace
from typing import Callable, Dict, List, Optional, Set, Tuple

from ...core.models.message import MessageData
from ...core.telemetry import telemetry
from .models import ContextCandidate, ContextClusterState, MessageKey
from .relationships import ChildReplyResolver, ThreadTopicResolver

logger = logging.getLogger(__name__)


class ContextClusterAssembler:
    def __init__(
        self,
        *,
        processed_ids: Set[MessageKey],
        message_key: Callable[[int, int], MessageKey],
        normalize_message: Callable[..., ContextCandidate],
    ):
        self.processed_ids = processed_ids
        self.message_key = message_key
        self.normalize_message = normalize_message
        self.child_reply_resolver = ChildReplyResolver()
        self.thread_topic_resolver = ThreadTopicResolver()

    @staticmethod
    def with_cluster(msg: MessageData, cluster_id: str) -> MessageData:
        return replace(msg, context_group_id=cluster_id)

    def initialize_clusters(
        self,
        target_messages: List[MessageData],
    ) -> List[ContextClusterState]:
        clusters: List[ContextClusterState] = []
        for msg in target_messages:
            key = self.message_key(msg.chat_id, msg.message_id)
            if key in self.processed_ids:
                continue

            cluster_id = msg.context_group_id or str(uuid.uuid4())
            clustered = self.with_cluster(msg, cluster_id)
            normalized = self.normalize_message(
                clustered,
                semantic_source="target",
                retrieval_source="input",
            )
            cluster = ContextClusterState(cluster_id=cluster_id, target=normalized)
            cluster.messages[normalized.key] = normalized
            cluster.reasons[normalized.key] = "self"
            clusters.append(cluster)
            self.processed_ids.add(normalized.key)
        return clusters

    def build_anchors_by_cluster(
        self,
        clusters: List[ContextClusterState],
        round_number: int,
        max_cluster: int,
    ) -> Dict[str, List[ContextCandidate]]:
        anchors_by_cluster: Dict[str, List[ContextCandidate]] = {}
        skipped_empty = 0
        for cluster in clusters:
            if cluster.remaining_slots(max_cluster) <= 0:
                continue

            anchors = self.round_anchors(cluster, round_number)
            if anchors:
                anchors_by_cluster[cluster.cluster_id] = anchors
            else:
                skipped_empty += 1
        telemetry.track_counter(
            f"deep.round_{round_number}.anchor_clusters", len(anchors_by_cluster)
        )
        if skipped_empty:
            telemetry.track_counter(
                f"deep.round_{round_number}.skipped_empty_clusters", skipped_empty
            )
        return anchors_by_cluster

    @staticmethod
    def round_anchors(
        cluster: ContextClusterState,
        round_number: int,
    ) -> List[ContextCandidate]:
        if round_number == 1:
            return [cluster.target]
        structural = [
            norm
            for norm in cluster.structural_messages()
            if norm.key != cluster.target.key
        ]
        if cluster.topic_id is not None:
            return [cluster.target, *structural]
        return structural

    def associate_parents(
        self,
        *,
        clusters: List[ContextClusterState],
        anchors_by_cluster: Dict[str, List[ContextCandidate]],
        parents: Dict[int, ContextCandidate],
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
                if self.add_to_cluster(
                    cluster_state,
                    parent,
                    "parent_reply",
                    max_cluster=max_cluster,
                    structural=True,
                ):
                    additions.append(
                        self.with_cluster(parent.message, cluster_state.cluster_id)
                    )
        return additions

    def associate_candidates(
        self,
        *,
        clusters: List[ContextClusterState],
        candidates: List[ContextCandidate],
        round_number: int,
        max_cluster: int,
    ) -> List[MessageData]:
        additions: List[MessageData] = []
        target_index, structural_index, topic_index = self.build_candidate_indexes(
            clusters,
            round_number=round_number,
            max_cluster=max_cluster,
        )
        for candidate in candidates:
            if candidate.message.is_service:
                continue
            if candidate.key in self.processed_ids:
                continue

            for cluster in self.candidate_clusters(
                candidate,
                round_number=round_number,
                target_index=target_index,
                structural_index=structural_index,
                topic_index=topic_index,
            ):
                if cluster.remaining_slots(max_cluster) <= 0:
                    continue
                if candidate.key in cluster.messages:
                    continue

                reason, structural = self.detect_relation(
                    cluster, candidate, round_number
                )
                if not reason:
                    continue

                if self.add_to_cluster(
                    cluster,
                    candidate,
                    reason,
                    max_cluster=max_cluster,
                    structural=structural,
                ):
                    additions.append(
                        self.with_cluster(candidate.message, cluster.cluster_id)
                    )
                    break
        return additions

    def build_candidate_indexes(
        self,
        clusters: List[ContextClusterState],
        *,
        round_number: int,
        max_cluster: int,
    ) -> Tuple[
        Dict[int, List[ContextClusterState]],
        Dict[int, List[ContextClusterState]],
        Dict[int, List[ContextClusterState]],
    ]:
        target_index: Dict[int, List[ContextClusterState]] = {}
        structural_index: Dict[int, List[ContextClusterState]] = {}
        topic_index: Dict[int, List[ContextClusterState]] = {}

        for cluster in clusters:
            if cluster.remaining_slots(max_cluster) <= 0:
                continue

            target_index.setdefault(cluster.target.message.message_id, []).append(
                cluster
            )
            if round_number < 2:
                continue

            for norm in cluster.structural_messages():
                structural_index.setdefault(norm.message.message_id, []).append(cluster)
            if cluster.topic_id:
                topic_index.setdefault(cluster.topic_id, []).append(cluster)

        return target_index, structural_index, topic_index

    def candidate_clusters(
        self,
        candidate: ContextCandidate,
        *,
        round_number: int,
        target_index: Dict[int, List[ContextClusterState]],
        structural_index: Dict[int, List[ContextClusterState]],
        topic_index: Dict[int, List[ContextClusterState]],
    ) -> List[ContextClusterState]:
        ordered = self.child_reply_resolver.candidate_clusters(
            candidate=candidate,
            round_number=round_number,
            target_index=target_index,
            structural_index=structural_index,
        )
        seen_cluster_ids = {cluster.cluster_id for cluster in ordered}
        for cluster in self.thread_topic_resolver.topic_clusters(
            candidate=candidate,
            round_number=round_number,
            topic_index=topic_index,
        ):
            if cluster.cluster_id in seen_cluster_ids:
                continue
            seen_cluster_ids.add(cluster.cluster_id)
            ordered.append(cluster)
        return ordered

    def detect_relation(
        self,
        cluster: ContextClusterState,
        candidate: ContextCandidate,
        round_number: int,
    ) -> Tuple[Optional[str], bool]:
        if candidate.key == cluster.target.key:
            return None, False
        if self.is_topic_mismatch(cluster, candidate):
            return None, False

        reason, structural = self.child_reply_resolver.detect_relation(
            cluster=cluster,
            candidate=candidate,
            round_number=round_number,
        )
        if reason:
            return reason, structural
        return self.thread_topic_resolver.detect_relation(
            cluster=cluster,
            candidate=candidate,
            round_number=round_number,
        )

    def add_to_cluster(
        self,
        cluster: ContextClusterState,
        norm: ContextCandidate,
        reason: str,
        *,
        max_cluster: int,
        structural: bool,
    ) -> bool:
        if norm.key in cluster.messages or norm.key in self.processed_ids:
            return False
        if norm.message.is_service:
            return False
        if cluster.remaining_slots(max_cluster) <= 0:
            return False
        if self.is_topic_mismatch(cluster, norm):
            return False

        cluster.messages[norm.key] = norm
        cluster.reasons[norm.key] = reason
        if structural:
            cluster.structural_count += 1
        self.processed_ids.add(norm.key)
        logger.debug(
            "Deep cluster %s added message %s via %s (%s/%s)",
            cluster.cluster_id,
            norm.message.message_id,
            reason,
            norm.semantic_source,
            norm.retrieval_source,
        )
        return True

    def is_topic_mismatch(
        self,
        cluster: ContextClusterState,
        norm: ContextCandidate,
    ) -> bool:
        return self.thread_topic_resolver.is_topic_mismatch(cluster, norm)
