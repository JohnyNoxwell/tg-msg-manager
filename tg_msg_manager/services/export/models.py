from dataclasses import dataclass
from typing import Any, Optional

from ...core.models.payloads.export import ExportSyncStartedPayload
from ...infrastructure.storage.records import SyncStatus


@dataclass
class SyncTargetContext:
    chat_id: int
    chat_title: str
    uid: int
    status: SyncStatus
    api_from_user: Optional[Any]
    local_sender_filter_id: Optional[int]
    active_deep: bool
    active_depth: int
    head_id: int
    tail_id: int
    is_complete: bool
    header_payload: ExportSyncStartedPayload
