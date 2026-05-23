from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from .inspector import validate_dataset
from .models import ValidationSeverity
from .options import DatasetValidationOptions


class DoctorSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass(frozen=True)
class DoctorFinding:
    code: str
    severity: DoctorSeverity
    message: str
    suggested_action: str
    path: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "code": self.code,
            "severity": self.severity.value,
            "message": self.message,
            "suggested_action": self.suggested_action,
        }
        if self.path is not None:
            payload["path"] = self.path
        return payload


@dataclass(frozen=True)
class DatasetDoctorReport:
    dataset_path: Path
    findings: tuple[DoctorFinding, ...]

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity is DoctorSeverity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(
            1 for finding in self.findings if finding.severity is DoctorSeverity.WARNING
        )

    @property
    def status(self) -> str:
        if self.error_count:
            return "errors"
        if self.warning_count:
            return "warnings"
        return "ok"

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "dataset_path": str(self.dataset_path),
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "findings": [finding.to_dict() for finding in self.findings],
        }


def diagnose_dataset(options: DatasetValidationOptions) -> DatasetDoctorReport:
    validation = validate_dataset(options)
    findings = tuple(
        DoctorFinding(
            code=issue.code,
            severity=_doctor_severity(issue.severity),
            path=issue.path,
            message=issue.message,
            suggested_action=_suggest_action(issue.code),
        )
        for issue in validation.issues
    )
    if not findings:
        findings = (
            DoctorFinding(
                code="dataset_healthy",
                severity=DoctorSeverity.INFO,
                path=None,
                message="No validation issues were found.",
                suggested_action="No action required.",
            ),
        )
    return DatasetDoctorReport(dataset_path=options.dataset_path, findings=findings)


def _doctor_severity(severity: ValidationSeverity) -> DoctorSeverity:
    if severity is ValidationSeverity.ERROR:
        return DoctorSeverity.ERROR
    return DoctorSeverity.WARNING


def _suggest_action(code: str) -> str:
    if code in {
        "dataset_path_missing",
        "dataset_path_not_directory",
        "missing_required_file",
        "missing_conditional_file",
        "manifest_included_file_missing",
    }:
        return "Restore the missing artifact or re-run export-channel for this dataset."
    if code in {
        "invalid_json",
        "invalid_jsonl",
        "invalid_jsonl_object",
        "invalid_discussion_comments_jsonl",
        "invalid_discussion_threads_jsonl",
        "invalid_discussion_metadata_jsonl",
        "file_unreadable",
    }:
        return "Replace the corrupt artifact from backup or rebuild the dataset with export-channel --force."
    if code in {
        "media_file_missing",
        "invalid_media_path",
        "media_path_escape",
    }:
        return "Check media paths inside the dataset or re-run export-channel with the intended media mode."
    if code in {
        "manifest_count_mismatch",
        "state_count_mismatch",
        "discussion_count_mismatch",
        "state_identity_mismatch",
    }:
        return "Review manifest/state consistency; re-run export-channel --force if the dataset is stale."
    if code in {
        "duplicate_message_id",
        "duplicate_media_id",
        "duplicate_discussion_comment_id",
    }:
        return "Rebuild the dataset from source; duplicate identifiers should not be edited by the doctor."
    if code in {
        "message_id_gap_detected",
        "reply_parent_missing",
        "reply_parent_outside_export_scope",
        "discussion_reply_parent_missing",
        "discussion_reply_parent_outside_export_scope",
    }:
        return "Review export scope and Telegram deletions; use a wider or forced export if parents are required."
    if code == "unknown_extra_file":
        return "Inspect the extra file manually; the doctor will not remove files."
    return "Run validate-dataset for details and rebuild or restore artifacts if needed."
