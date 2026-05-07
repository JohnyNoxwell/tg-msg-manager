from pathlib import Path
from typing import Any, Iterable, Optional

from ...core.service_events import ServiceEventSink, emit_service_event
from .jsonl_renderer import ChannelJsonlRenderer
from .manifest_writer import ChannelManifestWriter, build_manifest
from .media_manifest_writer import ChannelMediaManifestWriter
from .media_policy import validate_media_mode
from .models import ChannelExportOptions, ChannelExportResult
from .payload_writer import ChannelPayloadWriter
from .plan_builder import ChannelExportPlanBuilder
from .post_fetcher import ChannelPostFetcher
from .post_mapper import ChannelPostMapper
from .source_resolver import ChannelSourceResolver
from .txt_renderer import ChannelTxtRenderer


class ChannelExportService:
    def __init__(
        self,
        *,
        client: Any,
        base_dir: Path,
        event_sink: ServiceEventSink = None,
        source_resolver: Optional[ChannelSourceResolver] = None,
        post_fetcher: Optional[ChannelPostFetcher] = None,
        post_mapper: Optional[ChannelPostMapper] = None,
        plan_builder: Optional[ChannelExportPlanBuilder] = None,
        jsonl_renderer: Optional[ChannelJsonlRenderer] = None,
        txt_renderer: Optional[ChannelTxtRenderer] = None,
        media_manifest_writer: Optional[ChannelMediaManifestWriter] = None,
        manifest_writer: Optional[ChannelManifestWriter] = None,
        payload_writer: Optional[ChannelPayloadWriter] = None,
    ):
        self.client = client
        self.base_dir = Path(base_dir)
        self.event_sink = event_sink
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

    async def export_channel(
        self, options: ChannelExportOptions
    ) -> ChannelExportResult:
        media_mode = validate_media_mode(options.media_mode)
        plan = None
        channel_identity = None
        try:
            entity, channel_identity = await self.source_resolver.resolve(
                options.channel
            )
            plan = self.plan_builder.build(
                options.output_dir if options.output_dir else self.base_dir,
                channel_identity,
            )
            self._emit(
                "channel_export.started",
                channel=options.channel,
                output_dir=str(plan.output_dir),
                media_mode=media_mode,
            )
            mapped_records = [
                self.post_mapper.map_post(
                    message,
                    channel_identity,
                    media_mode=media_mode,
                )
                async for message in self.post_fetcher.iter_posts(
                    entity,
                    limit=options.limit,
                )
            ]
            message_count, media_count, date_from, date_to = (
                self.payload_writer.write_records(
                    plan=plan,
                    records=mapped_records,
                    jsonl_renderer=self.jsonl_renderer,
                    txt_renderer=self.txt_renderer,
                    media_manifest_writer=self.media_manifest_writer,
                    include_jsonl=options.include_jsonl,
                    include_txt=options.include_txt,
                )
            )
            downloaded_media_count = self._count_media_with_status(
                mapped_records,
                "downloaded",
            )
            skipped_media_count = self._count_media_with_status(
                mapped_records,
                "skipped_by_mode",
            )
            included_files = self._included_files(options)
            manifest = build_manifest(
                channel=channel_identity,
                message_count=message_count,
                media_count=media_count,
                downloaded_media_count=downloaded_media_count,
                skipped_media_count=skipped_media_count,
                date_from=date_from,
                date_to=date_to,
                media_mode=media_mode,
                included_files=included_files,
                status="completed",
            )
            self.manifest_writer.write(plan.manifest_path, manifest)
            result = ChannelExportResult(
                channel=channel_identity,
                message_count=message_count,
                media_count=media_count,
                downloaded_media_count=downloaded_media_count,
                skipped_media_count=skipped_media_count,
                manifest_path=plan.manifest_path,
                messages_jsonl_path=plan.messages_jsonl_path,
                messages_txt_path=plan.messages_txt_path,
                media_manifest_path=plan.media_manifest_path,
            )
            self._emit(
                "channel_export.completed",
                channel_id=channel_identity.channel_id,
                message_count=message_count,
                media_count=media_count,
                manifest_path=str(plan.manifest_path),
            )
            return result
        except Exception as exc:
            self._emit(
                "channel_export.failed",
                channel=options.channel,
                output_dir=str(plan.output_dir) if plan is not None else None,
                error=str(exc),
            )
            raise

    def _emit(self, event_name: str, **payload: Any) -> None:
        emit_service_event(self.event_sink, event_name, **payload)

    @staticmethod
    def _count_media_with_status(records: Iterable[Any], status: str) -> int:
        return sum(
            1
            for record in records
            for media_record in record.media
            if media_record.download_status == status
        )

    @staticmethod
    def _included_files(options: ChannelExportOptions) -> tuple[str, ...]:
        included = ["manifest.json", "media_manifest.jsonl"]
        if options.include_jsonl:
            included.append("messages.jsonl")
        if options.include_txt:
            included.append("messages.txt")
        return tuple(included)
