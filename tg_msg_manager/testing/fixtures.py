import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

from ..core.models.message import MessageData
from .fake_telegram import FakeDialog, FakeEntity


@dataclass
class FixtureFailureRule:
    method: str
    entity_id: Optional[int] = None
    from_user_id: Optional[int] = None
    error_type: str = "RuntimeError"
    message: str = "fixture failure"
    times: int = 1
    seconds: Optional[int] = None


@dataclass
class TelegramFixtureDataset:
    entities: dict[int, FakeEntity]
    dialogs: list[FakeDialog]
    messages_by_chat: dict[int, list[MessageData]]
    deleted_ids_by_chat: dict[int, set[int]] = field(default_factory=dict)
    missing_ids_by_chat: dict[int, set[int]] = field(default_factory=dict)
    failure_rules: list[FixtureFailureRule] = field(default_factory=list)
    me: Any = field(
        default_factory=lambda: FakeEntity(
            id=9000,
            entity_type="user",
            first_name="Fixture",
            last_name="Owner",
            username="fixture_owner",
        )
    )
    source_path: Optional[Path] = None


def load_telegram_fixture(path: str | Path) -> TelegramFixtureDataset:
    fixture_path = Path(path)
    entities: dict[int, FakeEntity] = {}
    dialogs: list[FakeDialog] = []
    messages_by_chat: dict[int, list[MessageData]] = {}
    deleted_ids_by_chat: dict[int, set[int]] = {}
    missing_ids_by_chat: dict[int, set[int]] = {}
    failure_rules: list[FixtureFailureRule] = []
    me_entity: Optional[FakeEntity] = None

    for line_number, raw_line in enumerate(
        fixture_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not raw_line.strip():
            continue
        payload = json.loads(raw_line)
        kind = str(payload.get("kind", "message")).strip().lower()

        if kind == "entity":
            entity = _parse_entity(payload)
            entities[entity.id] = entity
            if payload.get("include_in_dialogs"):
                dialogs.append(
                    FakeDialog(
                        entity=entity,
                        is_group=entity.is_group,
                        is_channel=entity.is_channel,
                    )
                )
            if payload.get("is_me"):
                me_entity = entity
            continue

        if kind == "message":
            message = _parse_message(payload)
            messages_by_chat.setdefault(message.chat_id, []).append(message)
            continue

        if kind == "deleted":
            deleted_ids_by_chat.setdefault(int(payload["chat_id"]), set()).add(
                int(payload["message_id"])
            )
            continue

        if kind == "missing":
            missing_ids_by_chat.setdefault(int(payload["chat_id"]), set()).add(
                int(payload["message_id"])
            )
            continue

        if kind == "failure":
            failure_rules.append(
                FixtureFailureRule(
                    method=str(payload["method"]),
                    entity_id=_optional_int(payload.get("entity_id")),
                    from_user_id=_optional_int(payload.get("from_user_id")),
                    error_type=str(payload.get("error_type", "RuntimeError")),
                    message=str(payload.get("message", "fixture failure")),
                    times=max(1, int(payload.get("times", 1))),
                    seconds=_optional_int(payload.get("seconds")),
                )
            )
            continue

        raise ValueError(
            f"Unsupported fixture record kind {kind!r} at {fixture_path}:{line_number}"
        )

    for chat_id, messages in messages_by_chat.items():
        messages.sort(key=lambda item: item.message_id, reverse=True)
        deleted_ids_by_chat.setdefault(chat_id, set())
        missing_ids_by_chat.setdefault(chat_id, set())

    if me_entity is None:
        me_entity = TelegramFixtureDataset.__dataclass_fields__["me"].default_factory()

    return TelegramFixtureDataset(
        entities=entities,
        dialogs=dialogs,
        messages_by_chat=messages_by_chat,
        deleted_ids_by_chat=deleted_ids_by_chat,
        missing_ids_by_chat=missing_ids_by_chat,
        failure_rules=failure_rules,
        me=me_entity,
        source_path=fixture_path,
    )


def seed_storage_from_fixture(
    storage: Any,
    dataset: TelegramFixtureDataset,
    *,
    target_id: Optional[int] = None,
    include_hidden: bool = False,
) -> None:
    for entity in dataset.entities.values():
        if entity.is_user:
            storage.upsert_user(
                entity.id,
                first_name=entity.first_name,
                last_name=entity.last_name,
                username=entity.username,
                phone=entity.phone,
            )
        else:
            storage.upsert_chat(
                entity.id, entity.title or f"Chat {entity.id}", entity._
            )

    for chat_id, messages in dataset.messages_by_chat.items():
        hidden_ids = set()
        if not include_hidden:
            hidden_ids.update(dataset.deleted_ids_by_chat.get(chat_id, set()))
            hidden_ids.update(dataset.missing_ids_by_chat.get(chat_id, set()))
        for message in reversed(messages):
            if message.message_id in hidden_ids:
                continue
            storage._conn.execute(
                """
                INSERT OR REPLACE INTO messages (
                    message_id, chat_id, user_id, author_name, timestamp, text,
                    media_type, reply_to_id, fwd_from_id, context_group_id,
                    raw_payload, payload_hash, is_service
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    message.message_id,
                    message.chat_id,
                    message.user_id,
                    message.author_name,
                    int(message.timestamp.timestamp()),
                    message.text,
                    message.media_type,
                    message.reply_to_id,
                    message.fwd_from_id,
                    message.context_group_id,
                    json.dumps(message.raw_payload, ensure_ascii=False),
                    message.get_payload_hash(),
                    1 if message.is_service else 0,
                ),
            )
            if target_id is not None:
                storage._conn.execute(
                    """
                    INSERT OR IGNORE INTO target_messages (chat_id, message_id, target_user_id)
                    VALUES (?, ?, ?)
                    """,
                    (message.chat_id, message.message_id, target_id),
                )
    storage._conn.commit()


def load_export_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw_line in Path(path).read_text(encoding="utf-8").splitlines():
        if raw_line.strip():
            rows.append(json.loads(raw_line))
    return rows


def normalize_export_rows(
    rows: Iterable[dict[str, Any]],
    *,
    drop_fields: Iterable[str] = (),
) -> list[dict[str, Any]]:
    dropped = set(drop_fields)
    normalized = []
    for row in rows:
        normalized.append(
            {key: value for key, value in row.items() if key not in dropped}
        )
    normalized.sort(
        key=lambda item: (item.get("message_id", 0), item.get("chat_id", 0))
    )
    return normalized


def _parse_entity(payload: dict[str, Any]) -> FakeEntity:
    entity_id = int(payload["entity_id"])
    entity_type = str(payload.get("entity_type", "user")).strip().lower()
    if entity_type not in {"user", "group", "channel"}:
        raise ValueError(f"Unsupported entity_type: {entity_type!r}")
    return FakeEntity(
        id=entity_id,
        entity_type=entity_type,
        title=payload.get("title"),
        first_name=payload.get("first_name"),
        last_name=payload.get("last_name"),
        username=payload.get("username"),
        phone=payload.get("phone"),
        broadcast=bool(payload.get("broadcast", False)),
        include_in_dialogs=bool(payload.get("include_in_dialogs", False)),
    )


def _parse_message(payload: dict[str, Any]) -> MessageData:
    timestamp = payload["timestamp"]
    if isinstance(timestamp, (int, float)):
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    else:
        dt = datetime.fromisoformat(str(timestamp))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

    raw_payload = payload.get("raw_payload", {})
    if not isinstance(raw_payload, dict):
        raise TypeError("raw_payload must be an object in fixture message records")

    return MessageData(
        message_id=int(payload["message_id"]),
        chat_id=int(payload["chat_id"]),
        user_id=int(payload["user_id"]),
        author_name=payload.get("author_name"),
        timestamp=dt,
        text=payload.get("text"),
        media_type=payload.get("media_type"),
        reply_to_id=_optional_int(payload.get("reply_to_id")),
        fwd_from_id=_optional_int(payload.get("fwd_from_id")),
        context_group_id=(
            str(payload["context_group_id"])
            if payload.get("context_group_id") is not None
            else None
        ),
        raw_payload=raw_payload,
        is_service=bool(payload.get("is_service", False)),
        media_ref=payload.get("media_ref"),
    )


def _optional_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    return int(value)
