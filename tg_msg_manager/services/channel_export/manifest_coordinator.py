from typing import Any

from .discussions.manifest_summary import build_discussion_manifest
from .included_files_builder import build_included_files
from .manifest_writer import build_manifest
from .models import ChannelExportOptions, ChannelExportState


def build_channel_export_manifest(
    *,
    channel: Any,
    state: ChannelExportState,
    options: ChannelExportOptions,
    media_mode: str,
    discussion_result: Any = None,
) -> dict[str, Any]:
    return build_manifest(
        channel=channel,
        message_count=state.message_count_total,
        media_count=state.media_count_total,
        downloaded_media_count=state.downloaded_media_count_total,
        already_existing_media_count=state.already_existing_media_count_total,
        skipped_media_count=state.skipped_media_count_total,
        skipped_by_size_count=state.skipped_by_size_count_total,
        skipped_by_type_count=state.skipped_by_type_count_total,
        failed_media_count=state.failed_media_count_total,
        date_from=state.date_from,
        date_to=state.date_to,
        media_mode=media_mode,
        max_media_size=options.max_media_size,
        media_types=options.media_types,
        included_files=build_included_files(options, discussion_result),
        discussion=build_discussion_manifest(
            discussion_mode=options.discussion_mode,
            max_comments_per_post=options.max_comments_per_post,
            discussion_result=discussion_result,
        ),
        status=state.last_run_status,
    )
