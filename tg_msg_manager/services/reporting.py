import json
import re
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from time import time
from typing import Any

from ..core.models.reporting import (
    AuditReport,
    ReportDatabaseSummary,
    ReportExportState,
    ReportRetrySummary,
    ReportTargetSummary,
    ReportWarning,
)


class ReportCollector:
    STALE_SYNC_SECONDS = 7 * 24 * 3600
    HIGH_MISSING_PARENT_MIN_COUNT = 10
    HIGH_MISSING_PARENT_RATIO = 0.10

    def __init__(
        self,
        *,
        storage: Any,
        exports_dir: str | Path,
        now_ts: int | None = None,
    ):
        self.storage = storage
        self.exports_dir = Path(exports_dir)
        self.now_ts = int(now_ts if now_ts is not None else time())

    def collect(self) -> AuditReport:
        database = self.storage.get_report_database_summary()
        retry = self.storage.get_report_retry_summary(now_ts=self.now_ts)
        targets = self.storage.get_report_target_summaries()
        exports = self._collect_export_states(targets)
        export_map = {item.user_id: item for item in exports}
        warnings = self._build_warnings(
            database=database,
            retry=retry,
            targets=targets,
            export_map=export_map,
        )
        retry_tasks = [
            task.as_dict() if hasattr(task, "as_dict") else dict(task)
            for task in self.storage.list_retry_tasks()
        ]
        return AuditReport(
            generated_at=self.now_ts,
            database=database,
            retry=retry,
            targets=targets,
            exports=exports,
            retry_tasks=retry_tasks,
            warnings=warnings,
        )

    def _collect_export_states(
        self, targets: list[ReportTargetSummary]
    ) -> list[ReportExportState]:
        export_files_by_user: dict[int, list[Path]] = {
            target.user_id: [] for target in targets
        }
        if self.exports_dir.exists():
            for path in sorted(self.exports_dir.iterdir()):
                if not path.is_file():
                    continue
                match = re.search(r"_(\d+)\.(jsonl|txt)$", path.name)
                if not match:
                    continue
                user_id = int(match.group(1))
                if user_id not in export_files_by_user:
                    continue
                export_files_by_user[user_id].append(path)

        states: list[ReportExportState] = []
        for target in sorted(targets, key=lambda item: (item.chat_id, item.user_id)):
            files = export_files_by_user.get(target.user_id, [])
            latest_path = None
            latest_modified_at = 0
            formats: list[str] = []
            for path in files:
                stat = path.stat()
                mtime = int(stat.st_mtime)
                suffix = path.suffix.lstrip(".").lower()
                if suffix and suffix not in formats:
                    formats.append(suffix)
                if mtime >= latest_modified_at:
                    latest_modified_at = mtime
                    latest_path = str(path)
            states.append(
                ReportExportState(
                    user_id=target.user_id,
                    artifact_count=len(files),
                    latest_artifact_path=latest_path,
                    latest_modified_at=latest_modified_at,
                    formats=tuple(sorted(formats)),
                )
            )
        return states

    def _build_warnings(
        self,
        *,
        database: ReportDatabaseSummary,
        retry: ReportRetrySummary,
        targets: list[ReportTargetSummary],
        export_map: dict[int, ReportExportState],
    ) -> list[ReportWarning]:
        warnings: list[ReportWarning] = []
        if (
            database.missing_parent_count >= self.HIGH_MISSING_PARENT_MIN_COUNT
            and database.missing_parent_ratio >= self.HIGH_MISSING_PARENT_RATIO
        ):
            warnings.append(
                ReportWarning(
                    code="high_missing_parent_signals",
                    severity="warn",
                    message=(
                        "High missing-parent signal ratio: "
                        f"{database.missing_parent_count}/{database.reply_messages_count}"
                    ),
                )
            )

        if retry.pending_tasks + retry.retrying_tasks > 0:
            warnings.append(
                ReportWarning(
                    code="retry_queue_not_empty",
                    severity="warn",
                    message=(
                        "Retry queue is not empty: "
                        f"pending={retry.pending_tasks}, retrying={retry.retrying_tasks}"
                    ),
                )
            )
        if retry.failed_tasks > 0:
            warnings.append(
                ReportWarning(
                    code="retry_failed_tasks",
                    severity="error",
                    message=f"Retry queue contains failed tasks: {retry.failed_tasks}",
                )
            )

        for target in targets:
            if not target.is_complete:
                warnings.append(
                    ReportWarning(
                        code="incomplete_target",
                        severity="warn",
                        message="Target sync history is incomplete.",
                        user_id=target.user_id,
                        chat_id=target.chat_id,
                    )
                )
            if not target.is_whole_chat and target.own_messages <= 0:
                warnings.append(
                    ReportWarning(
                        code="no_target_messages",
                        severity="warn",
                        message="Target has no own linked messages.",
                        user_id=target.user_id,
                        chat_id=target.chat_id,
                    )
                )
            if (
                not target.is_whole_chat
                and target.own_messages > 0
                and target.context_messages <= 0
            ):
                warnings.append(
                    ReportWarning(
                        code="no_context_coverage",
                        severity="warn",
                        message="Target has no context coverage.",
                        user_id=target.user_id,
                        chat_id=target.chat_id,
                    )
                )
            if (
                target.last_sync_at <= 0
                or target.last_sync_at <= self.now_ts - self.STALE_SYNC_SECONDS
            ) and (target.linked_messages > 0 or target.last_msg_id > 0):
                warnings.append(
                    ReportWarning(
                        code="stale_sync",
                        severity="warn",
                        message="Target sync state is stale.",
                        user_id=target.user_id,
                        chat_id=target.chat_id,
                    )
                )
            export_state = export_map.get(target.user_id)
            if (
                export_state is not None
                and target.linked_messages > 0
                and export_state.artifact_count <= 0
            ):
                warnings.append(
                    ReportWarning(
                        code="missing_export_state",
                        severity="warn",
                        message="Target has linked data but no local export artifact.",
                        user_id=target.user_id,
                        chat_id=target.chat_id,
                    )
                )
        warnings.sort(
            key=lambda item: (item.severity, item.code, item.chat_id, item.user_id)
        )
        return warnings


def render_report_json(report: AuditReport) -> str:
    payload = {
        "generated_at": report.generated_at,
        "database": asdict(report.database),
        "retry": asdict(report.retry),
        "targets": [asdict(target) for target in report.targets],
        "exports": [asdict(export_state) for export_state in report.exports],
        "retry_tasks": report.retry_tasks,
        "warnings": [asdict(warning) for warning in report.warnings],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)


def render_report_markdown(report: AuditReport) -> str:
    lines = [
        "# Audit Report",
        "",
        f"- Generated at: {datetime.fromtimestamp(report.generated_at, tz=timezone.utc).isoformat()}",
        f"- Messages: {report.database.messages_count}",
        f"- Targets: {report.database.targets_count}",
        f"- Incomplete targets: {report.database.incomplete_targets_count}",
        f"- Retry tasks: {report.retry.total_tasks}",
        "",
        "## Database",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Chats | {report.database.chats_count} |",
        f"| Users | {report.database.users_count} |",
        f"| Messages | {report.database.messages_count} |",
        f"| Target links | {report.database.target_links_count} |",
        f"| Context clusters | {report.database.context_cluster_count} |",
        f"| Reply messages | {report.database.reply_messages_count} |",
        f"| Missing parents | {report.database.missing_parent_count} |",
        "",
        "## Retry",
        "",
        "| Status | Count |",
        "| --- | ---: |",
        f"| Pending | {report.retry.pending_tasks} |",
        f"| Retrying | {report.retry.retrying_tasks} |",
        f"| Failed | {report.retry.failed_tasks} |",
        f"| Completed | {report.retry.completed_tasks} |",
        f"| Due now | {report.retry.due_tasks} |",
        "",
        "## Targets",
        "",
        "| Target | Chat | Complete | Linked | Own | Context | Retry artifacts |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    export_map = {item.user_id: item for item in report.exports}
    for target in report.targets:
        export_state = export_map.get(target.user_id)
        export_count = export_state.artifact_count if export_state else 0
        label = target.author_name or f"ID:{target.user_id}"
        chat = target.chat_title or str(target.chat_id)
        lines.append(
            f"| {label} ({target.user_id}) | {chat} | {'yes' if target.is_complete else 'no'} | "
            f"{target.linked_messages} | {target.own_messages} | {target.context_messages} | {export_count} |"
        )

    lines.extend(["", "## Warnings", ""])
    if not report.warnings:
        lines.append("- None")
    else:
        for warning in report.warnings:
            scope = ""
            if warning.user_id or warning.chat_id:
                scope = f" (chat={warning.chat_id}, user={warning.user_id})"
            lines.append(
                f"- `{warning.severity}` `{warning.code}`{scope}: {warning.message}"
            )
    return "\n".join(lines)
