from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from .manifest_validator import _load_json_object
from .models import ValidationIssue, issue_error, issue_warning

CHANNEL_STATE_JSON = "channel_export_state.json"
DISCUSSION_STATE_JSON = "discussion_export_state.json"

CHANNEL_COUNTER_KEYS = (
    "message_count_total",
    "media_count_total",
    "downloaded_media_count_total",
    "already_existing_media_count_total",
    "skipped_media_count_total",
    "skipped_by_size_count_total",
    "skipped_by_type_count_total",
    "failed_media_count_total",
)

DISCUSSION_COUNTER_KEYS = (
    "thread_count_total",
    "comment_count_total",
    "failed_thread_count_total",
)


@dataclass(frozen=True)
class StateValidationResult:
    channel_state: Optional[dict[str, Any]]
    discussion_state: Optional[dict[str, Any]]
    issues: tuple[ValidationIssue, ...]


def _check_counter_fields(
    payload: dict[str, Any],
    keys: tuple[str, ...],
    display_path: str,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for key in keys:
        value = payload.get(key)
        if value is not None and (not isinstance(value, int) or value < 0):
            issues.append(
                issue_error(
                    "negative_count",
                    f"{key} must be a non-negative integer",
                    path=display_path,
                )
            )
    return issues


def validate_state_files(
    dataset_path: Path,
    *,
    manifest: Optional[dict[str, Any]],
    message_count: Optional[int] = None,
    media_count: Optional[int] = None,
    discussion_comment_count: Optional[int] = None,
    discussion_thread_count: Optional[int] = None,
    discussion_payload_present: bool = False,
) -> StateValidationResult:
    issues: list[ValidationIssue] = []
    channel_state: Optional[dict[str, Any]] = None
    discussion_state: Optional[dict[str, Any]] = None
    channel_state_path = dataset_path / CHANNEL_STATE_JSON
    discussion_state_path = dataset_path / DISCUSSION_STATE_JSON

    if not channel_state_path.exists():
        issues.append(
            issue_error(
                "missing_required_file",
                "Required channel state file is missing",
                path=CHANNEL_STATE_JSON,
            )
        )
    else:
        channel_state, load_issues = _load_json_object(
            channel_state_path,
            CHANNEL_STATE_JSON,
        )
        issues.extend(load_issues)
        if channel_state is not None:
            issues.extend(
                _validate_channel_state(
                    channel_state,
                    manifest=manifest,
                    message_count=message_count,
                    media_count=media_count,
                )
            )

    if discussion_state_path.exists():
        discussion_state, load_issues = _load_json_object(
            discussion_state_path,
            DISCUSSION_STATE_JSON,
        )
        issues.extend(load_issues)
        if discussion_state is not None:
            issues.extend(
                _validate_discussion_state(
                    discussion_state,
                    manifest=manifest,
                    discussion_comment_count=discussion_comment_count,
                    discussion_thread_count=discussion_thread_count,
                )
            )
        if not discussion_payload_present:
            issues.append(
                issue_warning(
                    "discussion_state_without_payload",
                    "Discussion state exists but no discussion payload files exist",
                    path=DISCUSSION_STATE_JSON,
                )
            )
    elif discussion_payload_present:
        issues.append(
            issue_warning(
                "discussion_payload_without_state",
                "Discussion payload files exist but discussion state is missing",
                path=DISCUSSION_STATE_JSON,
            )
        )

    return StateValidationResult(
        channel_state=channel_state,
        discussion_state=discussion_state,
        issues=tuple(issues),
    )


def load_channel_state(dataset_path: Path) -> StateValidationResult:
    return validate_state_files(dataset_path, manifest=None)


def load_discussion_state(dataset_path: Path) -> StateValidationResult:
    return validate_state_files(dataset_path, manifest=None)


def _validate_channel_state(
    state: dict[str, Any],
    *,
    manifest: Optional[dict[str, Any]],
    message_count: Optional[int],
    media_count: Optional[int],
) -> list[ValidationIssue]:
    issues = _check_counter_fields(state, CHANNEL_COUNTER_KEYS, CHANNEL_STATE_JSON)
    last_exported_message_id = state.get("last_exported_message_id")
    if last_exported_message_id is not None and (
        not isinstance(last_exported_message_id, int) or last_exported_message_id < 0
    ):
        issues.append(
            issue_error(
                "negative_count",
                "last_exported_message_id must be a non-negative integer",
                path=CHANNEL_STATE_JSON,
            )
        )
    if state.get("last_run_status") not in (None, "completed"):
        issues.append(
            issue_warning(
                "state_status_drift",
                "last_run_status is not completed",
                path=CHANNEL_STATE_JSON,
            )
        )

    source = manifest.get("source") if manifest else None
    if isinstance(source, dict):
        if (
            isinstance(state.get("channel_id"), int)
            and isinstance(source.get("id"), int)
            and state["channel_id"] != source["id"]
        ):
            issues.append(
                issue_warning(
                    "state_identity_mismatch",
                    "State channel_id differs from manifest source id",
                    path=CHANNEL_STATE_JSON,
                )
            )
        if (
            state.get("channel_username")
            and source.get("username")
            and state["channel_username"] != source["username"]
        ):
            issues.append(
                issue_warning(
                    "state_identity_mismatch",
                    "State channel_username differs from manifest source username",
                    path=CHANNEL_STATE_JSON,
                )
            )

    if (
        message_count is not None
        and isinstance(state.get("message_count_total"), int)
        and state["message_count_total"] < message_count
    ):
        issues.append(
            issue_warning(
                "state_count_mismatch",
                "State message_count_total is lower than observed message count",
                path=CHANNEL_STATE_JSON,
            )
        )
    if (
        media_count is not None
        and isinstance(state.get("media_count_total"), int)
        and state["media_count_total"] < media_count
    ):
        issues.append(
            issue_warning(
                "state_count_mismatch",
                "State media_count_total is lower than observed media record count",
                path=CHANNEL_STATE_JSON,
            )
        )
    return issues


def _validate_discussion_state(
    state: dict[str, Any],
    *,
    manifest: Optional[dict[str, Any]],
    discussion_comment_count: Optional[int],
    discussion_thread_count: Optional[int],
) -> list[ValidationIssue]:
    issues = _check_counter_fields(
        state,
        DISCUSSION_COUNTER_KEYS,
        DISCUSSION_STATE_JSON,
    )
    source = manifest.get("source") if manifest else None
    if (
        isinstance(source, dict)
        and isinstance(state.get("channel_id"), int)
        and isinstance(source.get("id"), int)
        and state["channel_id"] != source["id"]
    ):
        issues.append(
            issue_warning(
                "state_identity_mismatch",
                "Discussion state channel_id differs from manifest source id",
                path=DISCUSSION_STATE_JSON,
            )
        )
    if (
        discussion_comment_count is not None
        and isinstance(state.get("comment_count_total"), int)
        and state["comment_count_total"] < discussion_comment_count
    ):
        issues.append(
            issue_warning(
                "discussion_count_mismatch",
                "Discussion state comment_count_total is lower than observed comments",
                path=DISCUSSION_STATE_JSON,
            )
        )
    if (
        discussion_thread_count is not None
        and isinstance(state.get("thread_count_total"), int)
        and state["thread_count_total"] < discussion_thread_count
    ):
        issues.append(
            issue_warning(
                "discussion_count_mismatch",
                "Discussion state thread_count_total is lower than observed threads",
                path=DISCUSSION_STATE_JSON,
            )
        )
    return issues
