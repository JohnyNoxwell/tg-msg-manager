from typing import Any, AsyncIterator, Optional


class ChannelPostFetcher:
    def __init__(self, client: Any):
        self.client = client

    async def iter_posts(
        self,
        entity: Any,
        *,
        limit: Optional[int] = None,
    ) -> AsyncIterator[Any]:
        async for message in self.client.iter_messages(entity, limit=limit):
            if getattr(message, "is_service", False):
                continue
            yield message
