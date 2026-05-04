import logging
import re
import time
from dataclasses import dataclass
from typing import Any, Optional, Union

from ..core.models.retry import RetryRunStats, RetryTaskStatus, RetryTaskType
from ..infrastructure.storage.interface import RetryStorage
from ..infrastructure.storage.records import RetryTaskRecord, SyncStatus

logger = logging.getLogger(__name__)


def build_sync_target_retry_task_id(chat_id: int, user_id: int) -> str:
    return f"{RetryTaskType.SYNC_TARGET.value}:{chat_id}:{user_id}"


def build_archive_pm_retry_task_id(user_id: int) -> str:
    return f"{RetryTaskType.ARCHIVE_PM.value}:{user_id}"


@dataclass(frozen=True)
class RetryBackoffPolicy:
    base_delay_seconds: int = 300
    max_delay_seconds: int = 21600

    def next_delay_seconds(
        self, attempt_number: int, explicit_delay_seconds: Optional[int] = None
    ) -> int:
        if explicit_delay_seconds is not None and explicit_delay_seconds > 0:
            return explicit_delay_seconds
        effective_attempt = max(attempt_number, 1)
        return min(
            self.max_delay_seconds,
            self.base_delay_seconds * (2 ** (effective_attempt - 1)),
        )


def detect_retry_delay_seconds(exc: Exception) -> Optional[int]:
    for attr_name in ("seconds", "value"):
        value = getattr(exc, attr_name, None)
        if isinstance(value, int) and value > 0:
            return value

    match = re.search(r"(\d+)\s*seconds?", str(exc), re.IGNORECASE)
    if match:
        try:
            delay_seconds = int(match.group(1))
        except ValueError:
            return None
        return delay_seconds if delay_seconds > 0 else None
    return None


def enqueue_sync_target_retry_task(
    storage: RetryStorage,
    *,
    chat_id: int,
    user_id: int,
    error: Union[Exception, str],
    backoff_policy: Optional[RetryBackoffPolicy] = None,
    max_attempts: int = 5,
) -> None:
    policy = backoff_policy or RetryBackoffPolicy()
    delay_seconds = (
        detect_retry_delay_seconds(error) if isinstance(error, Exception) else None
    )
    next_retry = int(time.time()) + policy.next_delay_seconds(1, delay_seconds)
    storage.enqueue_retry_task(
        build_sync_target_retry_task_id(chat_id, user_id),
        chat_id,
        RetryTaskType.SYNC_TARGET.value,
        str(error),
        target_user_id=user_id,
        payload={"chat_id": chat_id, "user_id": user_id},
        next_retry_timestamp=next_retry,
        max_attempts=max_attempts,
        status=RetryTaskStatus.PENDING.value,
    )


def enqueue_archive_pm_retry_task(
    storage: RetryStorage,
    *,
    user_id: int,
    error: Union[Exception, str],
    backoff_policy: Optional[RetryBackoffPolicy] = None,
    max_attempts: int = 5,
) -> None:
    policy = backoff_policy or RetryBackoffPolicy()
    delay_seconds = (
        detect_retry_delay_seconds(error) if isinstance(error, Exception) else None
    )
    next_retry = int(time.time()) + policy.next_delay_seconds(1, delay_seconds)
    storage.enqueue_retry_task(
        build_archive_pm_retry_task_id(user_id),
        user_id,
        RetryTaskType.ARCHIVE_PM.value,
        str(error),
        target_user_id=user_id,
        payload={"user_id": user_id},
        next_retry_timestamp=next_retry,
        max_attempts=max_attempts,
        status=RetryTaskStatus.PENDING.value,
    )


class RetryWorker:
    def __init__(
        self,
        *,
        storage: RetryStorage,
        client: Any,
        exporter: Any,
        private_archive: Any,
        backoff_policy: Optional[RetryBackoffPolicy] = None,
    ):
        self.storage = storage
        self.client = client
        self.exporter = exporter
        self.private_archive = private_archive
        self.backoff_policy = backoff_policy or RetryBackoffPolicy()

    async def run_due_tasks(self, limit: Optional[int] = None) -> RetryRunStats:
        stats = RetryRunStats()
        due_tasks = self.storage.get_due_retry_tasks(limit=limit)
        stats.scanned = len(due_tasks)
        for task in due_tasks:
            await self._run_task(task, stats)
        return stats

    async def _run_task(self, task: RetryTaskRecord, stats: RetryRunStats) -> None:
        try:
            if task.task_type in (
                RetryTaskType.SYNC_TARGET.value,
                RetryTaskType.EXPORT.value,
            ):
                await self._handle_sync_target(task)
            elif task.task_type == RetryTaskType.ARCHIVE_PM.value:
                await self._handle_archive_pm(task)
            else:
                raise ValueError(f"Unsupported retry task type: {task.task_type}")
        except Exception as exc:
            if isinstance(exc, ValueError) and "Unsupported retry task type" in str(
                exc
            ):
                self.storage.mark_retry_task_failed(
                    task.task_id, str(exc), increment_retry_count=False
                )
                stats.failed += 1
                return

            delay_seconds = detect_retry_delay_seconds(exc)
            next_retry = int(time.time()) + self.backoff_policy.next_delay_seconds(
                max(task.retry_count + 1, 1),
                delay_seconds,
            )
            next_status = self.storage.mark_retry_task_rescheduled(
                task.task_id, str(exc), next_retry
            )
            if next_status == RetryTaskStatus.FAILED.value:
                stats.failed += 1
            else:
                stats.rescheduled += 1
            logger.warning("Retry task %s failed: %s", task.task_id, exc)
            return

        self.storage.mark_retry_task_completed(task.task_id)
        stats.succeeded += 1

    async def _handle_sync_target(self, task: RetryTaskRecord) -> None:
        payload = task.payload
        chat_id = int(payload.get("chat_id") or task.chat_id)
        user_id = int(payload.get("user_id") or task.target_user_id or chat_id)
        entity = await self.client.get_entity(chat_id)
        status = SyncStatus.coerce(self.storage.get_sync_status(chat_id, user_id))
        await self.exporter.sync_chat(
            entity,
            from_user_id=None if user_id == chat_id else user_id,
            resume_history=not status.is_complete,
            resolve_user_entity=False,
            emit_summary=False,
        )

    async def _handle_archive_pm(self, task: RetryTaskRecord) -> None:
        payload = task.payload
        user_id = int(payload.get("user_id") or task.target_user_id or task.chat_id)
        user_entity = await self.client.get_entity(user_id)
        await self.private_archive.archive_pm(user_entity)
