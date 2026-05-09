import inspect
from collections import Counter
from collections.abc import Iterable
from typing import Any, Optional

from .models import (
    DISCUSSION_SOURCE_STATUS_FAILED,
    DISCUSSION_SOURCE_STATUS_NOT_AVAILABLE,
    DISCUSSION_SOURCE_STATUS_NOT_LINKED,
    DISCUSSION_SOURCE_STATUS_RESOLVED,
    ChannelDiscussionSource,
)


class ChannelDiscussionResolver:
    def __init__(self, client: Any):
        self.client = client

    async def resolve(
        self, channel_entity: Any, posts: Optional[list[Any]] = None
    ) -> ChannelDiscussionSource:
        source = await self._resolve_channel_link(channel_entity)
        if source.status != DISCUSSION_SOURCE_STATUS_NOT_LINKED:
            return source
        fallback_chat_id = self._discussion_chat_id_from_posts(posts or ())
        if fallback_chat_id is None:
            return source
        return await self._resolve_discussion_entity(fallback_chat_id)

    async def _resolve_channel_link(
        self, channel_entity: Any
    ) -> ChannelDiscussionSource:
        linked_chat_id = self._extract_linked_chat_id(channel_entity)
        discussion_entity = None
        if linked_chat_id is None:
            full_result = await self._get_full_channel(channel_entity)
            if isinstance(full_result, Exception):
                return ChannelDiscussionSource(
                    status=DISCUSSION_SOURCE_STATUS_FAILED,
                    discussion_chat_id=None,
                    discussion_entity=None,
                    error=str(full_result),
                )
            if full_result is not None:
                linked_chat_id = self._extract_linked_chat_id(full_result)
                discussion_entity = self._find_chat(full_result, linked_chat_id)
        if linked_chat_id is None:
            return ChannelDiscussionSource(
                status=DISCUSSION_SOURCE_STATUS_NOT_LINKED,
                discussion_chat_id=None,
                discussion_entity=None,
                error=None,
            )

        if discussion_entity is not None:
            return ChannelDiscussionSource(
                status=DISCUSSION_SOURCE_STATUS_RESOLVED,
                discussion_chat_id=linked_chat_id,
                discussion_entity=discussion_entity,
                error=None,
            )

        return await self._resolve_discussion_entity(linked_chat_id)

    async def _resolve_discussion_entity(
        self, discussion_chat_id: int
    ) -> ChannelDiscussionSource:
        get_entity = getattr(self.client, "get_entity", None)
        if get_entity is None:
            return ChannelDiscussionSource(
                status=DISCUSSION_SOURCE_STATUS_NOT_AVAILABLE,
                discussion_chat_id=discussion_chat_id,
                discussion_entity=None,
                error="Client does not support entity resolution",
            )

        try:
            discussion_entity = get_entity(discussion_chat_id)
            if inspect.isawaitable(discussion_entity):
                discussion_entity = await discussion_entity
        except Exception as exc:
            return ChannelDiscussionSource(
                status=DISCUSSION_SOURCE_STATUS_FAILED,
                discussion_chat_id=discussion_chat_id,
                discussion_entity=None,
                error=str(exc),
            )

        return ChannelDiscussionSource(
            status=DISCUSSION_SOURCE_STATUS_RESOLVED,
            discussion_chat_id=discussion_chat_id,
            discussion_entity=discussion_entity,
            error=None,
        )

    @staticmethod
    def _extract_linked_chat_id(channel_entity: Any) -> Optional[int]:
        candidates = (
            channel_entity,
            getattr(channel_entity, "full_chat", None),
            getattr(channel_entity, "channel_full", None),
            getattr(channel_entity, "full_channel", None),
        )
        for candidate in candidates:
            if candidate is None:
                continue
            for attribute in (
                "linked_chat_id",
                "linked_discussion_chat_id",
                "discussion_chat_id",
            ):
                value = getattr(candidate, attribute, None)
                if value is not None:
                    return int(value)
        return None

    async def _get_full_channel(self, channel_entity: Any) -> Any:
        try:
            from telethon import functions
        except ImportError:
            return None
        request = functions.channels.GetFullChannelRequest(channel=channel_entity)
        raw_request = getattr(self.client, "request", None)
        if callable(raw_request):
            caller = raw_request
        elif callable(self.client):
            caller = self.client
        else:
            return None
        try:
            result = caller(request)
            if inspect.isawaitable(result):
                result = await result
            return result
        except Exception as exc:
            return exc

    @staticmethod
    def _find_chat(full_result: Any, linked_chat_id: Optional[int]) -> Optional[Any]:
        if linked_chat_id is None:
            return None
        for chat in getattr(full_result, "chats", None) or ():
            if getattr(chat, "id", None) == linked_chat_id:
                return chat
        return None

    @classmethod
    def _discussion_chat_id_from_posts(cls, posts: Iterable[Any]) -> Optional[int]:
        counter: Counter[int] = Counter()
        for post in posts:
            chat_id = cls._discussion_chat_id_from_post(post)
            if chat_id is not None:
                counter[chat_id] += 1
        if not counter:
            return None
        return sorted(counter.items(), key=lambda item: (-item[1], item[0]))[0][0]

    @staticmethod
    def _discussion_chat_id_from_post(post: Any) -> Optional[int]:
        raw_payload = getattr(post, "raw_payload", None)
        if not isinstance(raw_payload, dict):
            return None
        replies = raw_payload.get("replies")
        if not isinstance(replies, dict) or replies.get("comments") is not True:
            return None
        value = replies.get("channel_id")
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
