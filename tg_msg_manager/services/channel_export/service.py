from dataclasses import replace
from pathlib import Path
from typing import Any, Optional

from .event_emitter import ChannelExportEventEmitter
from .manifest_coordinator import build_channel_export_manifest
from .jsonl_renderer import ChannelJsonlRenderer
from .manifest_writer import ChannelManifestWriter
from .media_downloader import ChannelMediaDownloader
from .media_manifest_writer import ChannelMediaManifestWriter
from .media_processor import ChannelExportMediaProcessor
from .media_policy import validate_media_mode
from .result_builder import build_channel_export_result
from .discussions import (
    DISCUSSION_MODE_FULL,
    DISCUSSION_MODE_METADATA,
    DISCUSSION_MODE_NONE,
    DISCUSSION_SOURCE_STATUS_DISABLED,
    ChannelDiscussionExporter,
    ChannelDiscussionFetcher,
    ChannelDiscussionOptions,
    ChannelDiscussionResolver,
    ChannelDiscussionSource,
    validate_discussion_mode,
    validate_max_comments_per_post,
)
from .models import (
    CHANNEL_EXPORT_RUN_MODE_FORCE_FULL,
    CHANNEL_EXPORT_RUN_MODE_INCREMENTAL,
    ChannelExportOptions,
    ChannelExportResult,
    ChannelExportRunStats,
    ChannelExportState,
)
from .payload_writer import (
    WRITE_MODE_APPEND,
    WRITE_MODE_OVERWRITE,
    ChannelPayloadWriter,
)
from .plan_builder import ChannelExportPlanBuilder
from .post_fetcher import ChannelPostFetcher
from .post_mapper import ChannelPostMapper
from .size_parser import DEFAULT_MAX_MEDIA_SIZE_BYTES
from .source_resolver import ChannelSourceResolver
from .state_manager import ChannelExportStateManager
from .txt_renderer import ChannelTxtRenderer


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
                return await self._run_incremental_export(
                    entity=entity,
                    channel_identity=channel_identity,
                    plan=plan,
                    options=options,
                    media_mode=media_mode,
                    state=state,
                )

            return await self._run_full_export(
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

    async def _run_full_export(
        self,
        *,
        entity: Any,
        channel_identity: Any,
        plan: Any,
        options: ChannelExportOptions,
        media_mode: str,
        run_mode: str,
    ) -> ChannelExportResult:
        write_session = self.payload_writer.open_session(
            plan=plan,
            jsonl_renderer=self.jsonl_renderer,
            txt_renderer=self.txt_renderer,
            media_manifest_writer=self.media_manifest_writer,
            run_mode=run_mode,
            write_mode=WRITE_MODE_OVERWRITE,
            include_jsonl=options.include_jsonl,
            include_txt=options.include_txt,
            progress_callback=self._emit_progress,
            progress_interval=self.progress_interval,
        )

        with write_session as session:
            current_run_records = []
            async for message in self.post_fetcher.iter_posts(
                entity,
                limit=options.limit,
            ):
                mapped_record = await self._prepare_record(
                    message=message,
                    channel_identity=channel_identity,
                    options=options,
                    media_mode=media_mode,
                    output_dir=plan.output_dir,
                )
                session.write_record(mapped_record)
                current_run_records.append(mapped_record)
            run_stats = session.finish()

        discussion_result = await self._export_discussions_for_posts(
            entity=entity,
            channel_identity=channel_identity,
            plan=plan,
            options=options,
            run_mode=run_mode,
            posts=current_run_records,
        )
        completed_state = self.state_manager.build_completed_state(
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
        self.manifest_writer.write(plan.manifest_path, manifest)
        self.state_manager.save(plan.state_path, completed_state)
        if discussion_result is not None:
            self.discussion_exporter.save_result_state(discussion_result)
        result = build_channel_export_result(
            channel=channel_identity,
            plan=plan,
            options=options,
            run_mode=run_mode,
            state=completed_state,
            run_stats=run_stats,
            discussion_result=discussion_result,
        )
        self._emit_completed(result)
        return result

    async def _run_incremental_export(
        self,
        *,
        entity: Any,
        channel_identity: Any,
        plan: Any,
        options: ChannelExportOptions,
        media_mode: str,
        state: ChannelExportState,
    ) -> ChannelExportResult:
        mapped_records = []
        async for message in self.post_fetcher.iter_posts(
            entity,
            limit=options.limit,
            min_message_id=state.last_exported_message_id,
        ):
            mapped_records.append(
                await self._prepare_record(
                    message=message,
                    channel_identity=channel_identity,
                    options=options,
                    media_mode=media_mode,
                    output_dir=plan.output_dir,
                )
            )

        mapped_records.sort(key=lambda record: (record.message_id, record.timestamp))
        if not mapped_records:
            manifest = build_channel_export_manifest(
                channel=channel_identity,
                state=state,
                options=options,
                media_mode=media_mode,
                discussion_result=None,
            )
            self.manifest_writer.write(plan.manifest_path, manifest)
            self.event_emitter.emit_no_new_posts(
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
            result = build_channel_export_result(
                channel=channel_identity,
                plan=plan,
                options=options,
                run_mode=CHANNEL_EXPORT_RUN_MODE_INCREMENTAL,
                state=state,
                run_stats=empty_stats,
                discussion_result=None,
            )
            self._emit_completed(result)
            return result

        write_session = self.payload_writer.open_session(
            plan=plan,
            jsonl_renderer=self.jsonl_renderer,
            txt_renderer=self.txt_renderer,
            media_manifest_writer=self.media_manifest_writer,
            run_mode=CHANNEL_EXPORT_RUN_MODE_INCREMENTAL,
            write_mode=WRITE_MODE_APPEND,
            include_jsonl=options.include_jsonl,
            include_txt=options.include_txt,
            progress_callback=self._emit_progress,
            progress_interval=self.progress_interval,
        )
        with write_session as session:
            for record in mapped_records:
                session.write_record(record)
            run_stats = session.finish()

        previous_discussion_state = None
        if options.discussion_mode == DISCUSSION_MODE_FULL:
            previous_discussion_state = self.discussion_exporter.load_state(
                plan.discussion_state_path
            )
        discussion_result = await self._export_discussions_for_posts(
            entity=entity,
            channel_identity=channel_identity,
            plan=plan,
            options=options,
            run_mode=CHANNEL_EXPORT_RUN_MODE_INCREMENTAL,
            posts=mapped_records,
            previous_discussion_state=previous_discussion_state,
        )
        completed_state = self.state_manager.build_completed_state(
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
        self.manifest_writer.write(plan.manifest_path, manifest)
        self.state_manager.save(plan.state_path, completed_state)
        if discussion_result is not None:
            self.discussion_exporter.save_result_state(discussion_result)
        result = build_channel_export_result(
            channel=channel_identity,
            plan=plan,
            options=options,
            run_mode=CHANNEL_EXPORT_RUN_MODE_INCREMENTAL,
            state=completed_state,
            run_stats=run_stats,
            discussion_result=discussion_result,
        )
        self._emit_completed(result)
        return result

    def _emit_completed(
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

    async def _prepare_record(
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

    async def _export_discussions_for_posts(
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
            channel_identity=channel_identity,
            discussion_source=discussion_source,
            posts=posts,
            plan=plan,
            discussion_options=discussion_options,
            run_mode=run_mode,
            previous_state=previous_discussion_state,
            save_state=False,
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

    def _emit_progress(self, payload: dict[str, object]) -> None:
        event_payload = dict(payload)
        event_payload["elapsed_seconds"] = round(
            self.event_emitter.elapsed_seconds(),
            3,
        )
        self.event_emitter.emit_progress(**event_payload)
