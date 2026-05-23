from __future__ import annotations

import json
from typing import Any

from .doctor import DatasetDoctorReport
from .models import DatasetInspectionReport, ValidationIssue, ValidationReport


def render_validation_report_markdown(report: ValidationReport) -> str:
    lines = [
        "# Dataset Validation Report",
        "",
        "## Status",
        report.status,
        "",
        "## Dataset Path",
        str(report.dataset_path),
        "",
        "## Files Checked",
    ]
    lines.extend(_bullet_list(report.files_checked))
    lines.extend(["", "## Errors"])
    lines.extend(_render_issues(report.errors, empty_text="No errors"))
    lines.extend(["", "## Warnings"])
    lines.extend(_render_issues(report.warnings, empty_text="No warnings"))
    lines.extend(["", "## Summary"])
    lines.extend(_render_mapping(report.summary))
    return "\n".join(lines) + "\n"


def render_validation_report_json(report: ValidationReport) -> str:
    return json.dumps(report.to_dict(), indent=2, sort_keys=True)


def render_inspection_report_markdown(report: DatasetInspectionReport) -> str:
    lines = [
        "# Dataset Inspection Report",
        "",
        "## Dataset Path",
        str(report.dataset_path),
        "",
        "## Files",
    ]
    lines.extend(_render_mapping(report.files))
    lines.extend(["", "## Messages"])
    lines.extend(_render_mapping(report.messages))
    lines.extend(["", "## Media"])
    lines.extend(_render_mapping(report.media))
    lines.extend(["", "## Discussions"])
    lines.extend(_render_mapping(report.discussions))
    lines.extend(["", "## State"])
    lines.extend(_render_mapping(report.state))
    lines.extend(["", "## Notes"])
    lines.extend(_bullet_list(report.notes) if report.notes else ["None"])
    return "\n".join(lines) + "\n"


def render_inspection_report_json(report: DatasetInspectionReport) -> str:
    return json.dumps(report.to_dict(), indent=2, sort_keys=True)


def render_doctor_report_markdown(report: DatasetDoctorReport) -> str:
    lines = [
        "# Dataset Doctor Report",
        "",
        "## Status",
        report.status,
        "",
        "## Dataset Path",
        str(report.dataset_path),
        "",
        "## Summary",
        f"- errors: {report.error_count}",
        f"- warnings: {report.warning_count}",
        "",
        "## Findings",
    ]
    if not report.findings:
        lines.append("None")
    else:
        for finding in report.findings:
            location = f" ({finding.path})" if finding.path else ""
            lines.append(
                f"- {finding.severity.value} {finding.code}{location}: "
                f"{finding.message} Action: {finding.suggested_action}"
            )
    return "\n".join(lines) + "\n"


def render_doctor_report_json(report: DatasetDoctorReport) -> str:
    return json.dumps(report.to_dict(), indent=2, sort_keys=True)


def _render_issues(
    issues: tuple[ValidationIssue, ...],
    *,
    empty_text: str,
) -> list[str]:
    if not issues:
        return [empty_text]
    lines = []
    for issue in issues:
        location = ""
        if issue.path is not None:
            location = f" ({issue.path}"
            if issue.line is not None:
                location += f":{issue.line}"
            location += ")"
        lines.append(f"- {issue.code}{location}: {issue.message}")
    return lines


def _render_mapping(mapping: dict[str, Any], *, indent: int = 0) -> list[str]:
    if not mapping:
        return [" " * indent + "None"]
    lines: list[str] = []
    prefix = " " * indent
    for key in sorted(mapping):
        value = mapping[key]
        if isinstance(value, dict):
            lines.append(f"{prefix}- {key}:")
            lines.extend(_render_mapping(value, indent=indent + 2))
        else:
            lines.append(f"{prefix}- {key}: {value}")
    return lines


def _bullet_list(values) -> list[str]:
    if not values:
        return ["None"]
    return [f"- {value}" for value in values]
