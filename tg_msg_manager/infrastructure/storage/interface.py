from abc import ABC, abstractmethod
from typing import Iterable, List, Optional, Protocol, runtime_checkable

from ...core.models.message import MessageData
from ...core.models.retry import RetryTaskStatus
from ...core.models.reporting import (
    ReportDatabaseSummary,
    ReportRetrySummary,
    ReportTargetSummary,
)
from .records import (
    DeleteUserDataResult,
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


@runtime_checkable
class StorageLifecycle(Protocol):
    async def start(self) -> None:
        """Starts any background workers required by the storage backend."""

    async def flush(self) -> None:
        """Waits until queued writes are persisted."""

    async def close(self) -> None:
        """Closes the storage connection and background resources."""


@runtime_checkable
class StopAwareStorage(Protocol):
    def request_stop(self) -> None:
        """Requests cooperative shutdown for long-running storage operations."""

    def should_stop(self) -> bool:
        """Returns True when the current operation should stop early."""


@runtime_checkable
class MessageWriteStorage(Protocol):
    async def save_message(
        self,
        msg: MessageData,
        target_id: Optional[int] = None,
        flush: bool = True,
    ) -> bool:
        """Saves a single message."""

    async def save_messages(
        self,
        msgs: List[MessageData],
        target_id: Optional[int] = None,
        flush: bool = True,
    ) -> int:
        """Saves multiple messages in a single logical batch."""


@runtime_checkable
class MessageReadStorage(Protocol):
    def get_message(self, chat_id: int, message_id: int) -> Optional[MessageData]:
        """Retrieves a single stored message."""

    def message_exists(self, chat_id: int, message_id: int) -> bool:
        """Checks whether a message already exists."""

    def get_last_msg_id(self, chat_id: int) -> int:
        """Returns the highest stored message id for the chat."""

    def get_message_count(self, chat_id: int, target_id: Optional[int] = None) -> int:
        """Returns total stored messages for the chat or linked target."""

    def get_all_message_ids_for_chat(self, chat_id: int) -> List[int]:
        """Returns all stored message ids for the chat."""


@runtime_checkable
class UserReadStorage(Protocol):
    def get_unique_sync_users(self) -> List[SyncUser]:
        """Returns distinct users present in storage."""

    def get_user(self, user_id: int) -> Optional[StoredUser]:
        """Returns stored user metadata."""

    def get_user_identity_history(self, user_id: int) -> List[UserIdentityRecord]:
        """Returns observed author-name/username history for a user."""

    def get_user_messages(self, user_id: int) -> List[MessageData]:
        """Returns all messages linked to a target user."""

    def get_user_export_summary(self, user_id: int) -> Optional[UserExportSummary]:
        """Returns deterministic summary metadata for exports when available."""

    def iter_user_export_rows(
        self, user_id: int, chunk_size: int = 1000
    ) -> Iterable[UserExportRow]:
        """Streams export rows in deterministic order."""

    def get_user_export_rows(self, user_id: int) -> List[UserExportRow]:
        """Returns materialized export rows for legacy callers/backends."""


@runtime_checkable
class TargetLinkReadStorage(Protocol):
    def has_target_link(self, chat_id: int, message_id: int, target_id: int) -> bool:
        """Returns True when a message is already linked to a target."""

    def get_target_message_breakdown(
        self, chat_id: int, target_id: int
    ) -> TargetMessageBreakdown:
        """Returns linked-message totals for the target in a chat."""


@runtime_checkable
class TargetRegistryStorage(Protocol):
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
        """Registers or refreshes a tracked sync target."""

    def get_primary_targets(self) -> List[PrimaryTarget]:
        """Returns manually registered sync targets."""

    def upsert_user(
        self,
        user_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
        phone: Optional[str] = None,
        author_name: Optional[str] = None,
    ) -> None:
        """Upserts user metadata."""

    def upsert_chat(
        self, chat_id: int, title: str, chat_type: Optional[str] = None
    ) -> None:
        """Upserts chat metadata."""


@runtime_checkable
class SyncStateStorage(Protocol):
    def get_sync_status(self, chat_id: int, user_id: int) -> SyncStatus:
        """Returns sync state for a tracked chat/target pair."""

    def get_outdated_chats(self, threshold_seconds: int) -> List[tuple[int, int]]:
        """Returns chat/target pairs that should be refreshed."""

    def update_sync_tail(
        self, chat_id: int, user_id: int, tail_id: int, is_complete: bool = False
    ) -> None:
        """Persists tail-progress state for partial history scans."""

    def update_last_msg_id(self, chat_id: int, user_id: int, last_msg_id: int) -> None:
        """Persists head-progress state for incremental scans."""

    def update_last_sync_at(self, chat_id: int, user_id: int) -> None:
        """Marks a chat/target pair as freshly synced."""


@runtime_checkable
class CleanupStorage(Protocol):
    def delete_messages(self, chat_id: int, message_ids: List[int]) -> int:
        """Deletes specific messages from storage."""

    def delete_user_data(self, user_id: int) -> DeleteUserDataResult:
        """Deletes all locally stored data for a target user."""


@runtime_checkable
class CleanerStorage(MessageReadStorage, CleanupStorage, Protocol):
    """Storage contract required by CleanerService."""


@runtime_checkable
class ContextStorage(MessageWriteStorage, Protocol):
    def get_message(self, chat_id: int, message_id: int) -> Optional[MessageData]:
        """Retrieves a single stored message for deep-mode reply stitching."""


@runtime_checkable
class DBExportStorage(UserReadStorage, Protocol):
    """Storage contract required by DBExportService."""


@runtime_checkable
class PrivateArchiveStorage(
    MessageWriteStorage, MessageReadStorage, TargetRegistryStorage, Protocol
):
    def update_last_sync_at(self, chat_id: int, user_id: int) -> None:
        """Marks the PM archive target as freshly synced."""


@runtime_checkable
class ExportStorage(
    MessageWriteStorage,
    MessageReadStorage,
    UserReadStorage,
    TargetLinkReadStorage,
    TargetRegistryStorage,
    SyncStateStorage,
    StopAwareStorage,
    Protocol,
):
    async def flush(self) -> None:
        """Waits until queued writes are persisted."""


@runtime_checkable
class RetryStorage(Protocol):
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
        """Creates or refreshes a retry task."""

    def get_due_retry_tasks(
        self,
        now_ts: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[RetryTaskRecord]:
        """Returns due retry tasks in execution order."""

    def list_retry_tasks(
        self,
        limit: Optional[int] = None,
        include_completed: bool = True,
    ) -> List[RetryTaskRecord]:
        """Returns retry tasks for inspection."""

    def mark_retry_task_completed(self, task_id: str) -> None:
        """Marks a retry task as completed."""

    def mark_retry_task_rescheduled(
        self, task_id: str, error: str, next_retry_timestamp: int
    ) -> str:
        """Reschedules a retry task and returns the new status."""

    def mark_retry_task_failed(
        self, task_id: str, error: str, increment_retry_count: bool = False
    ) -> None:
        """Marks a retry task as terminally failed."""

    def cleanup_retry_tasks(
        self,
        statuses: Optional[List[str]] = None,
        older_than_timestamp: Optional[int] = None,
    ) -> int:
        """Removes terminal retry tasks."""


@runtime_checkable
class ReportStorage(Protocol):
    def get_report_database_summary(self) -> ReportDatabaseSummary:
        """Returns global database/reporting summary."""

    def get_report_target_summaries(self) -> List[ReportTargetSummary]:
        """Returns tracked target summaries for audit reporting."""

    def get_report_retry_summary(
        self, now_ts: Optional[int] = None
    ) -> ReportRetrySummary:
        """Returns aggregated retry queue state."""


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
    def iter_user_export_rows(
        self, user_id: int, chunk_size: int = 1000
    ) -> Iterable[UserExportRow]:
        pass

    @abstractmethod
    def get_user_export_rows(self, user_id: int) -> List[UserExportRow]:
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
