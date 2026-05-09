import os
from typing import Optional

from ...infrastructure.storage.records import ExportTargetRecord, UserExportSummary
from .plan_builder import DBExportPlanBuilder
from .summary import DBExportSource

EXPORT_RUN_STATUS_SUCCESS = "success"


def _format_profile_for_state(fingerprint: dict) -> Optional[str]:
    if fingerprint.get("as_json"):
        value = fingerprint.get("json_profile")
    else:
        value = fingerprint.get("txt_profile")
    return str(value) if value is not None else None


class DBExportStateManager:
    def __init__(
        self,
        storage: object,
        *,
        default_output_dir: str = "DB_EXPORTS",
        plan_builder: Optional[DBExportPlanBuilder] = None,
    ):
        self.storage = storage
        self.default_output_dir = default_output_dir
        self.plan_builder = plan_builder or DBExportPlanBuilder(storage)

    def start_run(self, *, user_id: int) -> Optional[int]:
        starter = getattr(self.storage, "start_export_run", None)
        if not callable(starter):
            return None
        run_id = starter(target_user_id=user_id)
        return int(run_id) if run_id is not None else None

    def finish_run(
        self,
        run_id: Optional[int],
        *,
        status: str,
        new_messages_count: int = 0,
        last_new_message_ts: Optional[int] = None,
        error: Optional[str] = None,
    ) -> None:
        if run_id is None:
            return
        finisher = getattr(self.storage, "finish_export_run", None)
        if not callable(finisher):
            return
        finisher(
            run_id,
            status=status,
            new_messages_count=new_messages_count,
            last_new_message_ts=last_new_message_ts,
            error=error,
        )

    def extract_export_cursor(
        self,
        *,
        source: DBExportSource,
        fingerprint: dict[str, object],
    ) -> tuple[Optional[int], Optional[int]]:
        last_ts = fingerprint.get("last_timestamp")
        last_message_id = fingerprint.get("last_message_id")
        if last_ts is not None or last_message_id is not None:
            return (
                int(last_ts) if last_ts is not None else None,
                int(last_message_id) if last_message_id is not None else None,
            )

        if source.export_summary is not None:
            return (
                source.export_summary.last_timestamp,
                source.export_summary.last_message_id,
            )

        if source.export_rows:
            last_row = source.export_rows[-1]
            return last_row.timestamp, last_row.message_id

        if source.messages:
            last_message = sorted(
                source.messages,
                key=lambda message: (message.timestamp, message.message_id),
            )[-1]
            return int(last_message.timestamp.timestamp()), last_message.message_id

        return None, None

    def upsert_export_target_state(
        self,
        *,
        user_id: int,
        output_path: str,
        target_author: str,
        source: DBExportSource,
        fingerprint: dict[str, object],
        part_count: Optional[int] = None,
    ) -> None:
        updater = getattr(self.storage, "upsert_export_target", None)
        if not callable(updater):
            return

        db_user = getattr(self.storage, "get_user", lambda _user_id: None)(user_id)
        username = None
        if db_user is not None:
            username = getattr(db_user, "username", None)
            if username is None and isinstance(db_user, dict):
                username = db_user.get("username")

        last_ts, last_message_id = self.extract_export_cursor(
            source=source,
            fingerprint=fingerprint,
        )
        updater(
            target_user_id=user_id,
            export_filename=os.path.basename(output_path) or None,
            export_dir=os.path.dirname(output_path) or None,
            last_exported_message_ts=last_ts,
            last_exported_message_id=last_message_id,
            export_part_count=part_count,
            artifact_message_count=(
                int(fingerprint["message_count"])
                if fingerprint.get("message_count") is not None
                else None
            ),
            artifact_first_message_id=(
                int(fingerprint["first_message_id"])
                if fingerprint.get("first_message_id") is not None
                else None
            ),
            artifact_last_message_id=(
                int(fingerprint["last_message_id"])
                if fingerprint.get("last_message_id") is not None
                else None
            ),
            artifact_first_timestamp=(
                int(fingerprint["first_timestamp"])
                if fingerprint.get("first_timestamp") is not None
                else None
            ),
            artifact_last_timestamp=(
                int(fingerprint["last_timestamp"])
                if fingerprint.get("last_timestamp") is not None
                else None
            ),
            artifact_as_json=(
                bool(fingerprint["as_json"])
                if fingerprint.get("as_json") is not None
                else None
            ),
            artifact_include_date=(
                bool(fingerprint["include_date"])
                if fingerprint.get("include_date") is not None
                else None
            ),
            artifact_json_profile=(_format_profile_for_state(fingerprint)),
            last_known_author_name=target_author,
            last_known_username=username,
        )

    def resolve_existing_export_path(
        self,
        *,
        export_target: object,
        fallback_output_dir: str,
    ) -> Optional[str]:
        export_filename = getattr(export_target, "export_filename", None)
        export_dir = getattr(export_target, "export_dir", None) or fallback_output_dir
        if not export_filename:
            return None
        return os.path.join(export_dir, export_filename)

    def supports_incremental_update(
        self,
        *,
        export_target: object,
        output_dir: Optional[str],
        as_json: bool,
        include_date: bool,
        json_profile: str,
    ) -> bool:
        if not as_json or include_date or json_profile != "ai":
            return False
        if export_target is None:
            return False

        export_filename = getattr(export_target, "export_filename", None)
        export_dir = getattr(export_target, "export_dir", None)
        last_ts = getattr(export_target, "last_exported_message_ts", None)
        last_message_id = getattr(export_target, "last_exported_message_id", None)
        if not export_filename or last_ts is None or last_message_id is None:
            return False
        if (
            output_dir
            and export_dir
            and os.path.abspath(output_dir) != os.path.abspath(export_dir)
        ):
            return False
        return export_filename.endswith(".jsonl")

    def refresh_export_target_artifact_from_db_state(
        self,
        *,
        user_id: int,
        output_path: str,
        as_json: bool,
        include_date: bool,
        json_profile: str,
        part_count: int,
    ) -> None:
        full_summary_getter = getattr(self.storage, "get_user_export_summary", None)
        if not callable(full_summary_getter):
            return
        full_summary = UserExportSummary.coerce(full_summary_getter(user_id))
        if full_summary is None:
            return
        source = DBExportSource(
            export_summary=full_summary,
            export_rows=None,
            export_row_iter_factory=None,
            messages=None,
            source_count=full_summary.message_count,
        )
        plan = self.plan_builder.prepare_plan(
            user_id=user_id,
            output_dir=os.path.dirname(output_path) or self.default_output_dir,
            source=source,
            as_json=as_json,
            include_date=include_date,
            json_profile=json_profile,
            txt_profile=json_profile,
        )
        self.upsert_export_target_state(
            user_id=user_id,
            output_path=output_path,
            target_author=plan.target_author,
            source=source,
            fingerprint=plan.fingerprint,
            part_count=part_count,
        )

    def get_export_target(self, user_id: int) -> Optional[ExportTargetRecord]:
        return ExportTargetRecord.coerce(
            getattr(self.storage, "get_export_target", lambda _uid: None)(user_id)
        )
