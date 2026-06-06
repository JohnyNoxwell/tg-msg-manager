from typing import Any, Callable, Dict, List, Optional

from ...core.models.message import MessageData
from ...infrastructure.storage.contracts.db_export_storage import DBExportStorage
from .event_emitter import DBExportEventEmitter
from .jsonl_renderer import DBExportJsonlRenderer
from .manifest_writer import DBExportManifestWriter
from .models import DBExportSource, ExistingExportArtifact
from .payload_writer import DBExportPayloadWriter
from .plan_builder import DBExportPlanBuilder
from .run_coordinator import (
    DBExportFullRunCoordinator,
    DBExportUpdateRunCoordinator,
)
from .skip_policy import DBExportSkipPolicy
from .source_loader import DBExportSourceLoader
from .state_manager import DBExportStateManager
from .txt_renderer import DBExportTxtRenderer
from ..rendering.txt_profiles import DEFAULT_TXT_PROFILE, validate_txt_profile


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
        self.full_run_coordinator = DBExportFullRunCoordinator(
            source_loader=self.source_loader,
            plan_builder=self.plan_builder,
            skip_policy=self.skip_policy,
            state_manager=self.state_manager,
            payload_writer=self.payload_writer,
            event_emitter=self.event_emitter,
        )
        self.update_run_coordinator = DBExportUpdateRunCoordinator(
            source_loader=self.source_loader,
            state_manager=self.state_manager,
            payload_writer=self.payload_writer,
        )

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
        txt_profile: str = DEFAULT_TXT_PROFILE,
    ) -> str:
        txt_profile = validate_txt_profile(txt_profile)
        return await self.full_run_coordinator.run(
            user_id=user_id,
            output_dir=output_dir,
            default_output_dir=self.default_output_dir,
            as_json=as_json,
            include_date=include_date,
            json_profile=json_profile,
            txt_profile=txt_profile,
        )

    async def update_user_messages(
        self,
        user_id: int,
        output_dir: Optional[str] = None,
        as_json: bool = True,
        include_date: bool = False,
        json_profile: str = "ai",
        txt_profile: str = DEFAULT_TXT_PROFILE,
    ) -> str:
        txt_profile = validate_txt_profile(txt_profile)
        return await self.update_run_coordinator.run(
            user_id=user_id,
            output_dir=output_dir,
            default_output_dir=self.default_output_dir,
            as_json=as_json,
            include_date=include_date,
            json_profile=json_profile,
            txt_profile=txt_profile,
            full_export=self.export_user_messages,
        )
