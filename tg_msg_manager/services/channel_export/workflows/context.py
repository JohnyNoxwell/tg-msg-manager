from pathlib import Path
from typing import Any

from ..discussions import (
    DISCUSSION_MODE_METADATA,
    DISCUSSION_MODE_NONE,
    DISCUSSION_SOURCE_STATUS_DISABLED,
    ChannelDiscussionOptions,
    ChannelDiscussionSource,
)
from ..models import ChannelExportOptions, ChannelExportResult, ChannelExportRunStats
from ..run_changelog import RUN_CHANGELOG_JSONL


class ChannelExportWorkflowContext:
    def __init__(
        self,
        *,
        post_fetcher: Any,
        post_mapper: Any,
        media_processor: Any,
        payload_writer: Any,
        jsonl_renderer: Any,
        txt_renderer: Any,
        media_manifest_writer: Any,
        manifest_writer: Any,
        run_changelog_writer: Any,
        state_manager: Any,
        discussion_resolver: Any,
        discussion_exporter: Any,
        event_emitter: Any,
        progress_interval: int,
    ):
        self.post_fetcher = post_fetcher
        self.post_mapper = post_mapper
        self.media_processor = media_processor
        self.payload_writer = payload_writer
        self.jsonl_renderer = jsonl_renderer
        self.txt_renderer = txt_renderer
        self.media_manifest_writer = media_manifest_writer
        self.manifest_writer = manifest_writer
        self.run_changelog_writer = run_changelog_writer
        self.state_manager = state_manager
        self.discussion_resolver = discussion_resolver
        self.discussion_exporter = discussion_exporter
        self.event_emitter = event_emitter
        self.progress_interval = progress_interval

    def emit_completed(
        self,
        result: ChannelExportResult,
    ) -> None:
        self.event_emitter.emit_completed(
            channel_id=result.channel.channel_id,
            run_mode=result.run_mode,
            posts_exported_this_run=result.posts_exported_this_run,
            total_known_posts=result.message_count,
            media_records_added_this_run=result.media_records_added_this_run,
            total_known_media=result.media_count,
            downloaded_media_count_this_run=result.downloaded_media_count_this_run,
            already_existing_media_count_this_run=result.already_existing_media_count_this_run,
            skipped_by_size_count_this_run=result.skipped_by_size_count_this_run,
            skipped_by_type_count_this_run=result.skipped_by_type_count_this_run,
            failed_media_count_this_run=result.failed_media_count_this_run,
            manifest_path=str(result.manifest_path),
            state_path=str(result.state_path),
        )

    def write_run_changelog(
        self,
        *,
        plan: Any,
        channel_identity: Any,
        run_mode: str,
        previous_state: Any,
        completed_state: Any,
        run_stats: ChannelExportRunStats,
        posts: tuple[Any, ...],
        summary: Any = None,
    ) -> None:
        self.run_changelog_writer.append_entry(
            output_dir=plan.output_dir,
            channel=channel_identity,
            run_mode=run_mode,
            previous_state=previous_state,
            new_state=completed_state,
            run_stats=run_stats,
            posts=posts,
            summary=summary,
            artifact_paths={
                "manifest": "manifest.json",
                "messages_jsonl": "messages.jsonl",
                "messages_txt": "messages.txt",
                "media_manifest": "media_manifest.jsonl",
                "state": "channel_export_state.json",
                "run_changelog": RUN_CHANGELOG_JSONL,
            },
        )

    async def prepare_record(
        self,
        *,
        message: Any,
        channel_identity: Any,
        options: ChannelExportOptions,
        media_mode: str,
        output_dir: Path,
    ):
        mapped_record = self.post_mapper.map_post(
            message,
            channel_identity,
            media_mode=media_mode,
        )
        return await self.media_processor.prepare_record(
            record=mapped_record,
            media_mode=media_mode,
            media_ref=getattr(message, "media_ref", None),
            output_dir=output_dir,
            max_media_size=options.max_media_size,
            media_types=options.media_types,
        )

    async def export_discussions_for_posts(
        self,
        *,
        entity: Any,
        channel_identity: Any,
        plan: Any,
        options: ChannelExportOptions,
        run_mode: str,
        posts: list[Any],
        previous_discussion_state: Any = None,
    ):
        if options.discussion_mode == DISCUSSION_MODE_NONE or not posts:
            return None
        if options.discussion_mode == DISCUSSION_MODE_METADATA:
            discussion_source = ChannelDiscussionSource(
                status=DISCUSSION_SOURCE_STATUS_DISABLED,
                discussion_chat_id=None,
                discussion_entity=None,
                error=None,
            )
        else:
            discussion_source = await self.discussion_resolver.resolve(
                entity, posts=posts
            )
        discussion_options = ChannelDiscussionOptions(
            mode=options.discussion_mode,
            max_comments_per_post=options.max_comments_per_post,
        )
        return await self.discussion_exporter.export_for_posts(
            channel_entity=entity,
            channel_identity=channel_identity,
            discussion_source=discussion_source,
            posts=posts,
            plan=plan,
            discussion_options=discussion_options,
            run_mode=run_mode,
            previous_state=previous_discussion_state,
            save_state=False,
        )

    def emit_progress(self, payload: dict[str, object]) -> None:
        event_payload = dict(payload)
        event_payload["elapsed_seconds"] = round(
            self.event_emitter.elapsed_seconds(),
            3,
        )
        self.event_emitter.emit_progress(**event_payload)
