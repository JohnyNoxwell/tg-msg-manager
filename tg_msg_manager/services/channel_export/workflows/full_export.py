from typing import Any

from ..manifest_coordinator import build_channel_export_manifest
from ..models import ChannelExportOptions, ChannelExportResult
from ..payload_writer import WRITE_MODE_OVERWRITE
from ..result_builder import build_channel_export_result
from .context import ChannelExportWorkflowContext


async def run_full_export(
    workflow: ChannelExportWorkflowContext,
    *,
    entity: Any,
    channel_identity: Any,
    plan: Any,
    options: ChannelExportOptions,
    media_mode: str,
    run_mode: str,
) -> ChannelExportResult:
    write_session = workflow.payload_writer.open_session(
        plan=plan,
        jsonl_renderer=workflow.jsonl_renderer,
        txt_renderer=workflow.txt_renderer,
        media_manifest_writer=workflow.media_manifest_writer,
        run_mode=run_mode,
        write_mode=WRITE_MODE_OVERWRITE,
        include_jsonl=options.include_jsonl,
        include_txt=options.include_txt,
        progress_callback=workflow.emit_progress,
        progress_interval=workflow.progress_interval,
    )

    with write_session as session:
        current_run_records = []
        async for message in workflow.post_fetcher.iter_posts(
            entity,
            limit=options.limit,
        ):
            mapped_record = await workflow.prepare_record(
                message=message,
                channel_identity=channel_identity,
                options=options,
                media_mode=media_mode,
                output_dir=plan.output_dir,
            )
            session.write_record(mapped_record)
            current_run_records.append(mapped_record)
        run_stats = session.finish()

    discussion_result = await workflow.export_discussions_for_posts(
        entity=entity,
        channel_identity=channel_identity,
        plan=plan,
        options=options,
        run_mode=run_mode,
        posts=current_run_records,
    )
    completed_state = workflow.state_manager.build_completed_state(
        channel=channel_identity,
        stats=run_stats,
        manifest_path=plan.manifest_path,
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
        run_mode=run_mode,
        previous_state=None,
        completed_state=completed_state,
        run_stats=run_stats,
        posts=tuple(current_run_records),
    )
    workflow.state_manager.save(plan.state_path, completed_state)
    if discussion_result is not None:
        workflow.discussion_exporter.save_result_state(discussion_result)
    result = build_channel_export_result(
        channel=channel_identity,
        plan=plan,
        options=options,
        run_mode=run_mode,
        state=completed_state,
        run_stats=run_stats,
        discussion_result=discussion_result,
    )
    workflow.emit_completed(result)
    return result
