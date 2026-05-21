from typing import Any

from ..manifest_coordinator import build_channel_export_manifest
from ..models import (
    CHANNEL_EXPORT_RUN_MODE_INCREMENTAL,
    ChannelExportOptions,
    ChannelExportResult,
    ChannelExportRunStats,
    ChannelExportState,
)
from ..result_builder import build_channel_export_result
from .context import ChannelExportWorkflowContext


async def run_no_new_posts(
    workflow: ChannelExportWorkflowContext,
    *,
    channel_identity: Any,
    plan: Any,
    options: ChannelExportOptions,
    media_mode: str,
    state: ChannelExportState,
) -> ChannelExportResult:
    manifest = build_channel_export_manifest(
        channel=channel_identity,
        state=state,
        options=options,
        media_mode=media_mode,
        discussion_result=None,
    )
    workflow.manifest_writer.write(plan.manifest_path, manifest)
    workflow.event_emitter.emit_no_new_posts(
        channel_id=channel_identity.channel_id,
        state_path=str(plan.state_path),
        last_exported_message_id=state.last_exported_message_id,
        total_known_posts=state.message_count_total,
    )
    empty_stats = ChannelExportRunStats(
        mode=CHANNEL_EXPORT_RUN_MODE_INCREMENTAL,
        posts_exported=0,
        media_records_added=0,
        downloaded_media_count=0,
        already_existing_media_count=0,
        skipped_media_count=0,
        skipped_by_size_count=0,
        skipped_by_type_count=0,
        failed_media_count=0,
        date_from=None,
        date_to=None,
        last_exported_message_id=state.last_exported_message_id,
    )
    workflow.write_run_changelog(
        plan=plan,
        channel_identity=channel_identity,
        run_mode=CHANNEL_EXPORT_RUN_MODE_INCREMENTAL,
        previous_state=state,
        completed_state=state,
        run_stats=empty_stats,
        posts=(),
    )
    result = build_channel_export_result(
        channel=channel_identity,
        plan=plan,
        options=options,
        run_mode=CHANNEL_EXPORT_RUN_MODE_INCREMENTAL,
        state=state,
        run_stats=empty_stats,
        discussion_result=None,
    )
    workflow.emit_completed(result)
    return result
