from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Tuple

from tg_msg_manager.core.models.dataset_contracts import MANIFEST_JSON

from .models import ValidationIssue, issue_error, issue_warning


@dataclass(frozen=True)
class ManifestValidationResult:
    manifest: Optional[dict[str, Any]]
    issues: tuple[ValidationIssue, ...]


def _load_json_object(
    path: Path, display_path: str
) -> Tuple[Optional[dict[str, Any]], list[ValidationIssue]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, [
            issue_error(
                "invalid_json",
                f"Invalid JSON: {exc.msg}",
                path=display_path,
                line=exc.lineno,
            )
        ]
    except OSError as exc:
        return None, [
            issue_error(
                "file_unreadable",
                f"Could not read file: {exc}",
                path=display_path,
            )
        ]
    if not isinstance(payload, dict):
        return None, [
            issue_error(
                "invalid_json",
                "JSON root must be an object",
                path=display_path,
            )
        ]
    return payload, []


def _warn_missing_key(
    container: dict[str, Any], key: str, path: str
) -> Optional[ValidationIssue]:
    if key not in container:
        return issue_warning(
            "manifest_shape_drift",
            f"Manifest is missing expected key {key!r}",
            path=path,
        )
    return None


def _check_non_negative_int(
    value: Any,
    key: str,
    path: str,
    *,
    required: bool = False,
) -> Optional[ValidationIssue]:
    if value is None and not required:
        return None
    if not isinstance(value, int) or value < 0:
        return issue_error(
            "negative_count",
            f"{key} must be a non-negative integer",
            path=path,
        )
    return None


def validate_manifest_shape(
    dataset_path: Path,
    *,
    message_count: Optional[int] = None,
    media_count: Optional[int] = None,
    discussion_comment_count: Optional[int] = None,
    discussion_thread_count: Optional[int] = None,
) -> ManifestValidationResult:
    manifest_path = dataset_path / MANIFEST_JSON
    issues: list[ValidationIssue] = []
    if not manifest_path.exists():
        return ManifestValidationResult(
            manifest=None,
            issues=(
                issue_error(
                    "missing_required_file",
                    "Required manifest file is missing",
                    path=MANIFEST_JSON,
                ),
            ),
        )

    manifest, load_issues = _load_json_object(manifest_path, MANIFEST_JSON)
    issues.extend(load_issues)
    if manifest is None:
        return ManifestValidationResult(manifest=None, issues=tuple(issues))

    for key in (
        "dataset_type",
        "schema_version",
        "exported_at",
        "source",
        "export",
        "discussion",
        "status",
    ):
        maybe_issue = _warn_missing_key(manifest, key, MANIFEST_JSON)
        if maybe_issue is not None:
            issues.append(maybe_issue)

    source = manifest.get("source")
    if isinstance(source, dict):
        for key in ("type", "id", "username", "title"):
            maybe_issue = _warn_missing_key(source, key, MANIFEST_JSON)
            if maybe_issue is not None:
                issues.append(maybe_issue)
    elif source is not None:
        issues.append(
            issue_error(
                "invalid_manifest_shape", "source must be an object", MANIFEST_JSON
            )
        )

    export = manifest.get("export")
    if isinstance(export, dict):
        count_keys = (
            "message_count",
            "media_count",
            "downloaded_media_count",
            "already_existing_media_count",
            "skipped_media_count",
            "skipped_by_size_count",
            "skipped_by_type_count",
            "failed_media_count",
        )
        for key in count_keys:
            maybe_issue = _check_non_negative_int(
                export.get(key), f"export.{key}", MANIFEST_JSON
            )
            if maybe_issue is not None:
                issues.append(maybe_issue)
        if message_count is not None and isinstance(export.get("message_count"), int):
            if export["message_count"] != message_count:
                issues.append(
                    issue_warning(
                        "manifest_count_mismatch",
                        "Manifest message_count differs from messages.jsonl count",
                        path=MANIFEST_JSON,
                    )
                )
        if media_count is not None and isinstance(export.get("media_count"), int):
            if export["media_count"] != media_count:
                issues.append(
                    issue_warning(
                        "manifest_count_mismatch",
                        "Manifest media_count differs from media_manifest.jsonl count",
                        path=MANIFEST_JSON,
                    )
                )
        included_files = export.get("included_files")
        if included_files is not None:
            issues.extend(
                _validate_included_files(
                    dataset_path, included_files, "export.included_files"
                )
            )
    elif export is not None:
        issues.append(
            issue_error(
                "invalid_manifest_shape", "export must be an object", MANIFEST_JSON
            )
        )

    discussion = manifest.get("discussion")
    if isinstance(discussion, dict):
        for key in ("thread_count", "comment_count", "failed_thread_count"):
            maybe_issue = _check_non_negative_int(
                discussion.get(key),
                f"discussion.{key}",
                MANIFEST_JSON,
            )
            if maybe_issue is not None:
                issues.append(maybe_issue)
        if (
            discussion_comment_count is not None
            and isinstance(discussion.get("comment_count"), int)
            and discussion["comment_count"] != discussion_comment_count
        ):
            issues.append(
                issue_warning(
                    "discussion_count_mismatch",
                    "Manifest discussion comment_count differs from observed comments",
                    path=MANIFEST_JSON,
                )
            )
        if (
            discussion_thread_count is not None
            and isinstance(discussion.get("thread_count"), int)
            and discussion["thread_count"] != discussion_thread_count
        ):
            issues.append(
                issue_warning(
                    "discussion_count_mismatch",
                    "Manifest discussion thread_count differs from observed threads",
                    path=MANIFEST_JSON,
                )
            )
        included_files = discussion.get("included_files")
        if included_files is not None:
            issues.extend(
                _validate_included_files(
                    dataset_path,
                    included_files,
                    "discussion.included_files",
                )
            )
    elif discussion is not None:
        issues.append(
            issue_error(
                "invalid_manifest_shape",
                "discussion must be an object",
                MANIFEST_JSON,
            )
        )

    return ManifestValidationResult(manifest=manifest, issues=tuple(issues))


def load_manifest(dataset_path: Path) -> ManifestValidationResult:
    return validate_manifest_shape(dataset_path)


def _validate_included_files(
    dataset_path: Path,
    included_files: Any,
    field: str,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not isinstance(included_files, list):
        return [
            issue_warning(
                "manifest_shape_drift",
                f"{field} should be a list",
                path=MANIFEST_JSON,
            )
        ]
    root = dataset_path.resolve()
    for value in included_files:
        if not isinstance(value, str) or not value:
            issues.append(
                issue_warning(
                    "manifest_shape_drift",
                    f"{field} contains a non-string file entry",
                    path=MANIFEST_JSON,
                )
            )
            continue
        candidate = (dataset_path / value).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            issues.append(
                issue_error(
                    "media_path_escape",
                    f"Manifest included file escapes dataset root: {value}",
                    path=MANIFEST_JSON,
                )
            )
            continue
        if value.endswith("/"):
            if not candidate.is_dir():
                issues.append(
                    issue_warning(
                        "manifest_included_file_missing",
                        f"Manifest included directory is missing: {value}",
                        path=MANIFEST_JSON,
                    )
                )
        elif not candidate.exists():
            issues.append(
                issue_warning(
                    "manifest_included_file_missing",
                    f"Manifest included file is missing: {value}",
                    path=MANIFEST_JSON,
                )
            )
    return issues
