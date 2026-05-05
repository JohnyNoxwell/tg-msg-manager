import asyncio
import logging
from time import perf_counter
from typing import Any, Optional, Set

from ...core.models.payloads.export import (
    ExportDialogScanStartedPayload,
    ExportDialogSearchScanningPayload,
    ExportDialogSearchStartedPayload,
    ExportGlobalExportFinishedPayload,
    ExportTargetedDialogSearchStartedPayload,
)
from ...core.service_events import ExportEvents
from ...core.telemetry import telemetry
from ...utils.ui import UI
from ..sync.dialog_targets import (
    filter_group_dialog_entities,
    resolve_targeted_dialog_entities,
)

logger = logging.getLogger(__name__)


class DialogSyncCoordinator:
    def __init__(self, *, client: Any, emit_event, sync_chat):
        self.client = client
        self.emit_event = emit_event
        self.sync_chat = sync_chat

    async def sync_all_dialogs_for_user(
        self,
        from_user_id: int,
        *,
        target_chat_ids: Optional[Set[Any]] = None,
        limit: Optional[int] = None,
        deep_mode: bool = False,
        force_resync: bool = False,
        context_window: int = 3,
        max_cluster: int = 20,
        recursive_depth: int = 3,
    ) -> int:
        if target_chat_ids:
            started_at = perf_counter()
            self.emit_event(
                ExportEvents.TARGETED_DIALOG_SEARCH_STARTED,
                **ExportTargetedDialogSearchStartedPayload(
                    from_user_id=from_user_id,
                    dialog_count=len(target_chat_ids),
                ).as_dict(),
            )
            targets = await resolve_targeted_dialog_entities(
                client=self.client,
                target_chat_ids=target_chat_ids,
            )
        else:
            started_at = perf_counter()
            self.emit_event(
                ExportEvents.DIALOG_SEARCH_STARTED,
                **ExportDialogSearchStartedPayload(from_user_id=from_user_id).as_dict(),
            )
            targets = filter_group_dialog_entities(await self.client.get_dialogs())

        self.emit_event(
            ExportEvents.DIALOG_SEARCH_SCANNING,
            **ExportDialogSearchScanningPayload(dialog_count=len(targets)).as_dict(),
        )

        total_processed = 0
        for i, dialog in enumerate(targets):
            try:
                self.emit_event(
                    ExportEvents.DIALOG_SCAN_STARTED,
                    **ExportDialogScanStartedPayload(
                        index=i + 1,
                        total=len(targets),
                        dialog_title=UI.format_name(dialog),
                    ).as_dict(),
                )
                total_processed += await self.sync_chat(
                    dialog,
                    from_user_id=from_user_id,
                    limit=limit,
                    deep_mode=deep_mode,
                    force_resync=force_resync,
                    context_window=context_window,
                    max_cluster=max_cluster,
                    recursive_depth=recursive_depth,
                    emit_summary=False,
                )
                await asyncio.sleep(0.5)
            except Exception as exc:
                logger.error(
                    "Error scanning dialog %s: %s",
                    getattr(dialog, "name", "Unknown"),
                    exc,
                )

        self.emit_event(
            ExportEvents.GLOBAL_EXPORT_FINISHED,
            **ExportGlobalExportFinishedPayload(
                total_processed=total_processed
            ).as_dict(),
        )
        telemetry.track_counter("sync.dialogs.scanned", len(targets))
        telemetry.track_duration(
            "sync.dialogs_for_user.total", perf_counter() - started_at
        )
        return total_processed
