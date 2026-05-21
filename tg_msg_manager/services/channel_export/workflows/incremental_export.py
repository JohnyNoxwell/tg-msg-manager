from typing import Any

from ..discussions import DISCUSSION_MODE_FULL
from ..manifest_coordinator import build_channel_export_manifest
from ..models import (
    CHANNEL_EXPORT_RUN_MODE_INCREMENTAL,
    ChannelExportOptions,
    ChannelExportResult,
    ChannelExportState,
)
from ..payload_writer import WRITE_MODE_APPEND
from ..result_builder import build_channel_export_result
from .context import ChannelExportWorkflowContext
from .no_new_posts import run_no_new_posts


async def run_incremental_export(
    workflow: ChannelExportWorkflowContext,
    *,
    entity: Any,
    channel_identity: Any,
    plan: Any,
    options: ChannelExportOptions,
    media_mode: str,
    state: ChannelExportState,
) -> ChannelExportResult:
    mapped_records = []
    async for message in workflow.post_fetcher.iter_posts(
        entity,
        limit=options.limit,
        min_message_id=state.last_exported_message_id,
    ):
        mapped_records.append(
            await workflow.prepare_record(
                message=message,
                channel_identity=channel_identity,
                options=options,
                media_mode=media_mode,
                output_dir=plan.output_dir,
            )
        )

    mapped_records.sort(key=lambda record: (record.message_id, record.timestamp))
    if not mapped_records:
        return await run_no_new_posts(
            workflow,
            channel_identity=channel_identity,
            plan=plan,
            options=options,
            media_mode=media_mode,
            state=state,
        )

    write_session = workflow.payload_writer.open_session(
        plan=plan,
        jsonl_renderer=workflow.jsonl_renderer,
        txt_renderer=workflow.txt_renderer,
        media_manifest_writer=workflow.media_manifest_writer,
        run_mode=CHANNEL_EXPORT_RUN_MODE_INCREMENTAL,
        write_mode=WRITE_MODE_APPEND,
        include_jsonl=options.include_jsonl,
        include_txt=options.include_txt,
        progress_callback=workflow.emit_progress,
        progress_interval=workflow.progress_interval,
    )
    with write_session as session:
        for record in mapped_records:
            session.write_record(record)
        run_stats = session.finish()

    previous_discussion_state = None
    if options.discussion_mode == DISCUSSION_MODE_FULL:
        previous_discussion_state = workflow.discussion_exporter.load_state(
            plan.discussion_state_path
        )
    discussion_result = await workflow.export_discussions_for_posts(
        entity=entity,
        channel_identity=channel_identity,
        plan=plan,
        options=options,
        run_mode=CHANNEL_EXPORT_RUN_MODE_INCREMENTAL,
        posts=mapped_records,
        previous_discussion_state=previous_discussion_state,
    )
    completed_state = workflow.state_manager.build_completed_state(
        channel=channel_identity,
        stats=run_stats,
        manifest_path=plan.manifest_path,
        previous_state=state,
    )
    manifest = build_channel_export_manifest(
        channel=channel_identity,
        state=completed_state,
        options=options,
        media_mode=media_mode,
        discussion_result=discussion_result,
    )
    workflow.manifest_writer.write(plan.manifest_path, manifest)
    workflow.write_run_changelog(
        plan=plan,
        channel_identity=channel_identity,
        run_mode=CHANNEL_EXPORT_RUN_MODE_INCREMENTAL,
        previous_state=state,
        completed_state=completed_state,
        run_stats=run_stats,
        posts=tuple(mapped_records),
    )
    workflow.state_manager.save(plan.state_path, completed_state)
    if discussion_result is not None:
        workflow.discussion_exporter.save_result_state(discussion_result)
    result = build_channel_export_result(
        channel=channel_identity,
        plan=plan,
        options=options,
        run_mode=CHANNEL_EXPORT_RUN_MODE_INCREMENTAL,
        state=completed_state,
        run_stats=run_stats,
        discussion_result=discussion_result,
    )
    workflow.emit_completed(result)
    return result
