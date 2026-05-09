from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class ValidationSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class ValidationIssue:
    severity: ValidationSeverity
    code: str
    message: str
    path: str | None = None
    line: int | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "severity": self.severity.value,
            "code": self.code,
            "message": self.message,
        }
        if self.path is not None:
            payload["path"] = self.path
        if self.line is not None:
            payload["line"] = self.line
        return payload


@dataclass(frozen=True)
class FileSummary:
    path: str
    exists: bool
    size_bytes: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "exists": self.exists,
            "size_bytes": self.size_bytes,
        }


@dataclass(frozen=True)
class MediaSummary:
    record_count: int = 0
    status_counts: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_count": self.record_count,
            "status_counts": dict(sorted(self.status_counts.items())),
        }


@dataclass(frozen=True)
class DiscussionSummary:
    present: bool = False
    comment_count: int = 0
    thread_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "present": self.present,
            "comment_count": self.comment_count,
            "thread_count": self.thread_count,
        }


@dataclass(frozen=True)
class MessageSummary:
    count: int = 0
    min_message_id: int | None = None
    max_message_id: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "count": self.count,
            "min_message_id": self.min_message_id,
            "max_message_id": self.max_message_id,
        }


@dataclass(frozen=True)
class ValidationReport:
    dataset_path: Path
    files_checked: tuple[str, ...]
    summary: dict[str, Any]
    issues: tuple[ValidationIssue, ...] = ()

    @property
    def status(self) -> str:
        if any(issue.severity is ValidationSeverity.ERROR for issue in self.issues):
            return "errors"
        if self.issues:
            return "warnings"
        return "ok"

    @property
    def errors(self) -> tuple[ValidationIssue, ...]:
        return tuple(
            issue for issue in self.issues if issue.severity is ValidationSeverity.ERROR
        )

    @property
    def warnings(self) -> tuple[ValidationIssue, ...]:
        return tuple(
            issue
            for issue in self.issues
            if issue.severity is ValidationSeverity.WARNING
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "dataset_path": str(self.dataset_path),
            "summary": self.summary,
            "files_checked": list(self.files_checked),
            "issues": [issue.to_dict() for issue in self.issues],
        }


@dataclass(frozen=True)
class DatasetInspectionReport:
    dataset_path: Path
    files: dict[str, dict[str, Any]]
    messages: dict[str, Any]
    media: dict[str, Any]
    discussions: dict[str, Any]
    state: dict[str, Any]
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_path": str(self.dataset_path),
            "files": self.files,
            "messages": self.messages,
            "media": self.media,
            "discussions": self.discussions,
            "state": self.state,
            "notes": list(self.notes),
        }


def issue_error(
    code: str,
    message: str,
    path: str | None = None,
    line: int | None = None,
) -> ValidationIssue:
    return ValidationIssue(
        severity=ValidationSeverity.ERROR,
        code=code,
        message=message,
        path=path,
        line=line,
    )


def issue_warning(
    code: str,
    message: str,
    path: str | None = None,
    line: int | None = None,
) -> ValidationIssue:
    return ValidationIssue(
        severity=ValidationSeverity.WARNING,
        code=code,
        message=message,
        path=path,
        line=line,
    )
