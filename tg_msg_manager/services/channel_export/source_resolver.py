from typing import Any, Tuple

from .errors import ChannelResolveError, InvalidChannelError
from .models import ChannelIdentity


class ChannelSourceResolver:
    def __init__(self, client: Any):
        self.client = client

    async def resolve(self, channel: str) -> Tuple[Any, ChannelIdentity]:
        last_error = None
        for candidate in self._resolution_candidates(channel):
            try:
                entity = await self.client.get_entity(candidate)
                break
            except Exception as exc:
                last_error = exc
        else:
            raise ChannelResolveError(
                f"Could not resolve channel {channel!r}"
            ) from last_error

        if not hasattr(entity, "id"):
            raise InvalidChannelError("Resolved entity does not expose an id")

        if self._looks_like_non_channel(entity):
            raise InvalidChannelError(self._invalid_entity_message(channel, entity))

        identity = ChannelIdentity(
            channel_id=int(getattr(entity, "id")),
            title=getattr(entity, "title", None),
            username=getattr(entity, "username", None),
            access_hash=getattr(entity, "access_hash", None),
        )
        return entity, identity

    @staticmethod
    def _resolution_candidates(channel: str) -> tuple[Any, ...]:
        normalized = channel.strip()
        candidates = [normalized]
        if normalized and (
            normalized.isdigit()
            or (normalized.startswith("-") and normalized[1:].isdigit())
        ):
            numeric_id = int(normalized)
            candidates.insert(0, numeric_id)
            if normalized.startswith("-100") and normalized[4:].isdigit():
                candidates.insert(1, int(normalized[4:]))
        return tuple(dict.fromkeys(candidates))

    @staticmethod
    def _looks_like_non_channel(entity: Any) -> bool:
        if getattr(entity, "is_user", False):
            return True
        if getattr(entity, "entity_type", None) == "user":
            return True
        if getattr(entity, "entity_type", None) == "group":
            return True
        if hasattr(entity, "broadcast"):
            return not bool(getattr(entity, "broadcast")) and not bool(
                getattr(entity, "is_channel", False)
            )
        if hasattr(entity, "is_channel"):
            return not bool(getattr(entity, "is_channel"))
        return False

    @staticmethod
    def _invalid_entity_message(channel: str, entity: Any) -> str:
        if (
            getattr(entity, "is_user", False)
            or getattr(entity, "entity_type", None) == "user"
        ):
            return (
                f"Resolved entity {channel!r} is a user; export-channel expects a "
                "broadcast channel"
            )
        if getattr(entity, "entity_type", None) == "group" or bool(
            getattr(entity, "megagroup", False)
        ):
            return (
                f"Resolved entity {channel!r} is a group/supergroup; "
                "export-channel currently supports broadcast channels only"
            )
        if hasattr(entity, "broadcast") and not bool(getattr(entity, "broadcast")):
            return (
                f"Resolved entity {channel!r} is not a broadcast channel; "
                "export-channel currently supports broadcast channels only"
            )
        return f"Resolved entity {channel!r} is not a channel"
