import logging
from typing import Any

logger = logging.getLogger(__name__)


def normalize_dialog_target_id(chat_ref: Any) -> Any:
    if isinstance(chat_ref, str) and (chat_ref.startswith("-") or chat_ref.isdigit()):
        try:
            return int(chat_ref)
        except ValueError:
            return chat_ref
    return chat_ref


async def resolve_targeted_dialog_entities(
    *,
    client: Any,
    target_chat_ids: set[Any],
) -> list[Any]:
    targets: list[Any] = []
    for chat_ref in target_chat_ids:
        try:
            entity = await client.get_entity(normalize_dialog_target_id(chat_ref))
        except Exception as exc:
            logger.warning("Could not resolve config chat %s: %s", chat_ref, exc)
            continue
        targets.append(entity)
    return targets


def filter_group_dialog_entities(dialogs: list[Any]) -> list[Any]:
    return [
        dialog.entity
        for dialog in dialogs
        if (dialog.is_group or dialog.is_channel)
        and not getattr(dialog.entity, "broadcast", False)
    ]
