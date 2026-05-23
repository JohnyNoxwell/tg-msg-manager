from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .jsonl_validator import JsonlRecord, load_jsonl_records
from .models import DiscussionSummary, ValidationIssue, issue_error, issue_warning

DISCUSSION_COMMENTS_JSONL = "discussion_comments.jsonl"
DISCUSSION_COMMENTS_TXT = "discussion_comments.txt"
DISCUSSION_THREADS_JSONL = "discussion_threads.jsonl"
DISCUSSION_METADATA_JSONL = "discussion_metadata.jsonl"
DISCUSSION_STATE_JSON = "discussion_export_state.json"


@dataclass(frozen=True)
class DiscussionValidationResult:
    metadata: tuple[JsonlRecord, ...]
    comments: tuple[JsonlRecord, ...]
    threads: tuple[JsonlRecord, ...]
    summary: DiscussionSummary
    issues: tuple[ValidationIssue, ...]


def validate_discussion_files(
    dataset_path: Path,
    *,
    message_ids: frozenset[int],
) -> DiscussionValidationResult:
    issues: list[ValidationIssue] = []
    metadata: tuple[JsonlRecord, ...] = ()
    comments: tuple[JsonlRecord, ...] = ()
    threads: tuple[JsonlRecord, ...] = ()
    discussion_paths = {
        DISCUSSION_METADATA_JSONL: dataset_path / DISCUSSION_METADATA_JSONL,
        DISCUSSION_COMMENTS_JSONL: dataset_path / DISCUSSION_COMMENTS_JSONL,
        DISCUSSION_COMMENTS_TXT: dataset_path / DISCUSSION_COMMENTS_TXT,
        DISCUSSION_THREADS_JSONL: dataset_path / DISCUSSION_THREADS_JSONL,
        DISCUSSION_STATE_JSON: dataset_path / DISCUSSION_STATE_JSON,
    }
    present_names = {name for name, path in discussion_paths.items() if path.exists()}
    if not present_names:
        return DiscussionValidationResult(
            metadata=metadata,
            comments=comments,
            threads=threads,
            summary=DiscussionSummary(present=False),
            issues=(),
        )

    if DISCUSSION_METADATA_JSONL in present_names:
        loaded = load_jsonl_records(
            discussion_paths[DISCUSSION_METADATA_JSONL],
            DISCUSSION_METADATA_JSONL,
        )
        metadata = loaded.records
        issues.extend(
            _rewrite_jsonl_codes(loaded.issues, "invalid_discussion_metadata_jsonl")
        )
        issues.extend(_validate_metadata(metadata, message_ids))

    if DISCUSSION_COMMENTS_JSONL in present_names:
        loaded = load_jsonl_records(
            discussion_paths[DISCUSSION_COMMENTS_JSONL],
            DISCUSSION_COMMENTS_JSONL,
        )
        comments = loaded.records
        issues.extend(
            _rewrite_jsonl_codes(loaded.issues, "invalid_discussion_comments_jsonl")
        )
        issues.extend(_validate_comments(comments, message_ids))
        if DISCUSSION_COMMENTS_TXT not in present_names:
            issues.append(
                issue_warning(
                    "missing_discussion_file",
                    "discussion_comments.txt is missing for discussion comments JSONL",
                    path=DISCUSSION_COMMENTS_TXT,
                )
            )
    elif (
        DISCUSSION_THREADS_JSONL in present_names
        or DISCUSSION_COMMENTS_TXT in present_names
    ):
        issues.append(
            issue_warning(
                "missing_discussion_file",
                "discussion_comments.jsonl is missing while discussion payload exists",
                path=DISCUSSION_COMMENTS_JSONL,
            )
        )

    if DISCUSSION_THREADS_JSONL in present_names:
        loaded = load_jsonl_records(
            discussion_paths[DISCUSSION_THREADS_JSONL],
            DISCUSSION_THREADS_JSONL,
        )
        threads = loaded.records
        issues.extend(
            _rewrite_jsonl_codes(loaded.issues, "invalid_discussion_threads_jsonl")
        )
        issues.extend(_validate_threads(threads, message_ids, comments))
    elif DISCUSSION_COMMENTS_JSONL in present_names:
        issues.append(
            issue_warning(
                "missing_discussion_file",
                "discussion_threads.jsonl is missing for discussion comments",
                path=DISCUSSION_THREADS_JSONL,
            )
        )

    return DiscussionValidationResult(
        metadata=metadata,
        comments=comments,
        threads=threads,
        summary=DiscussionSummary(
            present=True,
            metadata_count=len(metadata),
            comment_count=len(comments),
            thread_count=len(threads),
        ),
        issues=tuple(issues),
    )


def summarize_discussion_records(
    metadata: tuple[JsonlRecord, ...],
    comments: tuple[JsonlRecord, ...],
    threads: tuple[JsonlRecord, ...],
) -> DiscussionSummary:
    return DiscussionSummary(
        present=bool(metadata or comments or threads),
        metadata_count=len(metadata),
        comment_count=len(comments),
        thread_count=len(threads),
    )


def _rewrite_jsonl_codes(
    issues: tuple[ValidationIssue, ...],
    replacement_code: str,
) -> list[ValidationIssue]:
    return [
        ValidationIssue(
            severity=issue.severity,
            code=replacement_code
            if issue.code.startswith("invalid_jsonl")
            else issue.code,
            message=issue.message,
            path=issue.path,
            line=issue.line,
        )
        for issue in issues
    ]


def _validate_metadata(
    metadata: tuple[JsonlRecord, ...],
    message_ids: frozenset[int],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for record in metadata:
        channel_post_id = record.payload.get("channel_message_id")
        if isinstance(channel_post_id, int):
            if message_ids and channel_post_id not in message_ids:
                issues.append(
                    issue_warning(
                        "discussion_metadata_unlinked",
                        f"Discussion metadata references missing channel post {channel_post_id}",
                        path=DISCUSSION_METADATA_JSONL,
                        line=record.line,
                    )
                )
        elif channel_post_id is not None:
            issues.append(
                issue_error(
                    "negative_count",
                    "Discussion metadata channel_message_id must be an integer when present",
                    path=DISCUSSION_METADATA_JSONL,
                    line=record.line,
                )
            )
        replies_count = record.payload.get("replies_count")
        if replies_count is not None and (
            not isinstance(replies_count, int) or replies_count < 0
        ):
            issues.append(
                issue_error(
                    "negative_count",
                    "Discussion metadata replies_count must be a non-negative integer when present",
                    path=DISCUSSION_METADATA_JSONL,
                    line=record.line,
                )
            )
    return issues


def _validate_comments(
    comments: tuple[JsonlRecord, ...],
    message_ids: frozenset[int],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    seen_comment_ids: set[int] = set()
    comment_ids = {
        record.payload.get("message_id")
        for record in comments
        if isinstance(record.payload.get("message_id"), int)
    }
    min_comment_id = min(comment_ids) if comment_ids else None
    max_comment_id = max(comment_ids) if comment_ids else None
    for record in comments:
        comment_id = record.payload.get("message_id")
        if isinstance(comment_id, int):
            if comment_id in seen_comment_ids:
                issues.append(
                    issue_error(
                        "duplicate_discussion_comment_id",
                        f"Duplicate discussion comment message_id {comment_id}",
                        path=DISCUSSION_COMMENTS_JSONL,
                        line=record.line,
                    )
                )
            seen_comment_ids.add(comment_id)
        elif comment_id is not None:
            issues.append(
                issue_error(
                    "negative_count",
                    "Discussion comment message_id must be an integer when present",
                    path=DISCUSSION_COMMENTS_JSONL,
                    line=record.line,
                )
            )
        _check_non_negative_id_fields(
            record,
            ("channel_message_id", "discussion_root_message_id", "reply_to_id"),
            issues,
            DISCUSSION_COMMENTS_JSONL,
        )
        _validate_comment_reply_link(
            record,
            comment_ids,
            min_comment_id,
            max_comment_id,
            issues,
        )
        channel_post_id = record.payload.get("channel_message_id")
        if isinstance(channel_post_id, int) and channel_post_id not in message_ids:
            issues.append(
                issue_warning(
                    "discussion_comment_unlinked",
                    f"Discussion comment references missing channel post {channel_post_id}",
                    path=DISCUSSION_COMMENTS_JSONL,
                    line=record.line,
                )
            )
    if comments and not any(
        "channel_message_id" in record.payload for record in comments
    ):
        issues.append(
            issue_warning(
                "discussion_comment_unlinked",
                "Discussion comments do not include channel_message_id links",
                path=DISCUSSION_COMMENTS_JSONL,
            )
        )
    return issues


def _validate_comment_reply_link(
    record: JsonlRecord,
    comment_ids: set[int],
    min_comment_id: int | None,
    max_comment_id: int | None,
    issues: list[ValidationIssue],
) -> None:
    reply_to_id = record.payload.get("reply_to_id")
    if reply_to_id is None or not isinstance(reply_to_id, int) or not comment_ids:
        return
    if reply_to_id in comment_ids:
        return
    if reply_to_id == record.payload.get("discussion_root_message_id"):
        return
    if min_comment_id is None or max_comment_id is None:
        return
    comment_id = record.payload.get("message_id")
    if reply_to_id < min_comment_id or reply_to_id > max_comment_id:
        issues.append(
            issue_warning(
                "discussion_reply_parent_outside_export_scope",
                (
                    f"Discussion comment {comment_id} replies to {reply_to_id}, "
                    "which is outside the exported discussion comment id range"
                ),
                path=DISCUSSION_COMMENTS_JSONL,
                line=record.line,
            )
        )
        return
    issues.append(
        issue_warning(
            "discussion_reply_parent_missing",
            (
                f"Discussion comment {comment_id} replies to missing comment "
                f"{reply_to_id} inside the exported discussion comment id range"
            ),
            path=DISCUSSION_COMMENTS_JSONL,
            line=record.line,
        )
    )


def _validate_threads(
    threads: tuple[JsonlRecord, ...],
    message_ids: frozenset[int],
    comments: tuple[JsonlRecord, ...],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    comments_by_channel_post: dict[int, int] = {}
    for comment in comments:
        channel_post_id = comment.payload.get("channel_message_id")
        if isinstance(channel_post_id, int):
            comments_by_channel_post[channel_post_id] = (
                comments_by_channel_post.get(channel_post_id, 0) + 1
            )

    for record in threads:
        _check_non_negative_id_fields(
            record,
            ("channel_message_id", "discussion_root_message_id"),
            issues,
            DISCUSSION_THREADS_JSONL,
        )
        for key in ("comments_count", "exported_comments_count"):
            value = record.payload.get(key)
            if value is not None and (not isinstance(value, int) or value < 0):
                issues.append(
                    issue_error(
                        "negative_count",
                        f"{key} must be a non-negative integer",
                        path=DISCUSSION_THREADS_JSONL,
                        line=record.line,
                    )
                )
        channel_post_id = record.payload.get("channel_message_id")
        if isinstance(channel_post_id, int) and channel_post_id not in message_ids:
            issues.append(
                issue_warning(
                    "discussion_thread_unlinked",
                    f"Discussion thread references missing channel post {channel_post_id}",
                    path=DISCUSSION_THREADS_JSONL,
                    line=record.line,
                )
            )
        exported_count = record.payload.get("exported_comments_count")
        if (
            isinstance(channel_post_id, int)
            and isinstance(exported_count, int)
            and comments_by_channel_post.get(channel_post_id, 0) != exported_count
        ):
            issues.append(
                issue_warning(
                    "discussion_count_mismatch",
                    "Thread exported_comments_count differs from observed comments",
                    path=DISCUSSION_THREADS_JSONL,
                    line=record.line,
                )
            )
    return issues


def _check_non_negative_id_fields(
    record: JsonlRecord,
    keys: tuple[str, ...],
    issues: list[ValidationIssue],
    display_path: str,
) -> None:
    for key in keys:
        value: Any = record.payload.get(key)
        if value is not None and (not isinstance(value, int) or value < 0):
            issues.append(
                issue_error(
                    "negative_count",
                    f"{key} must be a non-negative integer when present",
                    path=display_path,
                    line=record.line,
                )
            )
