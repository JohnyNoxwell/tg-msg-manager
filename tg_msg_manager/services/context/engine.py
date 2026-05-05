import asyncio
import uuid
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from ...core.models.message import MessageData
from ...core.telegram.interface import TelegramClientInterface
from ...infrastructure.storage.interface import ContextStorage
from .cluster_builder import ContextClusterBuilder
from .deduplicator import ProcessedMessageDeduplicator
from .fetchers import LiveContextResolver, StorageContextResolver
from .models import (
    CandidatePoolRequest,
    ContextCandidate,
    ContextClusterState,
    MessageKey,
    ParentLookupRequest,
)
from .neighbor_window_resolver import NeighborWindowResolver
from .reply_chain_resolver import ReplyChainResolver
from .rounds import DeepContextRoundRunner
from .scope_policy import ContextScopePolicy
from .fallback import TimeFallbackResolver


class DeepModeEngine:
    """
    Facade over dedicated context strategy modules.
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
        self.deduplicator = ProcessedMessageDeduplicator()
        self._processed_ids: Set[MessageKey] = self.deduplicator.processed_ids
        self.storage_resolver = StorageContextResolver(
            storage=storage,
            normalize_message=self._normalize_message,
        )
        self.live_resolver = LiveContextResolver(
            client=client,
            semaphore=self.semaphore,
            normalize_message=self._normalize_message,
        )
        self.cluster_assembler = ContextClusterBuilder(
            processed_ids=self._processed_ids,
            message_key=self._message_key,
            normalize_message=self._normalize_message,
        )
        self.parent_reply_resolver = ReplyChainResolver(
            storage_resolver=self.storage_resolver,
            live_resolver=self.live_resolver,
            message_key=self._message_key,
            processed_ids=self._processed_ids,
        )
        self.candidate_pool_resolver = NeighborWindowResolver(
            storage_resolver=self.storage_resolver,
            live_resolver=self.live_resolver,
            normalize_message=self._normalize_message,
        )
        self.time_fallback_resolver = TimeFallbackResolver(
            candidate_pool_resolver=self.candidate_pool_resolver,
            cluster_assembler=self.cluster_assembler,
            processed_ids=self._processed_ids,
        )
        self.round_runner = DeepContextRoundRunner(self)

    def reset(self):
        self.deduplicator.reset()

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
        return await self.round_runner.extract_batch_context(
            entity,
            target_messages,
            target_id=target_id,
            window_size=window_size,
            max_cluster=max_cluster,
            recursive_depth=recursive_depth,
            on_progress=on_progress,
        )

    def _initialize_clusters(
        self, target_messages: List[MessageData]
    ) -> List[ContextClusterState]:
        return self.cluster_assembler.initialize_clusters(target_messages)

    async def _fetch_parent_messages(
        self,
        entity: Any,
        chat_id: int,
        anchors_by_cluster: Dict[str, List[ContextCandidate]],
    ) -> Dict[int, ContextCandidate]:
        return await self.parent_reply_resolver.fetch_parent_messages(
            entity=entity,
            request=ParentLookupRequest(
                chat_id=chat_id,
                anchors_by_cluster=anchors_by_cluster,
            ),
        )

    async def _fetch_candidate_pool(
        self,
        entity: Any,
        chat_id: int,
        *,
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

    def _associate_candidates(
        self,
        clusters: List[ContextClusterState],
        candidate_messages: List[ContextCandidate],
        *,
        round_number: int,
        max_cluster: int,
    ) -> List[MessageData]:
        return self.cluster_assembler.associate_candidates(
            clusters=clusters,
            candidates=candidate_messages,
            round_number=round_number,
            max_cluster=max_cluster,
        )

    def _normalize_message(
        self,
        msg: MessageData,
        *,
        semantic_source: str = "unknown",
        retrieval_source: str = "unknown",
    ) -> ContextCandidate:
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
