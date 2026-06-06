from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from tg_msg_manager.core.models.dataset_contracts import (
    DATASET_SCHEMA_VERSION,
    DIRECT_CHANNEL_EXPORT_DATASET_TYPE,
    DISCUSSION_ANY_DATASET_FILES,
    DISCUSSION_FULL_DATASET_FILES,
    DISCUSSION_METADATA_JSONL,
    MANIFEST_JSON,
    RUN_CHANGELOG_JSONL,
)

from .models import ValidationIssue, issue_error, issue_warning

DISCUSSION_FULL_FILES = DISCUSSION_FULL_DATASET_FILES
DISCUSSION_ANY_FILES = DISCUSSION_ANY_DATASET_FILES


def validate_contract_v1_files(
    dataset_path: Path,
    *,
    manifest: Optional[dict[str, Any]],
) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []
    issues.extend(_validate_required_artifacts(dataset_path))
    if manifest is None:
        return tuple(issues)
    issues.extend(_validate_manifest_identity(manifest))
    issues.extend(_validate_discussion_mode_files(dataset_path, manifest))
    return tuple(issues)


def _validate_required_artifacts(dataset_path: Path) -> list[ValidationIssue]:
    if (dataset_path / RUN_CHANGELOG_JSONL).exists():
        return []
    return [
        issue_error(
            "missing_required_file",
            "Required run changelog is missing",
            path=RUN_CHANGELOG_JSONL,
        )
    ]


def _validate_manifest_identity(manifest: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if manifest.get("dataset_type") not in (None, DIRECT_CHANNEL_EXPORT_DATASET_TYPE):
        issues.append(
            issue_warning(
                "dataset_type_mismatch",
                "Manifest dataset_type is not direct_channel_export",
                path=MANIFEST_JSON,
            )
        )
    if manifest.get("schema_version") not in (None, DATASET_SCHEMA_VERSION):
        issues.append(
            issue_warning(
                "schema_version_mismatch",
                "Manifest schema_version is not 1.0",
                path=MANIFEST_JSON,
            )
        )
    return issues


def _validate_discussion_mode_files(
    dataset_path: Path,
    manifest: dict[str, Any],
) -> list[ValidationIssue]:
    discussion = manifest.get("discussion")
    if not isinstance(discussion, dict):
        return []
    mode = discussion.get("mode") or "none"
    present = {name for name in DISCUSSION_ANY_FILES if (dataset_path / name).exists()}
    issues: list[ValidationIssue] = []
    if mode == "none":
        for name in sorted(present):
            issues.append(_unexpected_discussion_file(mode, name))
        return issues
    if mode == "metadata":
        if DISCUSSION_METADATA_JSONL not in present:
            issues.append(
                issue_error(
                    "missing_conditional_file",
                    "discussion_metadata.jsonl is required for discussion metadata mode",
                    path=DISCUSSION_METADATA_JSONL,
                )
            )
        for name in sorted(present - {DISCUSSION_METADATA_JSONL}):
            issues.append(_unexpected_discussion_file(mode, name))
        return issues
    if mode == "full":
        for name in DISCUSSION_FULL_FILES:
            if name not in present:
                issues.append(
                    issue_error(
                        "missing_conditional_file",
                        f"{name} is required for discussion full mode",
                        path=name,
                    )
                )
        if DISCUSSION_METADATA_JSONL in present:
            issues.append(_unexpected_discussion_file(mode, DISCUSSION_METADATA_JSONL))
    return issues


def _unexpected_discussion_file(mode: str, name: str) -> ValidationIssue:
    return issue_warning(
        "unexpected_discussion_file_for_mode",
        f"{name} is not expected for discussion mode {mode}",
        path=name,
    )
