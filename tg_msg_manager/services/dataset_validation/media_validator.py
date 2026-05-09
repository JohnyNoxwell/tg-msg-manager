from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .jsonl_validator import JsonlRecord, load_jsonl_records
from .models import MediaSummary, ValidationIssue, issue_error, issue_warning

MEDIA_MANIFEST_JSONL = "media_manifest.jsonl"
MEDIA_FILE_STATUSES = {"downloaded", "already_exists"}
KNOWN_MEDIA_STATUSES = {
    "metadata_only",
    "downloaded",
    "already_exists",
    "skipped_by_size",
    "skipped_by_type",
    "failed",
}


@dataclass(frozen=True)
class MediaValidationResult:
    records: tuple[JsonlRecord, ...]
    summary: MediaSummary
    issues: tuple[ValidationIssue, ...]


def validate_media_manifest(dataset_path: Path) -> MediaValidationResult:
    path = dataset_path / MEDIA_MANIFEST_JSONL
    issues: list[ValidationIssue] = []
    records: tuple[JsonlRecord, ...] = ()

    if not path.exists():
        return MediaValidationResult(
            records=records,
            summary=MediaSummary(),
            issues=(
                issue_error(
                    "missing_required_file",
                    "Required media manifest is missing",
                    path=MEDIA_MANIFEST_JSONL,
                ),
            ),
        )

    loaded = load_jsonl_records(path, MEDIA_MANIFEST_JSONL)
    records = loaded.records
    issues.extend(loaded.issues)

    status_counts: dict[str, int] = {}
    for record in records:
        status = record.payload.get("download_status")
        if not isinstance(status, str) or not status:
            status = "unknown"
            issues.append(
                issue_warning(
                    "unknown_media_status",
                    "Media record has no usable download_status",
                    path=MEDIA_MANIFEST_JSONL,
                    line=record.line,
                )
            )
        elif status not in KNOWN_MEDIA_STATUSES:
            issues.append(
                issue_warning(
                    "unknown_media_status",
                    f"Unknown media download_status {status!r}",
                    path=MEDIA_MANIFEST_JSONL,
                    line=record.line,
                )
            )
        status_counts[status] = status_counts.get(status, 0) + 1

        if status == "failed":
            issues.append(
                issue_warning(
                    "failed_media_records_present",
                    "Failed media record is present",
                    path=MEDIA_MANIFEST_JSONL,
                    line=record.line,
                )
            )

        issues.extend(_validate_media_path(dataset_path, record, status))

    return MediaValidationResult(
        records=records,
        summary=MediaSummary(record_count=len(records), status_counts=status_counts),
        issues=tuple(issues),
    )


def summarize_media_records(records: tuple[JsonlRecord, ...]) -> MediaSummary:
    status_counts: dict[str, int] = {}
    for record in records:
        status = record.payload.get("download_status")
        if not isinstance(status, str) or not status:
            status = "unknown"
        status_counts[status] = status_counts.get(status, 0) + 1
    return MediaSummary(record_count=len(records), status_counts=status_counts)


def _validate_media_path(
    dataset_path: Path,
    record: JsonlRecord,
    status: str,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    raw_path = _media_path_value(record)
    if status in MEDIA_FILE_STATUSES and not raw_path:
        return [
            issue_error(
                "invalid_media_path",
                "Downloaded media record must include final_path or local_path",
                path=MEDIA_MANIFEST_JSONL,
                line=record.line,
            )
        ]
    if not raw_path:
        return issues
    if not isinstance(raw_path, str):
        return [
            issue_error(
                "invalid_media_path",
                "Media path must be a string",
                path=MEDIA_MANIFEST_JSONL,
                line=record.line,
            )
        ]

    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = dataset_path / candidate
    resolved_dataset = dataset_path.resolve()
    resolved_candidate = candidate.resolve()
    try:
        resolved_candidate.relative_to(resolved_dataset)
    except ValueError:
        issues.append(
            issue_error(
                "media_path_escape",
                f"Media path escapes dataset root: {raw_path}",
                path=MEDIA_MANIFEST_JSONL,
                line=record.line,
            )
        )
        return issues

    if status in MEDIA_FILE_STATUSES and not resolved_candidate.is_file():
        issues.append(
            issue_error(
                "media_file_missing",
                f"Media file is missing for status {status}: {raw_path}",
                path=MEDIA_MANIFEST_JSONL,
                line=record.line,
            )
        )
    return issues


def _media_path_value(record: JsonlRecord):
    for key in ("final_path", "local_path", "relative_path", "path"):
        value = record.payload.get(key)
        if value:
            return value
    return None
