from dataclasses import replace
from pathlib import Path
from typing import Any, Optional

from .event_emitter import ChannelExportEventEmitter
from .jsonl_renderer import ChannelJsonlRenderer
from .manifest_writer import ChannelManifestWriter
from .media_downloader import ChannelMediaDownloader
from .media_manifest_writer import ChannelMediaManifestWriter
from .media_processor import ChannelExportMediaProcessor
from .media_policy import validate_media_mode
from .run_changelog import ChannelRunChangelogWriter
from .discussions import (
    ChannelDiscussionExporter,
    ChannelDiscussionFetcher,
    ChannelDiscussionResolver,
    validate_discussion_mode,
    validate_max_comments_per_post,
)
from .models import (
    CHANNEL_EXPORT_RUN_MODE_FORCE_FULL,
    CHANNEL_EXPORT_RUN_MODE_INCREMENTAL,
    ChannelExportOptions,
    ChannelExportResult,
)
from .payload_writer import ChannelPayloadWriter
from .plan_builder import ChannelExportPlanBuilder
from .post_fetcher import ChannelPostFetcher
from .post_mapper import ChannelPostMapper
from .size_parser import DEFAULT_MAX_MEDIA_SIZE_BYTES
from .source_resolver import ChannelSourceResolver
from .state_manager import ChannelExportStateManager
from .txt_renderer import ChannelTxtRenderer
from .workflows import (
    ChannelExportWorkflowContext,
    run_full_export,
    run_incremental_export,
)


class ChannelExportService:
    def __init__(
        self,
        *,
        client: Any,
        base_dir: Path,
        event_sink=None,
        source_resolver: Optional[ChannelSourceResolver] = None,
        post_fetcher: Optional[ChannelPostFetcher] = None,
        post_mapper: Optional[ChannelPostMapper] = None,
        plan_builder: Optional[ChannelExportPlanBuilder] = None,
        jsonl_renderer: Optional[ChannelJsonlRenderer] = None,
        txt_renderer: Optional[ChannelTxtRenderer] = None,
        media_manifest_writer: Optional[ChannelMediaManifestWriter] = None,
        manifest_writer: Optional[ChannelManifestWriter] = None,
        payload_writer: Optional[ChannelPayloadWriter] = None,
        run_changelog_writer: Optional[ChannelRunChangelogWriter] = None,
        media_downloader: Optional[ChannelMediaDownloader] = None,
        discussion_resolver: Optional[ChannelDiscussionResolver] = None,
        discussion_exporter: Optional[ChannelDiscussionExporter] = None,
        state_manager: Optional[ChannelExportStateManager] = None,
        event_emitter: Optional[ChannelExportEventEmitter] = None,
        progress_interval: int = 100,
    ):
        self.client = client
        self.base_dir = Path(base_dir)
        self.source_resolver = source_resolver or ChannelSourceResolver(client)
        self.post_fetcher = post_fetcher or ChannelPostFetcher(client)
        self.post_mapper = post_mapper or ChannelPostMapper(media_policy=object())
        self.plan_builder = plan_builder or ChannelExportPlanBuilder()
        self.jsonl_renderer = jsonl_renderer or ChannelJsonlRenderer()
        self.txt_renderer = txt_renderer or ChannelTxtRenderer()
        self.media_manifest_writer = (
            media_manifest_writer or ChannelMediaManifestWriter()
        )
        self.manifest_writer = manifest_writer or ChannelManifestWriter()
        self.payload_writer = payload_writer or ChannelPayloadWriter()
        self.run_changelog_writer = run_changelog_writer or ChannelRunChangelogWriter()
        self.media_downloader = media_downloader or ChannelMediaDownloader(client)
        self.discussion_resolver = discussion_resolver or ChannelDiscussionResolver(
            client
        )
        self.discussion_exporter = discussion_exporter or ChannelDiscussionExporter(
            fetcher=ChannelDiscussionFetcher(client)
        )
        self.state_manager = state_manager or ChannelExportStateManager()
        self.event_emitter = event_emitter or ChannelExportEventEmitter(event_sink)
        self.media_processor = ChannelExportMediaProcessor(
            media_downloader=self.media_downloader,
            event_emitter=self.event_emitter,
        )
        self.progress_interval = max(1, int(progress_interval))

    async def export_channel(
        self, options: ChannelExportOptions
    ) -> ChannelExportResult:
        media_mode = validate_media_mode(options.media_mode)
        discussion_mode = validate_discussion_mode(options.discussion_mode)
        max_comments_per_post = validate_max_comments_per_post(
            options.max_comments_per_post
        )
        options = self._normalize_options(
            options,
            media_mode,
            discussion_mode,
            max_comments_per_post,
        )
        self.media_processor.reset_progress()
        workflow = self._build_workflow_context()
        plan = None
        channel_identity = None
        run_mode = None

        try:
            entity, channel_identity = await self.source_resolver.resolve(
                options.channel
            )
            plan = self.plan_builder.build(
                options.output_dir if options.output_dir else self.base_dir,
                channel_identity,
            )
            self.event_emitter.emit_started(
                channel=options.channel,
                output_dir=str(plan.output_dir),
                media_mode=media_mode,
                force=options.force,
            )
            self.event_emitter.emit_channel_resolved(
                channel_id=channel_identity.channel_id,
                channel_username=channel_identity.username,
                channel_title=channel_identity.title,
                output_dir=str(plan.output_dir),
            )

            state = None
            if options.force:
                run_mode = self.state_manager.determine_run_mode(None, force=True)
                self.event_emitter.emit_state_loaded(
                    state_path=str(plan.state_path),
                    state_present=self.state_manager.state_exists(plan.state_path),
                    ignored=True,
                    run_mode=run_mode,
                    last_exported_message_id=None,
                )
            else:
                state = self.state_manager.load(plan.state_path)
                if state is not None:
                    self.state_manager.validate_state_for_channel(
                        state, channel_identity
                    )
                run_mode = self.state_manager.determine_run_mode(state, force=False)
                self.event_emitter.emit_state_loaded(
                    state_path=str(plan.state_path),
                    state_present=state is not None,
                    ignored=False,
                    run_mode=run_mode,
                    last_exported_message_id=(
                        state.last_exported_message_id if state is not None else None
                    ),
                )

            if run_mode == CHANNEL_EXPORT_RUN_MODE_INCREMENTAL and state is not None:
                return await run_incremental_export(
                    workflow,
                    entity=entity,
                    channel_identity=channel_identity,
                    plan=plan,
                    options=options,
                    media_mode=media_mode,
                    state=state,
                )

            return await run_full_export(
                workflow,
                entity=entity,
                channel_identity=channel_identity,
                plan=plan,
                options=options,
                media_mode=media_mode,
                run_mode=run_mode or CHANNEL_EXPORT_RUN_MODE_FORCE_FULL,
            )
        except Exception as exc:
            self.event_emitter.emit_failed(
                channel=options.channel,
                output_dir=str(plan.output_dir) if plan is not None else None,
                run_mode=run_mode,
                error=str(exc),
            )
            raise

    def _build_workflow_context(self) -> ChannelExportWorkflowContext:
        return ChannelExportWorkflowContext(
            post_fetcher=self.post_fetcher,
            post_mapper=self.post_mapper,
            media_processor=self.media_processor,
            payload_writer=self.payload_writer,
            jsonl_renderer=self.jsonl_renderer,
            txt_renderer=self.txt_renderer,
            media_manifest_writer=self.media_manifest_writer,
            manifest_writer=self.manifest_writer,
            run_changelog_writer=self.run_changelog_writer,
            state_manager=self.state_manager,
            discussion_resolver=self.discussion_resolver,
            discussion_exporter=self.discussion_exporter,
            event_emitter=self.event_emitter,
            progress_interval=self.progress_interval,
        )

    @staticmethod
    def _normalize_options(
        options: ChannelExportOptions,
        media_mode: str,
        discussion_mode: str,
        max_comments_per_post: int,
    ) -> ChannelExportOptions:
        options = replace(
            options,
            discussion_mode=discussion_mode,
            max_comments_per_post=max_comments_per_post,
        )
        if media_mode == "full" and options.max_media_size is None:
            return replace(options, max_media_size=DEFAULT_MAX_MEDIA_SIZE_BYTES)
        return options
