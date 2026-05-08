from typing import Any, AsyncIterator, Optional


class ChannelPostFetcher:
    def __init__(self, client: Any):
        self.client = client

    async def iter_posts(
        self,
        entity: Any,
        *,
        limit: Optional[int] = None,
        min_message_id: Optional[int] = None,
    ) -> AsyncIterator[Any]:
        iterator = self._build_iterator(
            entity,
            limit=limit,
            min_message_id=min_message_id,
        )
        yielded = 0
        async for message in iterator:
            if getattr(message, "is_service", False):
                continue
            if (
                min_message_id is not None
                and int(getattr(message, "message_id")) <= min_message_id
            ):
                continue
            yield message
            yielded += 1
            if limit is not None and yielded >= limit:
                break

    def _build_iterator(
        self,
        entity: Any,
        *,
        limit: Optional[int],
        min_message_id: Optional[int],
    ) -> AsyncIterator[Any]:
        if min_message_id is None:
            return self.client.iter_messages(entity, limit=limit)
        try:
            return self.client.iter_messages(
                entity,
                limit=limit,
                min_id=min_message_id,
            )
        except TypeError:
            return self.client.iter_messages(entity, limit=limit)
