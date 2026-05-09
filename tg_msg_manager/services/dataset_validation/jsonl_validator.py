from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import MessageSummary, ValidationIssue, issue_error

MESSAGES_JSONL = "messages.jsonl"
MESSAGES_TXT = "messages.txt"


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


def load_jsonl_records(path: Path, display_path: str | None = None) -> JsonlLoadResult:
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
