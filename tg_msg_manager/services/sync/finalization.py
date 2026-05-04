from dataclasses import dataclass
from typing import Any

from ...infrastructure.storage.records import TargetMessageBreakdown


@dataclass(frozen=True)
class SyncChatFinalState:
    db_count: int
    breakdown: TargetMessageBreakdown
    should_mark_synced: bool


def build_sync_chat_final_state(
    *,
    storage: Any,
    chat_id: int,
    uid: int,
) -> SyncChatFinalState:
    return SyncChatFinalState(
        db_count=storage.get_message_count(chat_id, target_id=uid),
        breakdown=TargetMessageBreakdown.coerce(
            storage.get_target_message_breakdown(chat_id, uid)
        ),
        should_mark_synced=not storage.should_stop(),
    )
