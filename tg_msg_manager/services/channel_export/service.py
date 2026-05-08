from pathlib import Path
from typing import Any, Optional

from .event_emitter import ChannelExportEventEmitter
from .jsonl_renderer import ChannelJsonlRenderer
from .manifest_writer import ChannelManifestWriter, build_manifest
from .media_manifest_writer import ChannelMediaManifestWriter
from .media_policy import validate_media_mode
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
        self.state_manager = state_manager or ChannelExportStateManager()
        self.event_emitter = event_emitter or ChannelExportEventEmitter(event_sink)
        self.progress_interval = max(1, int(progress_interval))

    async def export_channel(
        self, options: ChannelExportOptions
    ) -> ChannelExportResult:
        media_mode = validate_media_mode(options.media_mode)
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
            async for message in self.post_fetcher.iter_posts(
                entity,
                limit=options.limit,
            ):
                session.write_record(
                    self.post_mapper.map_post(
                        message,
                        channel_identity,
                        media_mode=media_mode,
                    )
                )
            run_stats = session.finish()

        completed_state = self.state_manager.build_completed_state(
            channel=channel_identity,
            stats=run_stats,
            manifest_path=plan.manifest_path,
        )
        manifest = self._build_manifest(
            channel=channel_identity,
            state=completed_state,
            media_mode=media_mode,
            included_files=self._included_files(options),
        )
        self.manifest_writer.write(plan.manifest_path, manifest)
        self.state_manager.save(plan.state_path, completed_state)
        return self._build_result(
            channel=channel_identity,
            plan=plan,
            run_mode=run_mode,
            state=completed_state,
            run_stats=run_stats,
        )

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
                self.post_mapper.map_post(
                    message,
                    channel_identity,
                    media_mode=media_mode,
                )
            )

        mapped_records.sort(key=lambda record: (record.message_id, record.timestamp))
        if not mapped_records:
            manifest = self._build_manifest(
                channel=channel_identity,
                state=state,
                media_mode=media_mode,
                included_files=self._included_files(options),
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
                skipped_media_count=0,
                date_from=None,
                date_to=None,
                last_exported_message_id=state.last_exported_message_id,
            )
            return self._build_result(
                channel=channel_identity,
                plan=plan,
                run_mode=CHANNEL_EXPORT_RUN_MODE_INCREMENTAL,
                state=state,
                run_stats=empty_stats,
            )

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

        completed_state = self.state_manager.build_completed_state(
            channel=channel_identity,
            stats=run_stats,
            manifest_path=plan.manifest_path,
            previous_state=state,
        )
        manifest = self._build_manifest(
            channel=channel_identity,
            state=completed_state,
            media_mode=media_mode,
            included_files=self._included_files(options),
        )
        self.manifest_writer.write(plan.manifest_path, manifest)
        self.state_manager.save(plan.state_path, completed_state)
        return self._build_result(
            channel=channel_identity,
            plan=plan,
            run_mode=CHANNEL_EXPORT_RUN_MODE_INCREMENTAL,
            state=completed_state,
            run_stats=run_stats,
        )

    def _build_manifest(
        self,
        *,
        channel: Any,
        state: ChannelExportState,
        media_mode: str,
        included_files: tuple[str, ...],
    ) -> dict[str, Any]:
        return build_manifest(
            channel=channel,
            message_count=state.message_count_total,
            media_count=state.media_count_total,
            downloaded_media_count=state.downloaded_media_count_total,
            skipped_media_count=state.skipped_media_count_total,
            date_from=state.date_from,
            date_to=state.date_to,
            media_mode=media_mode,
            included_files=included_files,
            status=state.last_run_status,
        )

    def _build_result(
        self,
        *,
        channel: Any,
        plan: Any,
        run_mode: str,
        state: ChannelExportState,
        run_stats: ChannelExportRunStats,
    ) -> ChannelExportResult:
        result = ChannelExportResult(
            channel=channel,
            run_mode=run_mode,
            message_count=state.message_count_total,
            media_count=state.media_count_total,
            posts_exported_this_run=run_stats.posts_exported,
            media_records_added_this_run=run_stats.media_records_added,
            downloaded_media_count=state.downloaded_media_count_total,
            skipped_media_count=state.skipped_media_count_total,
            manifest_path=plan.manifest_path,
            messages_jsonl_path=plan.messages_jsonl_path,
            messages_txt_path=plan.messages_txt_path,
            media_manifest_path=plan.media_manifest_path,
            state_path=plan.state_path,
        )
        self.event_emitter.emit_completed(
            channel_id=channel.channel_id,
            run_mode=run_mode,
            posts_exported_this_run=result.posts_exported_this_run,
            total_known_posts=result.message_count,
            media_records_added_this_run=result.media_records_added_this_run,
            total_known_media=result.media_count,
            manifest_path=str(result.manifest_path),
            state_path=str(result.state_path),
        )
        return result

    def _emit_progress(self, payload: dict[str, object]) -> None:
        event_payload = dict(payload)
        event_payload["elapsed_seconds"] = round(
            self.event_emitter.elapsed_seconds(),
            3,
        )
        self.event_emitter.emit_progress(**event_payload)

    @staticmethod
    def _included_files(options: ChannelExportOptions) -> tuple[str, ...]:
        included = ["manifest.json", "media_manifest.jsonl"]
        if options.include_jsonl:
            included.append("messages.jsonl")
        if options.include_txt:
            included.append("messages.txt")
        return tuple(included)
