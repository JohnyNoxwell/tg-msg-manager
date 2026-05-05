from typing import List, Optional, Protocol, runtime_checkable

from ....core.models.retry import RetryTaskStatus
from ...storage.records import RetryTaskRecord


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
