from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Optional

from ...infrastructure.storage.records import SyncStatus


@dataclass
class TrackedSyncPlan:
    chat_id: int
    from_user_id: int
    effective_from_user_id: Optional[int]
    entity: Any
    current_max: int
    target_status: SyncStatus
    last_msg_id: int
    is_complete: bool
    prefetched_messages: Optional[list[Any]] = None
    prefetched_head_complete: bool = False


class TrackedSyncPlanner:
    def __init__(
        self,
        *,
        client: Any,
        storage: Any,
        prefetch_chat_head_messages: Callable[
            [Any, int, int], Awaitable[tuple[list[Any], bool]]
        ],
    ):
        self.client = client
        self.storage = storage
        self.prefetch_chat_head_messages = prefetch_chat_head_messages

    @staticmethod
    def normalize_target_item(item: Any) -> tuple[int, int]:
        if isinstance(item, tuple) and len(item) == 2:
            return item
        return item, item

    async def get_or_load_entity(
        self,
        *,
        chat_id: int,
        entity_cache: dict[int, Any],
    ) -> Optional[Any]:
        entity = entity_cache.get(chat_id)
        if entity is None:
            entity = await self.client.get_entity(chat_id)
            if entity:
                entity_cache[chat_id] = entity
        return entity

    async def get_or_load_current_max(
        self,
        *,
        chat_id: int,
        entity: Any,
        current_max_cache: dict[int, int],
    ) -> int:
        current_max = current_max_cache.get(chat_id)
        if current_max is None:
            latest_msg = await self.client.get_messages(entity, limit=1)
            current_max = latest_msg[0].message_id if latest_msg else 1000000
            current_max_cache[chat_id] = current_max
        return current_max

    def get_cached_sync_status(
        self,
        *,
        chat_id: int,
        target_id: int,
        status_cache: dict[tuple[int, int], SyncStatus],
    ) -> SyncStatus:
        status_key = (chat_id, target_id)
        status = status_cache.get(status_key)
        if status is None:
            loaded = self.storage.get_sync_status(chat_id, target_id)
            status = SyncStatus.coerce(loaded)
            status_cache[status_key] = status
        return status

    async def prime_shared_head_prefetch_cache(
        self,
        *,
        items_by_chat: dict[int, list[int]],
        entity_cache: dict[int, Any],
        current_max_cache: dict[int, int],
        shared_prefetch_cache: dict[int, tuple[list[Any], bool]],
        status_cache: dict[tuple[int, int], SyncStatus],
    ) -> None:
        for chat_id, target_ids in items_by_chat.items():
            user_targets = [
                target_id for target_id in target_ids if target_id != chat_id
            ]
            if len(user_targets) < 2:
                continue

            entity = await self.get_or_load_entity(
                chat_id=chat_id, entity_cache=entity_cache
            )
            if entity is None:
                continue

            current_max = await self.get_or_load_current_max(
                chat_id=chat_id,
                entity=entity,
                current_max_cache=current_max_cache,
            )
            lower_bounds = []
            for target_id in user_targets:
                status = self.get_cached_sync_status(
                    chat_id=chat_id,
                    target_id=target_id,
                    status_cache=status_cache,
                )
                last_msg_id = status.last_msg_id
                if last_msg_id > 0 and current_max > last_msg_id:
                    lower_bounds.append(last_msg_id + 1)

            if len(lower_bounds) < 2:
                continue

            shared_prefetch_cache[chat_id] = await self.prefetch_chat_head_messages(
                entity,
                current_max=current_max,
                lower_bound=min(lower_bounds),
            )

    async def plan_target(
        self,
        item: Any,
        *,
        entity_cache: dict[int, Any],
        current_max_cache: dict[int, int],
        shared_prefetch_cache: dict[int, tuple[list[Any], bool]],
        status_cache: dict[tuple[int, int], SyncStatus],
    ) -> Optional[TrackedSyncPlan]:
        chat_id, from_user_id = self.normalize_target_item(item)
        entity = await self.get_or_load_entity(
            chat_id=chat_id, entity_cache=entity_cache
        )
        if entity is None:
            return None

        current_max = await self.get_or_load_current_max(
            chat_id=chat_id,
            entity=entity,
            current_max_cache=current_max_cache,
        )
        target_status = self.get_cached_sync_status(
            chat_id=chat_id,
            target_id=from_user_id,
            status_cache=status_cache,
        )
        last_msg_id = target_status.last_msg_id
        is_complete = target_status.is_complete

        effective_from_user_id = None if from_user_id == chat_id else from_user_id
        prefetched_messages = None
        prefetched_head_complete = False
        if effective_from_user_id:
            prefetched = shared_prefetch_cache.get(chat_id)
            if prefetched is not None:
                prefetched_messages, prefetched_head_complete = prefetched

        return TrackedSyncPlan(
            chat_id=chat_id,
            from_user_id=from_user_id,
            effective_from_user_id=effective_from_user_id,
            entity=entity,
            current_max=current_max,
            target_status=target_status,
            last_msg_id=last_msg_id,
            is_complete=is_complete,
            prefetched_messages=prefetched_messages,
            prefetched_head_complete=prefetched_head_complete,
        )
