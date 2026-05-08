from typing import Any

from .models import (
    ChannelExportOptions,
    ChannelExportResult,
    ChannelExportRunStats,
    ChannelExportState,
)


def build_channel_export_result(
    *,
    channel: Any,
    plan: Any,
    options: ChannelExportOptions,
    run_mode: str,
    state: ChannelExportState,
    run_stats: ChannelExportRunStats,
    discussion_result: Any = None,
) -> ChannelExportResult:
    return ChannelExportResult(
        channel=channel,
        run_mode=run_mode,
        media_mode=options.media_mode,
        max_media_size=options.max_media_size,
        media_types=options.media_types,
        message_count=state.message_count_total,
        media_count=state.media_count_total,
        posts_exported_this_run=run_stats.posts_exported,
        media_records_added_this_run=run_stats.media_records_added,
        downloaded_media_count_this_run=run_stats.downloaded_media_count,
        already_existing_media_count_this_run=run_stats.already_existing_media_count,
        skipped_by_size_count_this_run=run_stats.skipped_by_size_count,
        skipped_by_type_count_this_run=run_stats.skipped_by_type_count,
        failed_media_count_this_run=run_stats.failed_media_count,
        downloaded_media_count=state.downloaded_media_count_total,
        already_existing_media_count=state.already_existing_media_count_total,
        skipped_media_count=state.skipped_media_count_total,
        skipped_by_size_count=state.skipped_by_size_count_total,
        skipped_by_type_count=state.skipped_by_type_count_total,
        failed_media_count=state.failed_media_count_total,
        manifest_path=plan.manifest_path,
        messages_jsonl_path=plan.messages_jsonl_path,
        messages_txt_path=plan.messages_txt_path,
        media_manifest_path=plan.media_manifest_path,
        state_path=plan.state_path,
        discussion_mode=options.discussion_mode,
        discussion_chat_id=(
            discussion_result.discussion_chat_id
            if discussion_result is not None
            else None
        ),
        discussion_thread_count_this_run=(
            discussion_result.thread_count if discussion_result is not None else 0
        ),
        discussion_comment_count_this_run=(
            discussion_result.comment_count if discussion_result is not None else 0
        ),
        failed_discussion_thread_count_this_run=(
            discussion_result.failed_thread_count
            if discussion_result is not None
            else 0
        ),
        discussion_comments_jsonl_path=(
            discussion_result.comments_jsonl_path
            if discussion_result is not None
            else None
        ),
        discussion_comments_txt_path=(
            discussion_result.comments_txt_path
            if discussion_result is not None
            else None
        ),
        discussion_threads_jsonl_path=(
            discussion_result.threads_jsonl_path
            if discussion_result is not None
            else None
        ),
        discussion_state_path=(
            discussion_result.state_path if discussion_result is not None else None
        ),
    )
