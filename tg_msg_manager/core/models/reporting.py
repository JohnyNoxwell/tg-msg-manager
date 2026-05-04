from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class ReportDatabaseSummary:
    chats_count: int = 0
    users_count: int = 0
    messages_count: int = 0
    targets_count: int = 0
    incomplete_targets_count: int = 0
    target_links_count: int = 0
    reply_messages_count: int = 0
    missing_parent_count: int = 0
    context_cluster_count: int = 0

    @property
    def missing_parent_ratio(self) -> float:
        if self.reply_messages_count <= 0:
            return 0.0
        return self.missing_parent_count / self.reply_messages_count


@dataclass(frozen=True)
class ReportTargetSummary:
    user_id: int = 0
    chat_id: int = 0
    author_name: Optional[str] = None
    chat_title: Optional[str] = None
    last_msg_id: int = 0
    tail_msg_id: int = 0
    is_complete: bool = False
    deep_mode: bool = False
    recursive_depth: int = 0
    last_sync_at: int = 0
    linked_messages: int = 0
    own_messages: int = 0
    context_messages: int = 0
    missing_parent_messages: int = 0

    @property
    def is_whole_chat(self) -> bool:
        return self.user_id == self.chat_id

    @property
    def context_coverage_ratio(self) -> float:
        if self.own_messages <= 0:
            return 0.0
        return self.context_messages / self.own_messages


@dataclass(frozen=True)
class ReportRetrySummary:
    total_tasks: int = 0
    pending_tasks: int = 0
    retrying_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    due_tasks: int = 0


@dataclass(frozen=True)
class ReportExportState:
    user_id: int = 0
    artifact_count: int = 0
    latest_artifact_path: Optional[str] = None
    latest_modified_at: int = 0
    formats: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReportWarning:
    code: str
    severity: str
    message: str
    user_id: int = 0
    chat_id: int = 0


@dataclass
class AuditReport:
    generated_at: int
    database: ReportDatabaseSummary
    retry: ReportRetrySummary
    targets: list[ReportTargetSummary] = field(default_factory=list)
    exports: list[ReportExportState] = field(default_factory=list)
    retry_tasks: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[ReportWarning] = field(default_factory=list)
