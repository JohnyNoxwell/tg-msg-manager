import logging
from dataclasses import dataclass
from typing import Any, Optional

from ...infrastructure.storage.records import SyncStatus
from ...utils.ui import UI

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ResolvedSyncTargetIdentity:
    uid: int
    target_name: str
    user_label: str
    api_from_user: Optional[Any]
    local_sender_filter_id: Optional[int]


async def resolve_sync_target_identity(
    *,
    entity: Any,
    from_user_id: Optional[int],
    resolve_user_entity: bool,
    status: SyncStatus,
    client: Any,
    storage: Any,
) -> ResolvedSyncTargetIdentity:
    chat_id = getattr(entity, "id", 0)
    chat_title = UI.format_name(entity)
    uid = from_user_id or chat_id
    target_name = chat_title
    user_label = ""
    api_from_user = from_user_id
    local_sender_filter_id = None

    if from_user_id:
        if resolve_user_entity:
            try:
                user_ent = await client.get_entity(from_user_id)
                target_name = UI.format_name(user_ent)
                user_label = target_name
                api_from_user = user_ent
                storage.upsert_user(
                    user_id=user_ent.id,
                    first_name=getattr(user_ent, "first_name", None),
                    last_name=getattr(user_ent, "last_name", None),
                    username=getattr(user_ent, "username", None),
                )
            except Exception as exc:
                logger.warning(f"Could not resolve user {from_user_id}: {exc}")
                user_label = str(from_user_id)
                api_from_user = None
                local_sender_filter_id = from_user_id
        else:
            target_name = status.author_name or str(from_user_id)
            user_label = target_name

    return ResolvedSyncTargetIdentity(
        uid=uid,
        target_name=target_name,
        user_label=user_label,
        api_from_user=api_from_user,
        local_sender_filter_id=local_sender_filter_id,
    )


def resolve_active_sync_mode(
    *,
    deep_mode: bool,
    saved_deep: bool,
    recursive_depth: int,
    saved_depth: int,
) -> tuple[bool, int]:
    active_deep = deep_mode or saved_deep
    active_depth = (
        recursive_depth
        if recursive_depth > 0
        else (saved_depth if saved_depth > 0 else 2)
    )
    return active_deep, active_depth


def resolve_status_kind(
    *,
    resume_history: bool,
    tail_id: int,
    is_complete: bool,
    head_id: int,
) -> Optional[str]:
    if resume_history and tail_id > 0 and not is_complete:
        return "resuming_history"
    if head_id > 0:
        return "updating"
    return None
