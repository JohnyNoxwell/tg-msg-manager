from typing import Any

from .errors import ChannelDiscussionFetchError
from .models import ChannelDiscussionFetchResult


class ChannelDiscussionFetcher:
    def __init__(self, client: Any):
        self.client = client

    async def fetch_comments_for_post(
        self,
        *,
        channel_entity: Any,
        discussion_entity: Any,
        channel_post_record: Any,
        max_comments_per_post: int,
    ) -> ChannelDiscussionFetchResult:
        comments = []
        try:
            async for comment in self._iter_client_comments(
                channel_entity=channel_entity,
                discussion_entity=discussion_entity,
                channel_post_record=channel_post_record,
                max_comments_per_post=max_comments_per_post,
            ):
                comments.append(comment)
                if len(comments) > max_comments_per_post:
                    break
        except Exception as exc:
            return ChannelDiscussionFetchResult(comments=(), error=str(exc))

        has_more = len(comments) > max_comments_per_post
        selected = comments[:max_comments_per_post]
        selected.sort(key=self._comment_sort_key)
        return ChannelDiscussionFetchResult(
            comments=tuple(selected),
            has_more=has_more,
            error=None,
        )

    async def iter_comments_for_post(
        self,
        *,
        channel_entity: Any,
        discussion_entity: Any,
        channel_post_record: Any,
        max_comments_per_post: int,
    ):
        result = await self.fetch_comments_for_post(
            channel_entity=channel_entity,
            discussion_entity=discussion_entity,
            channel_post_record=channel_post_record,
            max_comments_per_post=max_comments_per_post,
        )
        if result.error is not None:
            raise ChannelDiscussionFetchError(result.error)
        for comment in result.comments:
            yield comment

    async def _iter_client_comments(
        self,
        *,
        channel_entity: Any,
        discussion_entity: Any,
        channel_post_record: Any,
        max_comments_per_post: int,
    ):
        limit = max_comments_per_post + 1
        async for comment in self.client.iter_messages(
            channel_entity,
            limit=limit,
            reply_to=channel_post_record.message_id,
        ):
            yield comment

    @staticmethod
    def _comment_sort_key(comment: Any) -> tuple[Any, int]:
        timestamp = getattr(comment, "timestamp", None) or getattr(
            comment, "date", None
        )
        message_id = getattr(comment, "message_id", None) or getattr(comment, "id", 0)
        return (timestamp is None, timestamp, int(message_id or 0))
