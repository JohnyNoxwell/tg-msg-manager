import logging
import os
from time import perf_counter
from typing import Any, Awaitable, Callable, Optional

from .event_emitter import DBExportEventEmitter
from .payload_writer import DBExportPayloadWriter
from .plan_builder import DBExportPlanBuilder
from .skip_policy import DBExportSkipPolicy
from .source_loader import DBExportSourceLoader
from .state_manager import DBExportStateManager

logger = logging.getLogger(__name__)

EXPORT_RUN_STATUS_SUCCESS = "success"
EXPORT_RUN_STATUS_FAILED = "failed"


class DBExportRunProgress:
    def __init__(self, *, coerce_datetime: bool):
        self.count = 0
        self.last_timestamp: Optional[int] = None
        self._coerce_datetime = coerce_datetime

    def track(self, count: int, item: Any) -> None:
        self.count = count
        timestamp = getattr(item, "timestamp", None)
        if timestamp is None and isinstance(item, dict):
            timestamp = item.get("timestamp")
        if self._coerce_datetime and hasattr(timestamp, "timestamp"):
            self.last_timestamp = int(timestamp.timestamp())
        elif timestamp is not None:
            self.last_timestamp = int(timestamp)


class DBExportFullRunCoordinator:
    def __init__(
        self,
        *,
        source_loader: DBExportSourceLoader,
        plan_builder: DBExportPlanBuilder,
        skip_policy: DBExportSkipPolicy,
        state_manager: DBExportStateManager,
        payload_writer: DBExportPayloadWriter,
        event_emitter: DBExportEventEmitter,
    ):
        self.source_loader = source_loader
        self.plan_builder = plan_builder
        self.skip_policy = skip_policy
        self.state_manager = state_manager
        self.payload_writer = payload_writer
        self.event_emitter = event_emitter

    async def run(
        self,
        *,
        user_id: int,
        output_dir: Optional[str],
        default_output_dir: str,
        as_json: bool,
        include_date: bool,
        json_profile: str,
        txt_profile: str,
    ) -> str:
        started_at = perf_counter()
        resolved_output_dir = output_dir or default_output_dir
        progress = DBExportRunProgress(coerce_datetime=True)
        run_id = self.state_manager.start_run(user_id=user_id)

        try:
            source = self.source_loader.load_full_source(
                user_id=user_id,
                as_json=as_json,
                json_profile=json_profile,
            )
            if source is None:
                logger.warning("No messages found in DB for user %s", user_id)
                self.state_manager.finish_run(
                    run_id,
                    status=EXPORT_RUN_STATUS_SUCCESS,
                    new_messages_count=0,
                    last_new_message_ts=None,
                    error=None,
                )
                return ""

            if not os.path.exists(resolved_output_dir):
                os.makedirs(resolved_output_dir)

            plan = self.plan_builder.prepare_plan(
                user_id=user_id,
                output_dir=resolved_output_dir,
                source=source,
                as_json=as_json,
                include_date=include_date,
                json_profile=json_profile,
                txt_profile=txt_profile,
            )
            decision = self.skip_policy.find_skip_decision(
                output_dir=resolved_output_dir,
                user_id=user_id,
                fingerprint=plan.fingerprint,
            )
            if decision.should_skip and decision.artifact is not None:
                self.event_emitter.emit_skipped_unchanged(
                    user_id=user_id,
                    source_count=source.source_count,
                    artifact=decision.artifact,
                )
                self.state_manager.upsert_export_target_state(
                    user_id=user_id,
                    output_path=decision.artifact.output_path,
                    target_author=plan.target_author,
                    source=source,
                    fingerprint=plan.fingerprint,
                    part_count=decision.artifact.part_count,
                )
                self.state_manager.finish_run(
                    run_id,
                    status=EXPORT_RUN_STATUS_SUCCESS,
                    new_messages_count=0,
                    last_new_message_ts=None,
                    error=None,
                )
                return decision.artifact.output_path

            self.payload_writer.cleanup_existing_export_files(
                output_dir=resolved_output_dir,
                user_id=user_id,
                ext=plan.ext,
                output_path=plan.output_path,
            )
            writer, result = await self.payload_writer.write_payloads(
                source=source,
                output_path=plan.output_path,
                as_json=as_json,
                json_profile=json_profile,
                txt_profile=txt_profile,
                expected_count=source.source_count,
                target_user_id=user_id,
                target_author=plan.target_author,
                overwrite=True,
                on_progress=progress.track,
            )
            self.event_emitter.emit_completed(
                user_id=user_id,
                count=result.count,
                as_json=as_json,
                output_path=plan.output_path,
                elapsed_seconds=perf_counter() - started_at,
                write_calls=writer.write_calls,
                bytes_written=writer.bytes_written,
                rotation_count=writer.rotation_count,
                state_persist_count=writer.state_persist_count,
            )
            self.state_manager.upsert_export_target_state(
                user_id=user_id,
                output_path=plan.output_path,
                target_author=plan.target_author,
                source=source,
                fingerprint=plan.fingerprint,
                part_count=writer.current_part,
            )
            last_ts, _last_message_id = self.state_manager.extract_export_cursor(
                source=source,
                fingerprint=plan.fingerprint,
            )
            self.state_manager.finish_run(
                run_id,
                status=EXPORT_RUN_STATUS_SUCCESS,
                new_messages_count=result.count,
                last_new_message_ts=last_ts,
                error=None,
            )
            logger.info(
                "DB Export complete for %s: %s messages.",
                plan.target_author,
                result.count,
            )
            return plan.output_path
        except Exception as exc:
            self.state_manager.finish_run(
                run_id,
                status=EXPORT_RUN_STATUS_FAILED,
                new_messages_count=progress.count,
                last_new_message_ts=progress.last_timestamp,
                error=str(exc),
            )
            raise


class DBExportUpdateRunCoordinator:
    def __init__(
        self,
        *,
        source_loader: DBExportSourceLoader,
        state_manager: DBExportStateManager,
        payload_writer: DBExportPayloadWriter,
    ):
        self.source_loader = source_loader
        self.state_manager = state_manager
        self.payload_writer = payload_writer

    async def run(
        self,
        *,
        user_id: int,
        output_dir: Optional[str],
        default_output_dir: str,
        as_json: bool,
        include_date: bool,
        json_profile: str,
        txt_profile: str,
        full_export: Callable[..., Awaitable[str]],
    ) -> str:
        resolved_output_dir = output_dir or default_output_dir
        export_target = self.state_manager.get_export_target(user_id)
        if not self.state_manager.supports_incremental_update(
            export_target=export_target,
            output_dir=output_dir,
            as_json=as_json,
            include_date=include_date,
            json_profile=json_profile,
        ):
            return await full_export(
                user_id,
                output_dir=output_dir,
                as_json=as_json,
                include_date=include_date,
                json_profile=json_profile,
                txt_profile=txt_profile,
            )

        output_path = self.state_manager.resolve_existing_export_path(
            export_target=export_target,
            fallback_output_dir=resolved_output_dir,
        )
        if not output_path or not os.path.exists(output_path):
            return await full_export(
                user_id,
                output_dir=output_dir,
                as_json=as_json,
                include_date=include_date,
                json_profile=json_profile,
                txt_profile=txt_profile,
            )

        last_ts = int(getattr(export_target, "last_exported_message_ts"))
        last_message_id = int(getattr(export_target, "last_exported_message_id"))
        run_id = self.state_manager.start_run(user_id=user_id)
        progress = DBExportRunProgress(coerce_datetime=False)

        try:
            source = self.source_loader.load_incremental_source(
                user_id=user_id,
                last_exported_message_ts=last_ts,
                last_exported_message_id=last_message_id,
                as_json=as_json,
                json_profile=json_profile,
            )
            if source is None:
                self.state_manager.finish_run(
                    run_id,
                    status=EXPORT_RUN_STATUS_SUCCESS,
                    new_messages_count=0,
                    last_new_message_ts=None,
                    error=None,
                )
                return output_path

            writer, result = await self.payload_writer.write_payloads(
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
                on_progress=progress.track,
            )
            self.state_manager.refresh_export_target_artifact_from_db_state(
                user_id=user_id,
                output_path=output_path,
                as_json=as_json,
                include_date=include_date,
                json_profile=json_profile,
                part_count=writer.current_part,
            )
            self.state_manager.finish_run(
                run_id,
                status=EXPORT_RUN_STATUS_SUCCESS,
                new_messages_count=result.count,
                last_new_message_ts=progress.last_timestamp,
                error=None,
            )
            return output_path
        except Exception as exc:
            self.state_manager.finish_run(
                run_id,
                status=EXPORT_RUN_STATUS_FAILED,
                new_messages_count=progress.count,
                last_new_message_ts=progress.last_timestamp,
                error=str(exc),
            )
            raise
