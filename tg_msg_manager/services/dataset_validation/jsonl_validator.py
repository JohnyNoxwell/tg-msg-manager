from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from tg_msg_manager.core.models.dataset_contracts import MESSAGES_JSONL, MESSAGES_TXT

from .models import MessageSummary, ValidationIssue, issue_error, issue_warning


@dataclass(frozen=True)
class JsonlRecord:
    line: int
    payload: dict[str, Any]


@dataclass(frozen=True)
class JsonlLoadResult:
    records: tuple[JsonlRecord, ...]
    issues: tuple[ValidationIssue, ...]


@dataclass(frozen=True)
class MessageValidationResult:
    records: tuple[JsonlRecord, ...]
    message_ids: frozenset[int]
    summary: MessageSummary
    issues: tuple[ValidationIssue, ...]


def load_jsonl_records(
    path: Path,
    display_path: Optional[str] = None,
) -> JsonlLoadResult:
    shown_path = display_path or str(path)
    records: list[JsonlRecord] = []
    issues: list[ValidationIssue] = []

    try:
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError as exc:
                    issues.append(
                        issue_error(
                            "invalid_jsonl",
                            f"Invalid JSONL at line {line_number}: {exc.msg}",
                            path=shown_path,
                            line=line_number,
                        )
                    )
                    continue
                if not isinstance(payload, dict):
                    issues.append(
                        issue_error(
                            "invalid_jsonl_object",
                            "JSONL line must contain a JSON object",
                            path=shown_path,
                            line=line_number,
                        )
                    )
                    continue
                records.append(JsonlRecord(line=line_number, payload=payload))
    except OSError as exc:
        issues.append(
            issue_error(
                "file_unreadable",
                f"Could not read file: {exc}",
                path=shown_path,
            )
        )

    return JsonlLoadResult(records=tuple(records), issues=tuple(issues))


def validate_messages_jsonl(dataset_path: Path) -> MessageValidationResult:
    issues: list[ValidationIssue] = []
    messages_path = dataset_path / MESSAGES_JSONL
    txt_path = dataset_path / MESSAGES_TXT
    records: tuple[JsonlRecord, ...] = ()

    if not messages_path.exists():
        issues.append(
            issue_error(
                "missing_required_file",
                "Required messages JSONL file is missing",
                path=MESSAGES_JSONL,
            )
        )
    else:
        loaded = load_jsonl_records(messages_path, MESSAGES_JSONL)
        records = loaded.records
        issues.extend(loaded.issues)

    if not txt_path.exists():
        issues.append(
            issue_error(
                "missing_required_file",
                "Required messages text projection is missing",
                path=MESSAGES_TXT,
            )
        )

    seen_ids: set[int] = set()
    duplicate_ids: set[int] = set()
    for record in records:
        message_id = record.payload.get("message_id")
        if not isinstance(message_id, int) or message_id < 0:
            issues.append(
                issue_error(
                    "missing_message_id",
                    "Message row must include a non-negative integer message_id",
                    path=MESSAGES_JSONL,
                    line=record.line,
                )
            )
            continue
        if message_id in seen_ids:
            duplicate_ids.add(message_id)
            issues.append(
                issue_error(
                    "duplicate_message_id",
                    f"Duplicate message_id {message_id}",
                    path=MESSAGES_JSONL,
                    line=record.line,
                )
            )
            continue
        seen_ids.add(message_id)

    sorted_ids = sorted(seen_ids | duplicate_ids)
    issues.extend(_validate_message_id_gaps(sorted_ids))
    issues.extend(_validate_message_reply_links(records, frozenset(sorted_ids)))
    summary = MessageSummary(
        count=len(records),
        min_message_id=sorted_ids[0] if sorted_ids else None,
        max_message_id=sorted_ids[-1] if sorted_ids else None,
    )
    return MessageValidationResult(
        records=records,
        message_ids=frozenset(seen_ids | duplicate_ids),
        summary=summary,
        issues=tuple(issues),
    )


def _validate_message_id_gaps(sorted_ids: list[int]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if len(sorted_ids) < 2:
        return issues
    previous = sorted_ids[0]
    for current in sorted_ids[1:]:
        if current == previous:
            continue
        if current > previous + 1:
            missing_count = current - previous - 1
            issues.append(
                issue_warning(
                    "message_id_gap_detected",
                    (
                        "Message id gap detected; Telegram deletions or unavailable "
                        f"messages may also cause this: {previous + 1}-{current - 1} "
                        f"({missing_count} missing)"
                    ),
                    path=MESSAGES_JSONL,
                )
            )
        previous = current
    return issues


def _validate_message_reply_links(
    records: tuple[JsonlRecord, ...],
    message_ids: frozenset[int],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not message_ids:
        return issues
    min_message_id = min(message_ids)
    max_message_id = max(message_ids)
    for record in records:
        message_id = record.payload.get("message_id")
        reply_to_id = _extract_reply_to_id(record.payload)
        if reply_to_id is None:
            continue
        if not isinstance(reply_to_id, int) or reply_to_id < 0:
            issues.append(
                issue_error(
                    "invalid_reply_to_id",
                    "Message reply_to_id must be a non-negative integer when present",
                    path=MESSAGES_JSONL,
                    line=record.line,
                )
            )
            continue
        if reply_to_id in message_ids:
            continue
        if reply_to_id < min_message_id or reply_to_id > max_message_id:
            issues.append(
                issue_warning(
                    "reply_parent_outside_export_scope",
                    (
                        f"Message {message_id} replies to {reply_to_id}, which is "
                        "outside the exported message id range"
                    ),
                    path=MESSAGES_JSONL,
                    line=record.line,
                )
            )
            continue
        issues.append(
            issue_warning(
                "reply_parent_missing",
                (
                    f"Message {message_id} replies to missing message {reply_to_id} "
                    "inside the exported message id range"
                ),
                path=MESSAGES_JSONL,
                line=record.line,
            )
        )
    return issues


def _extract_reply_to_id(payload: dict[str, Any]) -> Any:
    if "reply_to_id" in payload:
        return payload.get("reply_to_id")
    raw_payload = payload.get("raw_payload")
    if isinstance(raw_payload, dict):
        if "reply_to_id" in raw_payload:
            return raw_payload.get("reply_to_id")
        reply_to = raw_payload.get("reply_to")
        if isinstance(reply_to, dict):
            return reply_to.get("reply_to_msg_id")
        if isinstance(reply_to, int):
            return reply_to
    return None
