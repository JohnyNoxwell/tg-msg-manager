import inspect
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, AsyncGenerator, Callable, Optional

from ..core.models.message import MessageData
from ..core.telegram.interface import TelegramClientInterface


@dataclass(frozen=True)
class FakeEntity:
    id: int
    entity_type: str
    title: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    phone: Optional[str] = None
    broadcast: bool = False
    include_in_dialogs: bool = False

    @property
    def is_group(self) -> bool:
        return self.entity_type == "group"

    @property
    def is_channel(self) -> bool:
        return self.entity_type == "channel"

    @property
    def is_user(self) -> bool:
        return self.entity_type == "user"

    @property
    def _(self) -> str:
        if self.entity_type == "channel":
            return "Channel"
        if self.entity_type == "group":
            return "Chat"
        return "User"


@dataclass(frozen=True)
class FakeDialog:
    entity: FakeEntity
    is_group: bool
    is_channel: bool


@dataclass
class _FailureRuleState:
    method: str
    entity_id: Optional[int]
    from_user_id: Optional[int]
    error_type: str
    message: str
    times: int
    seconds: Optional[int] = None


class FakeTelegramClient(TelegramClientInterface):
    """
    Telegram-like client backed by anonymized fixture datasets.
    """

    def __init__(self, dataset: Any):
        self.connected = False
        self.call_history: list[dict[str, Any]] = []
        self.message_yield_hook: Optional[Callable[..., Any]] = None
        self.replace_dataset(dataset)

    def replace_dataset(self, dataset: Any) -> None:
        self.dataset = dataset
        self.entities = dict(dataset.entities)
        self._dialogs = list(dataset.dialogs)
        self._messages_by_chat = {
            chat_id: list(messages)
            for chat_id, messages in dataset.messages_by_chat.items()
        }
        self._deleted_ids_by_chat = {
            chat_id: set(ids) for chat_id, ids in dataset.deleted_ids_by_chat.items()
        }
        self._missing_ids_by_chat = {
            chat_id: set(ids) for chat_id, ids in dataset.missing_ids_by_chat.items()
        }
        self._failure_rules = [
            _FailureRuleState(
                method=rule.method,
                entity_id=rule.entity_id,
                from_user_id=rule.from_user_id,
                error_type=rule.error_type,
                message=rule.message,
                times=rule.times,
                seconds=rule.seconds,
            )
            for rule in dataset.failure_rules
        ]
        self._message_index: dict[tuple[int, int], MessageData] = {}
        for chat_id, messages in self._messages_by_chat.items():
            for message in messages:
                self._message_index[(chat_id, message.message_id)] = message

    async def connect(self):
        self.connected = True

    async def disconnect(self):
        self.connected = False

    async def get_me(self):
        return self.dataset.me

    async def get_dialogs(self) -> list[Any]:
        self._record_call("get_dialogs")
        return list(self._dialogs)

    async def get_entity(self, entity_id: Any) -> Any:
        resolved_id = self._resolve_entity_id(entity_id)
        self._record_call("get_entity", entity_id=resolved_id)
        entity = self.entities.get(resolved_id)
        if entity is None:
            raise ValueError(f"Unknown fixture entity: {entity_id!r}")
        return entity

    async def get_messages(
        self,
        entity: Any,
        message_ids: Optional[list[int]] = None,
        limit: Optional[int] = None,
    ) -> list[MessageData]:
        entity_id = self._resolve_entity_id(entity)
        self._maybe_raise_failure(
            method="get_messages",
            entity_id=entity_id,
            from_user_id=None,
        )
        self._record_call(
            "get_messages",
            entity_id=entity_id,
            message_ids=list(message_ids) if message_ids is not None else None,
            limit=limit,
        )
        visible_messages = self._visible_messages(entity_id)
        if limit is not None:
            return visible_messages[:limit]
        if not message_ids:
            return []
        return [
            self._message_index[(entity_id, message_id)]
            for message_id in message_ids
            if (entity_id, message_id) in self._message_index
            and not self._is_hidden(entity_id, message_id)
        ]

    async def iter_messages(
        self,
        entity,
        limit: Optional[int] = None,
        offset_id: int = 0,
        from_user: Optional[Any] = None,
        **kwargs,
    ) -> AsyncGenerator[MessageData, None]:
        entity_id = self._resolve_entity_id(entity)
        from_user_id = self._resolve_user_id(from_user)
        self._maybe_raise_failure(
            method="iter_messages",
            entity_id=entity_id,
            from_user_id=from_user_id,
        )
        self._record_call(
            "iter_messages",
            entity_id=entity_id,
            offset_id=offset_id,
            limit=limit,
            from_user_id=from_user_id,
        )

        yielded = 0
        for message in self._visible_messages(entity_id):
            if offset_id and message.message_id >= offset_id:
                continue
            if from_user_id is not None and message.user_id != from_user_id:
                continue
            if self.message_yield_hook is not None:
                maybe_awaitable = self.message_yield_hook(
                    message,
                    {
                        "entity_id": entity_id,
                        "from_user_id": from_user_id,
                        "offset_id": offset_id,
                        "limit": limit,
                    },
                )
                if inspect.isawaitable(maybe_awaitable):
                    await maybe_awaitable
            yield message
            yielded += 1
            if limit is not None and yielded >= limit:
                break

    async def delete_messages(self, entity, message_ids: list[int]) -> int:
        entity_id = self._resolve_entity_id(entity)
        self._record_call(
            "delete_messages", entity_id=entity_id, message_ids=list(message_ids)
        )
        deleted = self._deleted_ids_by_chat.setdefault(entity_id, set())
        before = len(deleted)
        deleted.update(message_ids)
        return len(deleted) - before

    async def download_media(
        self, media: Any, file: Optional[str] = None
    ) -> Optional[str]:
        self._record_call("download_media", file=file)
        if media is None:
            return None

        payload = media if isinstance(media, dict) else {"content": str(media)}
        content = payload.get("content", "")
        suffix = payload.get("suffix", ".bin")
        binary = bool(payload.get("binary", False))

        if file:
            target_path = Path(file)
        else:
            target_path = Path("fixture_media").with_suffix(suffix)
        if target_path.suffix == "":
            target_path = target_path.with_suffix(suffix)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        mode = "wb" if binary else "w"
        with open(target_path, mode, encoding=None if binary else "utf-8") as handle:
            if binary:
                if isinstance(content, bytes):
                    handle.write(content)
                else:
                    handle.write(str(content).encode("utf-8"))
            else:
                handle.write(str(content))
        return os.fspath(target_path)

    def _record_call(self, method: str, **payload: Any) -> None:
        self.call_history.append({"method": method, **payload})

    def _visible_messages(self, entity_id: int) -> list[MessageData]:
        return [
            message
            for message in self._messages_by_chat.get(entity_id, [])
            if not self._is_hidden(entity_id, message.message_id)
        ]

    def _is_hidden(self, entity_id: int, message_id: int) -> bool:
        return message_id in self._deleted_ids_by_chat.get(
            entity_id, set()
        ) or message_id in self._missing_ids_by_chat.get(entity_id, set())

    def _maybe_raise_failure(
        self,
        *,
        method: str,
        entity_id: Optional[int],
        from_user_id: Optional[int],
    ) -> None:
        for rule in self._failure_rules:
            if rule.times <= 0:
                continue
            if rule.method != method:
                continue
            if rule.entity_id is not None and rule.entity_id != entity_id:
                continue
            if rule.from_user_id is not None and rule.from_user_id != from_user_id:
                continue
            rule.times -= 1
            raise self._build_error(rule)

    @staticmethod
    def _build_error(rule: _FailureRuleState) -> Exception:
        if rule.error_type == "FloodWaitError":
            exc = RuntimeError(rule.message)
            if rule.seconds is not None:
                setattr(exc, "seconds", rule.seconds)
            return exc
        if rule.error_type == "ValueError":
            return ValueError(rule.message)
        exc = RuntimeError(rule.message)
        if rule.seconds is not None:
            setattr(exc, "seconds", rule.seconds)
        return exc

    @staticmethod
    def _resolve_entity_id(entity: Any) -> int:
        if isinstance(entity, bool):
            raise ValueError("Boolean entity ids are not supported")
        if isinstance(entity, int):
            return entity
        if isinstance(entity, str) and (
            entity.isdigit() or (entity.startswith("-") and entity[1:].isdigit())
        ):
            return int(entity)
        if hasattr(entity, "id"):
            return int(getattr(entity, "id"))
        raise ValueError(f"Could not resolve fixture entity id from {entity!r}")

    @classmethod
    def _resolve_user_id(cls, from_user: Optional[Any]) -> Optional[int]:
        if from_user is None:
            return None
        if isinstance(from_user, str) and from_user == "me":
            return None
        try:
            return cls._resolve_entity_id(from_user)
        except Exception:
            if hasattr(from_user, "user_id"):
                return int(getattr(from_user, "user_id"))
            return None
