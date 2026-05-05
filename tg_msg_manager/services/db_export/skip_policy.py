import os
from typing import Any, Optional

from ...infrastructure.storage.records import ExportTargetRecord
from .manifest_writer import DBExportManifestWriter
from .models import ExistingExportArtifact, SkipDecision


class DBExportSkipPolicy:
    def __init__(
        self,
        storage: object,
        *,
        manifest_writer: Optional[DBExportManifestWriter] = None,
    ):
        self.storage = storage
        self.manifest_writer = manifest_writer or DBExportManifestWriter()

    def artifact_paths_exist(self, output_path: str, part_count: int) -> bool:
        return all(
            os.path.exists(path)
            for path in self.manifest_writer.expected_paths(
                output_path, max(1, int(part_count))
            )
        )

    def _resolve_existing_export_path(
        self,
        *,
        export_target: Any,
        fallback_output_dir: str,
    ) -> Optional[str]:
        export_filename = getattr(export_target, "export_filename", None)
        export_dir = getattr(export_target, "export_dir", None) or fallback_output_dir
        if not export_filename:
            return None
        return os.path.join(export_dir, export_filename)

    def _db_skip_match(
        self,
        *,
        output_dir: str,
        user_id: int,
        fingerprint: dict[str, Any],
    ) -> Optional[ExistingExportArtifact]:
        export_target = ExportTargetRecord.coerce(
            getattr(self.storage, "get_export_target", lambda _uid: None)(user_id)
        )
        if export_target is None:
            return None

        output_path = self._resolve_existing_export_path(
            export_target=export_target,
            fallback_output_dir=output_dir,
        )
        if not output_path:
            return None
        if (
            output_dir
            and export_target.export_dir
            and os.path.abspath(output_dir) != os.path.abspath(export_target.export_dir)
        ):
            return None

        if (
            export_target.artifact_message_count != fingerprint.get("message_count")
            or export_target.artifact_first_message_id
            != fingerprint.get("first_message_id")
            or export_target.artifact_last_message_id
            != fingerprint.get("last_message_id")
            or export_target.artifact_first_timestamp
            != fingerprint.get("first_timestamp")
            or export_target.artifact_last_timestamp
            != fingerprint.get("last_timestamp")
            or export_target.artifact_as_json != fingerprint.get("as_json")
            or export_target.artifact_include_date != fingerprint.get("include_date")
            or export_target.artifact_json_profile != fingerprint.get("json_profile")
        ):
            return None

        part_count = getattr(export_target, "export_part_count", None)
        if part_count is None:
            return None
        if not self.artifact_paths_exist(output_path, part_count):
            return None
        return ExistingExportArtifact(
            output_path=output_path, part_count=int(part_count)
        )

    def _legacy_manifest_skip_match(
        self,
        *,
        output_dir: str,
        user_id: int,
        fingerprint: dict[str, Any],
    ) -> Optional[ExistingExportArtifact]:
        manifest = self.manifest_writer.load_manifest(output_dir, user_id)
        if not manifest or manifest.get("fingerprint") != fingerprint:
            return None

        output_path = manifest.get("output_path")
        if not output_path or not isinstance(output_path, str):
            return None

        try:
            part_count = max(1, int(manifest.get("part_count", 1)))
        except Exception:
            return None

        if not self.artifact_paths_exist(output_path, part_count):
            return None
        return ExistingExportArtifact(output_path=output_path, part_count=part_count)

    def find_skip_decision(
        self,
        *,
        output_dir: str,
        user_id: int,
        fingerprint: dict[str, Any],
    ) -> SkipDecision:
        artifact = self._db_skip_match(
            output_dir=output_dir,
            user_id=user_id,
            fingerprint=fingerprint,
        ) or self._legacy_manifest_skip_match(
            output_dir=output_dir,
            user_id=user_id,
            fingerprint=fingerprint,
        )
        if artifact is None:
            return SkipDecision(
                should_skip=False,
                reason="changed",
                current_fingerprint=fingerprint,
            )
        return SkipDecision(
            should_skip=True,
            reason="unchanged",
            current_fingerprint=fingerprint,
            artifact=artifact,
        )
