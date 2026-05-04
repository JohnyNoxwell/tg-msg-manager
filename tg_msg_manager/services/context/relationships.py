from typing import Dict, List, Optional, Set, Tuple

from .models import ContextCandidate, ContextClusterState


class ChildReplyResolver:
    @staticmethod
    def candidate_clusters(
        *,
        candidate: ContextCandidate,
        round_number: int,
        target_index: Dict[int, List[ContextClusterState]],
        structural_index: Dict[int, List[ContextClusterState]],
    ) -> List[ContextClusterState]:
        ordered: List[ContextClusterState] = []
        seen_cluster_ids: Set[str] = set()

        def append_matches(matches: List[ContextClusterState]) -> None:
            for cluster in matches:
                if cluster.cluster_id in seen_cluster_ids:
                    continue
                seen_cluster_ids.add(cluster.cluster_id)
                ordered.append(cluster)

        if candidate.reply_to_id is None:
            return ordered

        append_matches(target_index.get(candidate.reply_to_id, []))
        if round_number >= 2:
            append_matches(structural_index.get(candidate.reply_to_id, []))
        return ordered

    @staticmethod
    def detect_relation(
        *,
        cluster: ContextClusterState,
        candidate: ContextCandidate,
        round_number: int,
    ) -> Tuple[Optional[str], bool]:
        structural_ids = {
            norm.message.message_id for norm in cluster.structural_messages()
        }
        target_id = cluster.target.message.message_id

        if candidate.reply_to_id == target_id:
            return "reply_to_target", True

        if round_number >= 2 and candidate.reply_to_id in structural_ids:
            return "reply_chain", True

        return None, False


class ThreadTopicResolver:
    @staticmethod
    def topic_clusters(
        *,
        candidate: ContextCandidate,
        round_number: int,
        topic_index: Dict[int, List[ContextClusterState]],
    ) -> List[ContextClusterState]:
        if round_number < 2 or candidate.topic_id is None:
            return []
        return list(topic_index.get(candidate.topic_id, []))

    @staticmethod
    def is_topic_mismatch(
        cluster: ContextClusterState,
        norm: ContextCandidate,
    ) -> bool:
        if cluster.topic_id is None or norm.topic_id is None:
            return False
        return cluster.topic_id != norm.topic_id

    @staticmethod
    def detect_relation(
        *,
        cluster: ContextClusterState,
        candidate: ContextCandidate,
        round_number: int,
    ) -> Tuple[Optional[str], bool]:
        if (
            round_number >= 2
            and cluster.topic_id
            and candidate.topic_id == cluster.topic_id
        ):
            return "same_topic", False
        return None, False
