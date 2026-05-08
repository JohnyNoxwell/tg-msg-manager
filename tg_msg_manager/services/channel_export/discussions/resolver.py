import inspect
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

    async def resolve(self, channel_entity: Any) -> ChannelDiscussionSource:
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

        get_entity = getattr(self.client, "get_entity", None)
        if get_entity is None:
            return ChannelDiscussionSource(
                status=DISCUSSION_SOURCE_STATUS_NOT_AVAILABLE,
                discussion_chat_id=linked_chat_id,
                discussion_entity=None,
                error="Client does not support entity resolution",
            )

        try:
            discussion_entity = get_entity(linked_chat_id)
            if inspect.isawaitable(discussion_entity):
                discussion_entity = await discussion_entity
        except Exception as exc:
            return ChannelDiscussionSource(
                status=DISCUSSION_SOURCE_STATUS_FAILED,
                discussion_chat_id=linked_chat_id,
                discussion_entity=None,
                error=str(exc),
            )

        return ChannelDiscussionSource(
            status=DISCUSSION_SOURCE_STATUS_RESOLVED,
            discussion_chat_id=linked_chat_id,
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
        if not callable(self.client):
            return None
        try:
            from telethon import functions
        except ImportError:
            return None
        try:
            result = self.client(
                functions.channels.GetFullChannelRequest(channel=channel_entity)
            )
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
