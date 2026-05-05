import logging

from ...core.telemetry import telemetry
from .models import ExistingExportArtifact

logger = logging.getLogger(__name__)


class DBExportEventEmitter:
    def emit_skipped_unchanged(
        self,
        *,
        user_id: int,
        source_count: int,
        artifact: ExistingExportArtifact,
    ) -> None:
        telemetry.track_counter("db_export.skipped_unchanged", 1)
        logger.info(
            "DB export skipped as unchanged",
            extra={
                "event": "db_export_skipped",
                "metrics": {
                    "user_id": user_id,
                    "messages": source_count,
                    "path": artifact.output_path,
                },
            },
        )

    def emit_completed(
        self,
        *,
        user_id: int,
        count: int,
        as_json: bool,
        output_path: str,
        elapsed_seconds: float,
        write_calls: int,
        bytes_written: int,
        rotation_count: int,
        state_persist_count: int,
    ) -> None:
        telemetry.track_counter("db_export.users", 1)
        telemetry.track_counter("db_export.messages", count)
        telemetry.track_duration("db_export.total", elapsed_seconds)
        logger.info(
            "DB export complete",
            extra={
                "event": "db_export_complete",
                "metrics": {
                    "user_id": user_id,
                    "messages": count,
                    "json": as_json,
                    "path": output_path,
                    "elapsed_seconds": round(elapsed_seconds, 3),
                    "writer_write_calls": write_calls,
                    "writer_bytes_written": bytes_written,
                    "writer_rotations": rotation_count,
                    "writer_state_persists": state_persist_count,
                },
            },
        )
