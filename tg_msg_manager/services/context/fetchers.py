import asyncio
from time import perf_counter
from typing import Any, Callable, Dict, Iterable, List, Optional

from ...core.models.message import MessageData
from ...core.telemetry import telemetry
from .models import ContextCandidate


class StorageContextResolver:
    def __init__(
        self,
        *,
        storage: Any,
        normalize_message: Callable[..., ContextCandidate],
    ):
        self.storage = storage
        self.normalize_message = normalize_message

    async def load_parent_messages_by_ids(
        self,
        *,
        chat_id: int,
        parent_ids: List[int],
    ) -> tuple[Dict[int, ContextCandidate], int, List[int]]:
        normalized: Dict[int, ContextCandidate] = {}
        stored_messages = self.load_stored_messages_by_ids(chat_id, parent_ids)
        if stored_messages is None:
            storage_hits = 0
            missing_ids: List[int] = []
            for parent_id in parent_ids:
                stored = await asyncio.to_thread(
                    self.storage.get_message, chat_id, parent_id
                )
                if stored:
                    normalized[parent_id] = self.normalize_message(
                        stored,
                        semantic_source="parent_lookup",
                        retrieval_source="storage",
                    )
                    storage_hits += 1
                else:
                    missing_ids.append(parent_id)
            return normalized, storage_hits, missing_ids

        for stored in stored_messages.values():
            normalized[stored.message_id] = self.normalize_message(
                stored,
                semantic_source="parent_lookup",
                retrieval_source="storage",
            )
        missing_ids = [
            parent_id for parent_id in parent_ids if parent_id not in normalized
        ]
        return normalized, len(stored_messages), missing_ids

    def load_stored_range(
        self,
        *,
        chat_id: int,
        start_id: int,
        end_id: int,
    ) -> List[MessageData]:
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
        telemetry.track_duration(
            "deep.load_stored_range.total", perf_counter() - started_at
        )
        return rows

    def load_stored_messages_by_ids(
        self,
        chat_id: int,
        message_ids: List[int],
    ) -> Optional[Dict[int, MessageData]]:
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

    def load_stored_replies(
        self,
        *,
        chat_id: int,
        reply_to_ids: Iterable[int],
    ) -> List[MessageData]:
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
        telemetry.track_duration(
            "deep.load_stored_replies.total", perf_counter() - started_at
        )
        return rows


class LiveContextResolver:
    def __init__(
        self,
        *,
        client: Any,
        semaphore: asyncio.Semaphore,
        normalize_message: Callable[..., ContextCandidate],
    ):
        self.client = client
        self.semaphore = semaphore
        self.normalize_message = normalize_message

    async def fetch_parent_messages_by_ids(
        self,
        *,
        entity: Any,
        missing_ids: List[int],
    ) -> Dict[int, ContextCandidate]:
        try:
            async with self.semaphore:
                fetched = await self.client.get_messages(
                    entity, message_ids=missing_ids
                )
        except TypeError:
            async with self.semaphore:
                fetched = await self.client.get_messages(entity, missing_ids)

        normalized: Dict[int, ContextCandidate] = {}
        for msg in fetched:
            norm = self.normalize_message(
                msg,
                semantic_source="parent_lookup",
                retrieval_source="live",
            )
            normalized[norm.message.message_id] = norm
        return normalized

    async def fetch_range(
        self,
        *,
        entity: Any,
        start_id: int,
        end_id: int,
        retrieval_source: str,
    ) -> List[MessageData]:
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
        telemetry.track_counter(
            f"deep.fetch_range.source.{retrieval_source}", len(results)
        )
        telemetry.track_duration("deep.fetch_range.total", perf_counter() - started_at)
        return results

    async def fetch_ranges(
        self,
        *,
        entity: Any,
        ranges: List[tuple[int, int]],
        retrieval_source: str,
    ) -> List[MessageData]:
        results: List[MessageData] = []
        for start_id, end_id in ranges:
            results.extend(
                await self.fetch_range(
                    entity=entity,
                    start_id=start_id,
                    end_id=end_id,
                    retrieval_source=retrieval_source,
                )
            )
        return results

    async def fetch_missing_ids(
        self,
        *,
        entity: Any,
        message_ids: List[int],
    ) -> List[MessageData]:
        if not message_ids:
            return []

        started_at = perf_counter()
        try:
            async with self.semaphore:
                return await self.client.get_messages(entity, message_ids=message_ids)
        finally:
            telemetry.track_counter("deep.fetch_missing_ids.calls", 1)
            telemetry.track_counter(
                "deep.fetch_missing_ids.requested", len(message_ids)
            )
            telemetry.track_duration(
                "deep.fetch_missing_ids.total", perf_counter() - started_at
            )
