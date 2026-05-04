from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from ...core.models.message import MessageData

MessageKey = Tuple[int, int]
STRUCTURAL_REASONS = {"self", "parent_reply", "reply_to_target", "reply_chain"}


@dataclass(frozen=True)
class ContextCandidate:
    message: MessageData
    reply_to_id: Optional[int]
    reply_to_top_id: Optional[int]
    forum_topic: bool
    semantic_source: str
    retrieval_source: str

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
class ContextClusterState:
    cluster_id: str
    target: ContextCandidate
    messages: Dict[MessageKey, ContextCandidate] = field(default_factory=dict)
    reasons: Dict[MessageKey, str] = field(default_factory=dict)
    structural_count: int = 0

    @property
    def topic_id(self) -> Optional[int]:
        return self.target.topic_id

    def structural_messages(self) -> List[ContextCandidate]:
        return [
            norm
            for key, norm in self.messages.items()
            if self.reasons.get(key) in STRUCTURAL_REASONS
        ]

    def remaining_slots(self, max_cluster: int) -> int:
        if max_cluster <= 0:
            return 10**9
        return max(0, max_cluster - len(self.messages))


@dataclass(frozen=True)
class ParentLookupRequest:
    chat_id: int
    anchors_by_cluster: Dict[str, List[ContextCandidate]]


@dataclass(frozen=True)
class ParentLookupResult:
    normalized: Dict[int, ContextCandidate]
    storage_hits: int
    missing_ids: List[int]


@dataclass(frozen=True)
class CandidatePoolRequest:
    chat_id: int
    anchor_ids: List[int]
    scan_before: int
    scan_after: int
