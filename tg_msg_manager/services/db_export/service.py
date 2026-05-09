import logging
import os
from time import perf_counter
from typing import Any, Callable, Dict, List, Optional

from ...core.models.message import MessageData
from ...infrastructure.storage.contracts.db_export_storage import DBExportStorage
from .event_emitter import DBExportEventEmitter
from .jsonl_renderer import DBExportJsonlRenderer
from .manifest_writer import DBExportManifestWriter
from .models import DBExportSource, ExistingExportArtifact
from .payload_writer import DBExportPayloadWriter
from .plan_builder import DBExportPlanBuilder
from .skip_policy import DBExportSkipPolicy
from .source_loader import DBExportSourceLoader
from .state_manager import DBExportStateManager
from .txt_renderer import DBExportTxtRenderer
from ..rendering.txt_profiles import TXT_PROFILE_LEGACY, validate_txt_profile

logger = logging.getLogger(__name__)

EXPORT_RUN_STATUS_SUCCESS = "success"
EXPORT_RUN_STATUS_FAILED = "failed"


class DBExportService:
    """
    Thin orchestration facade for exporting cached messages from SQLite into files.
    """

    def __init__(
        self,
        storage: DBExportStorage,
        *,
        default_output_dir: str = "DB_EXPORTS",
        source_loader: Optional[DBExportSourceLoader] = None,
        plan_builder: Optional[DBExportPlanBuilder] = None,
        skip_policy: Optional[DBExportSkipPolicy] = None,
        state_manager: Optional[DBExportStateManager] = None,
        payload_writer: Optional[DBExportPayloadWriter] = None,
        txt_renderer: Optional[DBExportTxtRenderer] = None,
        jsonl_renderer: Optional[DBExportJsonlRenderer] = None,
        event_emitter: Optional[DBExportEventEmitter] = None,
        manifest_writer: Optional[DBExportManifestWriter] = None,
    ):
        self.storage = storage
        self.default_output_dir = default_output_dir
        self.txt_renderer = txt_renderer or DBExportTxtRenderer()
        self.jsonl_renderer = jsonl_renderer or DBExportJsonlRenderer()
        self.manifest_writer = manifest_writer or DBExportManifestWriter()
        self.source_loader = source_loader or DBExportSourceLoader(storage)
        self.plan_builder = plan_builder or DBExportPlanBuilder(storage)
        self.skip_policy = skip_policy or DBExportSkipPolicy(
            storage, manifest_writer=self.manifest_writer
        )
        self.state_manager = state_manager or DBExportStateManager(
            storage,
            default_output_dir=default_output_dir,
            plan_builder=self.plan_builder,
        )
        self.payload_writer = payload_writer or DBExportPayloadWriter(
            txt_renderer=self.txt_renderer,
            jsonl_renderer=self.jsonl_renderer,
        )
        self.event_emitter = event_emitter or DBExportEventEmitter()

    def _load_export_manifest(
        self, output_dir: str, user_id: int
    ) -> Optional[Dict[str, Any]]:
        return self.manifest_writer.load_manifest(output_dir, user_id)

    def _artifact_paths_exist(self, output_path: str, part_count: int) -> bool:
        return self.skip_policy.artifact_paths_exist(output_path, part_count)

    def _resolve_export_author_name(
        self, user_id: int, messages: List[MessageData]
    ) -> str:
        return self.plan_builder.resolve_author_name(user_id, messages)

    def _resolve_export_author_name_from_rows(
        self, user_id: int, rows: List[Any]
    ) -> str:
        return self.plan_builder.resolve_author_name_from_rows(user_id, rows)

    def format_message(
        self, message: MessageData, as_json: bool = False, json_profile: str = "ai"
    ) -> str:
        if as_json:
            return self.jsonl_renderer.render_message(message, profile=json_profile)
        return self.txt_renderer.format_message(message)

    def _write_batch_size(self, *, as_json: bool, json_profile: str) -> int:
        return self.payload_writer.write_batch_size(
            as_json=as_json, json_profile=json_profile
        )

    def _load_export_source(
        self,
        *,
        user_id: int,
        as_json: bool,
        json_profile: str,
    ) -> Optional[DBExportSource]:
        return self.source_loader.load_full_source(
            user_id=user_id,
            as_json=as_json,
            json_profile=json_profile,
        )

    def _load_incremental_export_source(
        self,
        *,
        user_id: int,
        last_exported_message_ts: int,
        last_exported_message_id: int,
        as_json: bool,
        json_profile: str,
    ) -> Optional[DBExportSource]:
        return self.source_loader.load_incremental_source(
            user_id=user_id,
            last_exported_message_ts=last_exported_message_ts,
            last_exported_message_id=last_exported_message_id,
            as_json=as_json,
            json_profile=json_profile,
        )

    def _prepare_export_plan(
        self,
        *,
        user_id: int,
        output_dir: str,
        source: DBExportSource,
        as_json: bool,
        include_date: bool,
        json_profile: str,
        txt_profile: str,
    ):
        return self.plan_builder.prepare_plan(
            user_id=user_id,
            output_dir=output_dir,
            source=source,
            as_json=as_json,
            include_date=include_date,
            json_profile=json_profile,
            txt_profile=txt_profile,
        )

    def _maybe_skip_unchanged_export(
        self,
        *,
        output_dir: str,
        user_id: int,
        fingerprint: Dict[str, Any],
        source_count: int,
    ) -> Optional[ExistingExportArtifact]:
        decision = self.skip_policy.find_skip_decision(
            output_dir=output_dir,
            user_id=user_id,
            fingerprint=fingerprint,
        )
        if not decision.should_skip or decision.artifact is None:
            return None
        self.event_emitter.emit_skipped_unchanged(
            user_id=user_id,
            source_count=source_count,
            artifact=decision.artifact,
        )
        return decision.artifact

    def _cleanup_existing_export_files(
        self,
        *,
        output_dir: str,
        user_id: int,
        ext: str,
        output_path: str,
    ) -> None:
        self.payload_writer.cleanup_existing_export_files(
            output_dir=output_dir,
            user_id=user_id,
            ext=ext,
            output_path=output_path,
        )

    def _extract_export_cursor(
        self,
        *,
        source: DBExportSource,
        fingerprint: Dict[str, Any],
    ) -> tuple[Optional[int], Optional[int]]:
        return self.state_manager.extract_export_cursor(
            source=source,
            fingerprint=fingerprint,
        )

    def _upsert_export_target_state(
        self,
        *,
        user_id: int,
        output_path: str,
        target_author: str,
        source: DBExportSource,
        fingerprint: Dict[str, Any],
        part_count: Optional[int] = None,
    ) -> None:
        self.state_manager.upsert_export_target_state(
            user_id=user_id,
            output_path=output_path,
            target_author=target_author,
            source=source,
            fingerprint=fingerprint,
            part_count=part_count,
        )

    def _start_export_run(self, *, user_id: int) -> Optional[int]:
        return self.state_manager.start_run(user_id=user_id)

    def _resolve_existing_export_path(
        self,
        *,
        export_target: Any,
        fallback_output_dir: str,
    ) -> Optional[str]:
        return self.state_manager.resolve_existing_export_path(
            export_target=export_target,
            fallback_output_dir=fallback_output_dir,
        )

    def _supports_incremental_update(
        self,
        *,
        export_target: Any,
        output_dir: Optional[str],
        as_json: bool,
        include_date: bool,
        json_profile: str,
    ) -> bool:
        return self.state_manager.supports_incremental_update(
            export_target=export_target,
            output_dir=output_dir,
            as_json=as_json,
            include_date=include_date,
            json_profile=json_profile,
        )

    def _refresh_export_target_artifact_from_db_state(
        self,
        *,
        user_id: int,
        output_path: str,
        as_json: bool,
        include_date: bool,
        json_profile: str,
        part_count: int,
    ) -> None:
        self.state_manager.refresh_export_target_artifact_from_db_state(
            user_id=user_id,
            output_path=output_path,
            as_json=as_json,
            include_date=include_date,
            json_profile=json_profile,
            part_count=part_count,
        )

    def _finish_export_run(
        self,
        run_id: Optional[int],
        *,
        status: str,
        new_messages_count: int = 0,
        last_new_message_ts: Optional[int] = None,
        error: Optional[str] = None,
    ) -> None:
        self.state_manager.finish_run(
            run_id,
            status=status,
            new_messages_count=new_messages_count,
            last_new_message_ts=last_new_message_ts,
            error=error,
        )

    async def _write_export_payloads(
        self,
        *,
        source: DBExportSource,
        output_path: str,
        as_json: bool,
        json_profile: str,
        txt_profile: str,
        expected_count: int,
        target_user_id: int,
        target_author: str,
        overwrite: bool = True,
        on_progress: Optional[Callable[[int, Any], None]] = None,
    ):
        writer, result = await self.payload_writer.write_payloads(
            source=source,
            output_path=output_path,
            as_json=as_json,
            json_profile=json_profile,
            txt_profile=txt_profile,
            expected_count=expected_count,
            target_user_id=target_user_id,
            target_author=target_author,
            overwrite=overwrite,
            on_progress=on_progress,
        )
        return writer, result.count

    async def export_user_messages(
        self,
        user_id: int,
        output_dir: Optional[str] = None,
        as_json: bool = False,
        include_date: bool = False,
        json_profile: str = "ai",
        txt_profile: str = TXT_PROFILE_LEGACY,
    ) -> str:
        txt_profile = validate_txt_profile(txt_profile)
        started_at = perf_counter()
        resolved_output_dir = output_dir or self.default_output_dir
        processed_count = 0
        processed_last_ts: Optional[int] = None
        run_id = self._start_export_run(user_id=user_id)

        def track_progress(count: int, item: Any) -> None:
            nonlocal processed_count, processed_last_ts
            processed_count = count
            timestamp = getattr(item, "timestamp", None)
            if timestamp is None and isinstance(item, dict):
                timestamp = item.get("timestamp")
            if hasattr(timestamp, "timestamp"):
                processed_last_ts = int(timestamp.timestamp())
            elif timestamp is not None:
                processed_last_ts = int(timestamp)

        try:
            source = self._load_export_source(
                user_id=user_id,
                as_json=as_json,
                json_profile=json_profile,
            )
            if source is None:
                logger.warning("No messages found in DB for user %s", user_id)
                self._finish_export_run(
                    run_id,
                    status=EXPORT_RUN_STATUS_SUCCESS,
                    new_messages_count=0,
                )
                return ""

            if not os.path.exists(resolved_output_dir):
                os.makedirs(resolved_output_dir)

            plan = self._prepare_export_plan(
                user_id=user_id,
                output_dir=resolved_output_dir,
                source=source,
                as_json=as_json,
                include_date=include_date,
                json_profile=json_profile,
                txt_profile=txt_profile,
            )
            unchanged = self._maybe_skip_unchanged_export(
                output_dir=resolved_output_dir,
                user_id=user_id,
                fingerprint=plan.fingerprint,
                source_count=source.source_count,
            )
            if unchanged:
                self._upsert_export_target_state(
                    user_id=user_id,
                    output_path=unchanged.output_path,
                    target_author=plan.target_author,
                    source=source,
                    fingerprint=plan.fingerprint,
                    part_count=unchanged.part_count,
                )
                self._finish_export_run(
                    run_id,
                    status=EXPORT_RUN_STATUS_SUCCESS,
                    new_messages_count=0,
                )
                return unchanged.output_path

            self._cleanup_existing_export_files(
                output_dir=resolved_output_dir,
                user_id=user_id,
                ext=plan.ext,
                output_path=plan.output_path,
            )
            writer, count = await self._write_export_payloads(
                source=source,
                output_path=plan.output_path,
                as_json=as_json,
                json_profile=json_profile,
                txt_profile=txt_profile,
                expected_count=source.source_count,
                target_user_id=user_id,
                target_author=plan.target_author,
                overwrite=True,
                on_progress=track_progress,
            )
            elapsed_seconds = perf_counter() - started_at
            self.event_emitter.emit_completed(
                user_id=user_id,
                count=count,
                as_json=as_json,
                output_path=plan.output_path,
                elapsed_seconds=elapsed_seconds,
                write_calls=writer.write_calls,
                bytes_written=writer.bytes_written,
                rotation_count=writer.rotation_count,
                state_persist_count=writer.state_persist_count,
            )
            self._upsert_export_target_state(
                user_id=user_id,
                output_path=plan.output_path,
                target_author=plan.target_author,
                source=source,
                fingerprint=plan.fingerprint,
                part_count=writer.current_part,
            )
            last_ts, _last_message_id = self._extract_export_cursor(
                source=source,
                fingerprint=plan.fingerprint,
            )
            self._finish_export_run(
                run_id,
                status=EXPORT_RUN_STATUS_SUCCESS,
                new_messages_count=count,
                last_new_message_ts=last_ts,
            )
            logger.info(
                "DB Export complete for %s: %s messages.", plan.target_author, count
            )
            return plan.output_path
        except Exception as exc:
            self._finish_export_run(
                run_id,
                status=EXPORT_RUN_STATUS_FAILED,
                new_messages_count=processed_count,
                last_new_message_ts=processed_last_ts,
                error=str(exc),
            )
            raise

    async def update_user_messages(
        self,
        user_id: int,
        output_dir: Optional[str] = None,
        as_json: bool = True,
        include_date: bool = False,
        json_profile: str = "ai",
        txt_profile: str = TXT_PROFILE_LEGACY,
    ) -> str:
        txt_profile = validate_txt_profile(txt_profile)
        resolved_output_dir = output_dir or self.default_output_dir
        export_target = self.state_manager.get_export_target(user_id)
        if not self._supports_incremental_update(
            export_target=export_target,
            output_dir=output_dir,
            as_json=as_json,
            include_date=include_date,
            json_profile=json_profile,
        ):
            return await self.export_user_messages(
                user_id,
                output_dir=output_dir,
                as_json=as_json,
                include_date=include_date,
                json_profile=json_profile,
                txt_profile=txt_profile,
            )

        output_path = self._resolve_existing_export_path(
            export_target=export_target,
            fallback_output_dir=resolved_output_dir,
        )
        if not output_path or not os.path.exists(output_path):
            return await self.export_user_messages(
                user_id,
                output_dir=output_dir,
                as_json=as_json,
                include_date=include_date,
                json_profile=json_profile,
                txt_profile=txt_profile,
            )

        last_ts = int(getattr(export_target, "last_exported_message_ts"))
        last_message_id = int(getattr(export_target, "last_exported_message_id"))
        run_id = self._start_export_run(user_id=user_id)
        processed_count = 0
        processed_last_ts: Optional[int] = None

        def track_progress(count: int, item: Any) -> None:
            nonlocal processed_count, processed_last_ts
            processed_count = count
            timestamp = getattr(item, "timestamp", None)
            if timestamp is None and isinstance(item, dict):
                timestamp = item.get("timestamp")
            processed_last_ts = int(timestamp) if timestamp is not None else None

        try:
            source = self._load_incremental_export_source(
                user_id=user_id,
                last_exported_message_ts=last_ts,
                last_exported_message_id=last_message_id,
                as_json=as_json,
                json_profile=json_profile,
            )
            if source is None:
                self._finish_export_run(
                    run_id,
                    status=EXPORT_RUN_STATUS_SUCCESS,
                    new_messages_count=0,
                )
                return output_path

            writer, count = await self._write_export_payloads(
                source=source,
                output_path=output_path,
                as_json=as_json,
                json_profile=json_profile,
                txt_profile=txt_profile,
                expected_count=source.source_count,
                target_user_id=user_id,
                target_author=getattr(export_target, "last_known_author_name", None)
                or f"User_{user_id}",
                overwrite=False,
                on_progress=track_progress,
            )
            self._refresh_export_target_artifact_from_db_state(
                user_id=user_id,
                output_path=output_path,
                as_json=as_json,
                include_date=include_date,
                json_profile=json_profile,
                part_count=writer.current_part,
            )
            self._finish_export_run(
                run_id,
                status=EXPORT_RUN_STATUS_SUCCESS,
                new_messages_count=count,
                last_new_message_ts=processed_last_ts,
            )
            return output_path
        except Exception as exc:
            self._finish_export_run(
                run_id,
                status=EXPORT_RUN_STATUS_FAILED,
                new_messages_count=processed_count,
                last_new_message_ts=processed_last_ts,
                error=str(exc),
            )
            raise
