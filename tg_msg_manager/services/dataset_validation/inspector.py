from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from .discussion_validator import validate_discussion_files
from .jsonl_validator import validate_messages_jsonl
from .manifest_validator import validate_manifest_shape
from .media_validator import validate_media_manifest
from .models import (
    DatasetInspectionReport,
    FileSummary,
    ValidationIssue,
    ValidationReport,
    issue_error,
    issue_warning,
)
from .options import DatasetInspectionOptions, DatasetValidationOptions
from .state_validator import validate_state_files

KNOWN_DATASET_FILES = (
    "manifest.json",
    "messages.jsonl",
    "messages.txt",
    "media_manifest.jsonl",
    "channel_export_state.json",
    "discussion_comments.jsonl",
    "discussion_comments.txt",
    "discussion_threads.jsonl",
    "discussion_export_state.json",
    "media/",
)


def validate_dataset(options: DatasetValidationOptions) -> ValidationReport:
    dataset_path = options.dataset_path
    issues: list[ValidationIssue] = []
    if not dataset_path.exists():
        issues.append(
            issue_error(
                "dataset_path_missing",
                "Dataset path does not exist",
                path=str(dataset_path),
            )
        )
        return _build_report(dataset_path, issues, None, None, None, None, None)
    if not dataset_path.is_dir():
        issues.append(
            issue_error(
                "dataset_path_not_directory",
                "Dataset path must be a directory",
                path=str(dataset_path),
            )
        )
        return _build_report(dataset_path, issues, None, None, None, None, None)

    message_result = validate_messages_jsonl(dataset_path)
    issues.extend(message_result.issues)

    media_result = validate_media_manifest(dataset_path)
    issues.extend(media_result.issues)

    discussion_result = validate_discussion_files(
        dataset_path,
        message_ids=message_result.message_ids,
    )
    issues.extend(discussion_result.issues)

    manifest_result = validate_manifest_shape(
        dataset_path,
        message_count=message_result.summary.count,
        media_count=media_result.summary.record_count,
        discussion_comment_count=discussion_result.summary.comment_count
        if discussion_result.summary.present
        else None,
        discussion_thread_count=discussion_result.summary.thread_count
        if discussion_result.summary.present
        else None,
    )
    issues.extend(manifest_result.issues)

    state_result = validate_state_files(
        dataset_path,
        manifest=manifest_result.manifest,
        message_count=message_result.summary.count,
        media_count=media_result.summary.record_count,
        discussion_comment_count=discussion_result.summary.comment_count,
        discussion_thread_count=discussion_result.summary.thread_count,
        discussion_payload_present=discussion_result.summary.present,
    )
    issues.extend(state_result.issues)

    issues.extend(_detect_unknown_files(dataset_path))
    return _build_report(
        dataset_path,
        issues,
        message_result.summary.to_dict(),
        media_result.summary.to_dict(),
        discussion_result.summary.to_dict(),
        _manifest_summary(manifest_result.manifest),
        _state_summary(state_result.channel_state, state_result.discussion_state),
    )


def inspect_dataset(options: DatasetInspectionOptions) -> DatasetInspectionReport:
    validation = validate_dataset(
        DatasetValidationOptions(
            dataset_path=options.dataset_path,
            strict=options.strict,
        )
    )
    summary = validation.summary
    notes = [
        f"validation_status={validation.status}",
        f"errors={len(validation.errors)}",
        f"warnings={len(validation.warnings)}",
    ]
    return DatasetInspectionReport(
        dataset_path=options.dataset_path,
        files=summary.get("files", {}),
        messages=summary.get("messages", {}),
        media=summary.get("media", {}),
        discussions=summary.get("discussions", {}),
        state=summary.get("state", {}),
        notes=tuple(notes),
    )


def _build_report(
    dataset_path: Path,
    issues: list[ValidationIssue],
    messages: Optional[dict[str, Any]],
    media: Optional[dict[str, Any]],
    discussions: Optional[dict[str, Any]],
    manifest: Optional[dict[str, Any]],
    state: Optional[dict[str, Any]],
) -> ValidationReport:
    files = _summarize_files(dataset_path) if dataset_path.is_dir() else {}
    if dataset_path.is_dir() and not any(files.values()):
        issues.append(
            issue_warning(
                "empty_dataset",
                "Dataset directory is empty",
                path=str(dataset_path),
            )
        )
    summary = {
        "files": files,
        "messages": messages or {},
        "media": media or {},
        "discussions": discussions or {},
        "manifest": manifest or {},
        "state": state or {},
    }
    return ValidationReport(
        dataset_path=dataset_path,
        files_checked=tuple(sorted(files)),
        summary=summary,
        issues=tuple(_sort_issues(issues)),
    )


def _summarize_files(dataset_path: Path) -> dict[str, dict[str, Any]]:
    summaries: dict[str, dict[str, Any]] = {}
    for name in KNOWN_DATASET_FILES:
        path = dataset_path / name.rstrip("/")
        exists = path.exists()
        size = path.stat().st_size if exists and path.is_file() else None
        summaries[name] = FileSummary(name, exists, size).to_dict()
    return summaries


def _manifest_summary(manifest: Optional[dict[str, Any]]) -> dict[str, Any]:
    if not manifest:
        return {}
    export = manifest.get("export") if isinstance(manifest.get("export"), dict) else {}
    discussion = (
        manifest.get("discussion")
        if isinstance(manifest.get("discussion"), dict)
        else {}
    )
    source = manifest.get("source") if isinstance(manifest.get("source"), dict) else {}
    return {
        "dataset_type": manifest.get("dataset_type"),
        "schema_version": manifest.get("schema_version"),
        "status": manifest.get("status"),
        "source_id": source.get("id"),
        "source_username": source.get("username"),
        "message_count": export.get("message_count"),
        "media_count": export.get("media_count"),
        "discussion_mode": discussion.get("mode"),
        "discussion_thread_count": discussion.get("thread_count"),
        "discussion_comment_count": discussion.get("comment_count"),
    }


def _state_summary(
    channel_state: Optional[dict[str, Any]],
    discussion_state: Optional[dict[str, Any]],
) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    if channel_state:
        summary["channel"] = {
            "last_exported_message_id": channel_state.get("last_exported_message_id"),
            "message_count_total": channel_state.get("message_count_total"),
            "media_count_total": channel_state.get("media_count_total"),
            "last_run_status": channel_state.get("last_run_status"),
        }
    if discussion_state:
        summary["discussion"] = {
            "thread_count_total": discussion_state.get("thread_count_total"),
            "comment_count_total": discussion_state.get("comment_count_total"),
            "failed_thread_count_total": discussion_state.get(
                "failed_thread_count_total"
            ),
            "last_run_status": discussion_state.get("last_run_status"),
        }
    return summary


def _detect_unknown_files(dataset_path: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    known = {name.rstrip("/") for name in KNOWN_DATASET_FILES}
    for child in sorted(dataset_path.iterdir(), key=lambda path: path.name):
        if child.name.startswith(".") or child.name in known:
            continue
        issues.append(
            issue_warning(
                "unknown_extra_file",
                f"Unknown extra dataset file or directory: {child.name}",
                path=child.name,
            )
        )
    return issues


def _sort_issues(issues: list[ValidationIssue]) -> list[ValidationIssue]:
    return sorted(
        issues,
        key=lambda issue: (
            0 if issue.severity.value == "error" else 1,
            issue.path or "",
            issue.line or 0,
            issue.code,
            issue.message,
        ),
    )
