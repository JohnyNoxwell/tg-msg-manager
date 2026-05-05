from abc import ABC, abstractmethod
from typing import Iterable, List, Optional

from ...core.models.message import MessageData
from ...core.models.retry import RetryTaskStatus
from .contracts.analytics_storage import AnalyticsStorage
from .contracts.cleaner_storage import CleanerStorage
from .contracts.common import (
    CleanupStorage,
    MessageReadStorage,
    MessageWriteStorage,
    StopAwareStorage,
    StorageLifecycle,
    SyncStateStorage,
    TargetLinkReadStorage,
    TargetRegistryStorage,
    UserReadStorage,
)
from .contracts.context_storage import ContextStorage
from .contracts.db_export_storage import DBExportStorage
from .contracts.export_storage import ExportStorage
from .contracts.private_archive_storage import PrivateArchiveStorage
from .contracts.report_storage import ReportStorage
from .contracts.retry_storage import RetryStorage
from .contracts.sync_storage import SyncStorage
from .records import (
    DeleteUserDataResult,
    ExportRunRecord,
    ExportTargetRecord,
    PrimaryTarget,
    RetryTaskRecord,
    StoredUser,
    SyncStatus,
    SyncUser,
    TargetMessageBreakdown,
    UserIdentityRecord,
    UserExportRow,
    UserExportSummary,
)

# Compatibility aggregator. New code should depend on narrow contracts.

__all__ = [
    "AnalyticsStorage",
    "CleanerStorage",
    "CleanupStorage",
    "ContextStorage",
    "DBExportStorage",
    "ExportStorage",
    "MessageReadStorage",
    "MessageWriteStorage",
    "PrivateArchiveStorage",
    "ReportStorage",
    "RetryStorage",
    "StopAwareStorage",
    "StorageLifecycle",
    "SyncStateStorage",
    "SyncStorage",
    "TargetLinkReadStorage",
    "TargetRegistryStorage",
    "UserReadStorage",
]


class BaseStorage(ABC):
    """
    Legacy umbrella storage contract.

    New code should prefer the narrower service-specific protocols above so each
    service depends only on the storage capabilities it actually uses.
    """

    @abstractmethod
    async def start(self) -> None:
        pass

    @abstractmethod
    async def save_message(
        self,
        msg: MessageData,
        target_id: Optional[int] = None,
        flush: bool = True,
    ) -> bool:
        pass

    @abstractmethod
    async def save_messages(
        self,
        msgs: List[MessageData],
        target_id: Optional[int] = None,
        flush: bool = True,
    ) -> int:
        pass

    @abstractmethod
    def get_message(self, chat_id: int, message_id: int) -> Optional[MessageData]:
        pass

    @abstractmethod
    def message_exists(self, chat_id: int, message_id: int) -> bool:
        pass

    @abstractmethod
    def get_last_msg_id(self, chat_id: int) -> int:
        pass

    @abstractmethod
    def get_outdated_chats(self, threshold_seconds: int) -> List[tuple[int, int]]:
        pass

    @abstractmethod
    def get_message_count(self, chat_id: int, target_id: Optional[int] = None) -> int:
        pass

    @abstractmethod
    def delete_messages(self, chat_id: int, message_ids: List[int]) -> int:
        pass

    @abstractmethod
    def get_all_message_ids_for_chat(self, chat_id: int) -> List[int]:
        pass

    @abstractmethod
    def get_unique_sync_users(self) -> List[SyncUser]:
        pass

    @abstractmethod
    def get_user(self, user_id: int) -> Optional[StoredUser]:
        pass

    @abstractmethod
    def get_user_identity_history(self, user_id: int) -> List[UserIdentityRecord]:
        pass

    @abstractmethod
    def get_user_messages(self, user_id: int) -> List[MessageData]:
        pass

    @abstractmethod
    def get_user_export_summary(self, user_id: int) -> Optional[UserExportSummary]:
        pass

    @abstractmethod
    def get_user_export_summary_since(
        self,
        user_id: int,
        last_exported_message_ts: int,
        last_exported_message_id: int,
    ) -> Optional[UserExportSummary]:
        pass

    @abstractmethod
    def iter_user_export_rows(
        self, user_id: int, chunk_size: int = 1000
    ) -> Iterable[UserExportRow]:
        pass

    @abstractmethod
    def iter_user_export_rows_since(
        self,
        user_id: int,
        last_exported_message_ts: int,
        last_exported_message_id: int,
        chunk_size: int = 1000,
    ) -> Iterable[UserExportRow]:
        pass

    @abstractmethod
    def get_user_export_rows(self, user_id: int) -> List[UserExportRow]:
        pass

    @abstractmethod
    def get_user_export_rows_since(
        self,
        user_id: int,
        last_exported_message_ts: int,
        last_exported_message_id: int,
    ) -> List[UserExportRow]:
        pass

    @abstractmethod
    def get_export_target(self, user_id: int) -> Optional[ExportTargetRecord]:
        pass

    @abstractmethod
    def list_export_runs(
        self, user_id: int, limit: Optional[int] = None
    ) -> List[ExportRunRecord]:
        pass

    @abstractmethod
    def get_target_message_breakdown(
        self, chat_id: int, target_id: int
    ) -> TargetMessageBreakdown:
        pass

    @abstractmethod
    def delete_user_data(self, user_id: int) -> DeleteUserDataResult:
        pass

    @abstractmethod
    def register_target(
        self,
        user_id: int,
        author_name: str,
        chat_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
        deep_mode: bool = False,
        recursive_depth: int = 0,
    ) -> None:
        pass

    @abstractmethod
    def get_primary_targets(self) -> List[PrimaryTarget]:
        pass

    @abstractmethod
    def upsert_user(
        self,
        user_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
        phone: Optional[str] = None,
        author_name: Optional[str] = None,
    ) -> None:
        pass

    @abstractmethod
    def get_sync_status(self, chat_id: int, user_id: int) -> SyncStatus:
        pass

    @abstractmethod
    def update_sync_tail(
        self, chat_id: int, user_id: int, tail_id: int, is_complete: bool = False
    ) -> None:
        pass

    @abstractmethod
    def update_last_msg_id(self, chat_id: int, user_id: int, last_msg_id: int) -> None:
        pass

    @abstractmethod
    def update_last_sync_at(self, chat_id: int, user_id: int) -> None:
        pass

    @abstractmethod
    def upsert_chat(
        self, chat_id: int, title: str, chat_type: Optional[str] = None
    ) -> None:
        pass

    @abstractmethod
    def upsert_export_target(
        self,
        *,
        target_user_id: int,
        export_filename: Optional[str] = None,
        export_dir: Optional[str] = None,
        last_exported_message_ts: Optional[int] = None,
        last_exported_message_id: Optional[int] = None,
        export_part_count: Optional[int] = None,
        artifact_message_count: Optional[int] = None,
        artifact_first_message_id: Optional[int] = None,
        artifact_last_message_id: Optional[int] = None,
        artifact_first_timestamp: Optional[int] = None,
        artifact_last_timestamp: Optional[int] = None,
        artifact_as_json: Optional[bool] = None,
        artifact_include_date: Optional[bool] = None,
        artifact_json_profile: Optional[str] = None,
        last_known_author_name: Optional[str] = None,
        last_known_username: Optional[str] = None,
    ) -> None:
        pass

    @abstractmethod
    def start_export_run(self, *, target_user_id: int) -> int:
        pass

    @abstractmethod
    def finish_export_run(
        self,
        run_id: int,
        *,
        status: str,
        new_messages_count: int = 0,
        last_new_message_ts: Optional[int] = None,
        error: Optional[str] = None,
    ) -> None:
        pass

    @abstractmethod
    def has_target_link(self, chat_id: int, message_id: int, target_id: int) -> bool:
        pass

    @abstractmethod
    def enqueue_retry_task(
        self,
        task_id: str,
        chat_id: int,
        task_type: str,
        error: str,
        *,
        target_user_id: Optional[int] = None,
        payload: Optional[dict] = None,
        next_retry_timestamp: Optional[int] = None,
        max_attempts: int = 5,
        status: str = RetryTaskStatus.PENDING.value,
    ) -> None:
        pass

    @abstractmethod
    def get_due_retry_tasks(
        self,
        now_ts: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[RetryTaskRecord]:
        pass

    @abstractmethod
    def list_retry_tasks(
        self,
        limit: Optional[int] = None,
        include_completed: bool = True,
    ) -> List[RetryTaskRecord]:
        pass

    @abstractmethod
    def mark_retry_task_completed(self, task_id: str) -> None:
        pass

    @abstractmethod
    def mark_retry_task_rescheduled(
        self, task_id: str, error: str, next_retry_timestamp: int
    ) -> str:
        pass

    @abstractmethod
    def mark_retry_task_failed(
        self, task_id: str, error: str, increment_retry_count: bool = False
    ) -> None:
        pass

    @abstractmethod
    def cleanup_retry_tasks(
        self,
        statuses: Optional[List[str]] = None,
        older_than_timestamp: Optional[int] = None,
    ) -> int:
        pass

    @abstractmethod
    def should_stop(self) -> bool:
        pass

    @abstractmethod
    def request_stop(self) -> None:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass

    @abstractmethod
    async def flush(self) -> None:
        pass
