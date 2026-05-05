from typing import Any, Optional

from ...core.context import set_chat_id
from ...core.models.payloads.export import ExportSyncStartedPayload
from ...core.models.sync_report import TrackedSyncRunReport, TrackedSyncUserStat
from ...infrastructure.storage.records import SyncStatus
from ...utils.ui import UI
from ..sync.targets import (
    resolve_active_sync_mode,
    resolve_status_kind,
    resolve_sync_target_identity,
)
from .models import SyncTargetContext


class SyncTargetResolver:
    def __init__(self, *, client: Any, storage: Any, context_engine: Any):
        self.client = client
        self.storage = storage
        self.context_engine = context_engine

    @staticmethod
    def build_sync_header_payload(
        *,
        chat_title: str,
        user_label: str,
        active_deep: bool,
        active_depth: int,
        status_kind: Optional[str],
    ) -> ExportSyncStartedPayload:
        return ExportSyncStartedPayload(
            chat_title=chat_title,
            user_label=user_label,
            deep_mode=active_deep,
            depth=active_depth if active_deep else 0,
            status_kind=status_kind,
        )

    async def prepare_sync_target(
        self,
        entity: Any,
        *,
        from_user_id: Optional[int],
        deep_mode: bool,
        recursive_depth: int,
        force_resync: bool,
        resume_history: bool,
        resolve_user_entity: bool,
    ) -> SyncTargetContext:
        chat_id = getattr(entity, "id", 0)
        chat_title = UI.format_name(entity)
        set_chat_id(chat_id)
        self.storage.upsert_chat(
            chat_id, chat_title, chat_type=getattr(entity, "_", None)
        )

        uid = from_user_id or chat_id
        status = SyncStatus.coerce(self.storage.get_sync_status(chat_id, uid))
        resolved_target = await resolve_sync_target_identity(
            entity=entity,
            from_user_id=from_user_id,
            resolve_user_entity=resolve_user_entity,
            status=status,
            client=self.client,
            storage=self.storage,
        )

        active_deep, active_depth = resolve_active_sync_mode(
            deep_mode=deep_mode,
            saved_deep=status.deep_mode,
            recursive_depth=recursive_depth,
            saved_depth=status.recursive_depth,
        )
        head_id = 0 if force_resync else status.last_msg_id
        tail_id = 0 if force_resync else status.tail_msg_id
        is_complete = False if force_resync else status.is_complete

        self.storage.register_target(
            resolved_target.uid,
            resolved_target.target_name,
            chat_id,
            deep_mode=active_deep,
            recursive_depth=active_depth,
        )
        if active_deep:
            self.context_engine.reset()

        status_kind = resolve_status_kind(
            resume_history=resume_history,
            tail_id=tail_id,
            is_complete=bool(is_complete),
            head_id=head_id,
        )
        return SyncTargetContext(
            chat_id=chat_id,
            chat_title=chat_title,
            uid=resolved_target.uid,
            status=status,
            api_from_user=resolved_target.api_from_user,
            local_sender_filter_id=resolved_target.local_sender_filter_id,
            active_deep=active_deep,
            active_depth=active_depth,
            head_id=head_id,
            tail_id=tail_id,
            is_complete=is_complete,
            header_payload=self.build_sync_header_payload(
                chat_title=chat_title,
                user_label=resolved_target.user_label,
                active_deep=active_deep,
                active_depth=active_depth,
                status_kind=status_kind,
            ),
        )

    def resolve_target_report_name(
        self,
        *,
        from_user_id: int,
        target_status: SyncStatus,
    ) -> str:
        name = target_status.author_name or f"ID:{from_user_id}"
        if not target_status.author_name or target_status.author_name.startswith("ID:"):
            user_info = self.storage.get_user(from_user_id)
            if user_info:
                first = user_info.get("first_name") or ""
                last = user_info.get("last_name") or ""
                name = f"{first} {last}".strip() or user_info.get("username") or name
        return name

    def ensure_user_stats_entry(
        self,
        *,
        user_stats: TrackedSyncRunReport,
        from_user_id: int,
        target_status: SyncStatus,
    ) -> None:
        if from_user_id in user_stats:
            return
        user_stats[from_user_id] = TrackedSyncUserStat(
            name=self.resolve_target_report_name(
                from_user_id=from_user_id,
                target_status=target_status,
            ),
        )
