import json
import time
from typing import List, Optional, Union

from ....core.models.retry import RetryTaskStatus


def enqueue_retry_task(
    storage,
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
):
    now = int(time.time())
    next_retry = (
        int(next_retry_timestamp) if next_retry_timestamp is not None else now + 300
    )
    payload_json = json.dumps(payload or {}, sort_keys=True)
    resolved_target_user_id = chat_id if target_user_id is None else target_user_id
    with storage._write_transaction() as conn:
        conn.execute(
            """
            INSERT INTO retry_queue (
                task_id,
                chat_id,
                target_user_id,
                task_type,
                status,
                payload_json,
                retry_count,
                max_attempts,
                last_error,
                next_retry_timestamp,
                created_at,
                updated_at,
                last_attempt_timestamp,
                completed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, 0, 0)
            ON CONFLICT(task_id) DO UPDATE SET
                chat_id = excluded.chat_id,
                target_user_id = excluded.target_user_id,
                task_type = excluded.task_type,
                status = excluded.status,
                payload_json = excluded.payload_json,
                max_attempts = excluded.max_attempts,
                last_error = excluded.last_error,
                next_retry_timestamp = excluded.next_retry_timestamp,
                updated_at = excluded.updated_at,
                completed_at = 0
        """,
            (
                task_id,
                chat_id,
                resolved_target_user_id,
                task_type,
                status,
                payload_json,
                max_attempts,
                error,
                next_retry,
                now,
                now,
            ),
        )


def remove_retry_task(storage, task_id: str):
    with storage._write_transaction() as conn:
        conn.execute("DELETE FROM retry_queue WHERE task_id = ?", (task_id,))


def mark_retry_task_completed(storage, task_id: str):
    now = int(time.time())
    with storage._write_transaction() as conn:
        conn.execute(
            """
            UPDATE retry_queue
            SET status = ?, updated_at = ?, completed_at = ?, last_error = NULL
            WHERE task_id = ?
        """,
            (RetryTaskStatus.COMPLETED.value, now, now, task_id),
        )


def mark_retry_task_rescheduled(
    storage, task_id: str, error: str, next_retry_timestamp: int
) -> str:
    now = int(time.time())
    with storage._write_transaction() as conn:
        row = conn.execute(
            "SELECT retry_count, max_attempts FROM retry_queue WHERE task_id = ?",
            (task_id,),
        ).fetchone()
        if row is None:
            return RetryTaskStatus.FAILED.value
        retry_count = int(row["retry_count"] or 0) + 1
        max_attempts = int(row["max_attempts"] or 5)
        next_status = (
            RetryTaskStatus.FAILED.value
            if retry_count >= max_attempts
            else RetryTaskStatus.RETRYING.value
        )
        completed_at = now if next_status == RetryTaskStatus.FAILED.value else 0
        next_retry = (
            0 if next_status == RetryTaskStatus.FAILED.value else next_retry_timestamp
        )
        conn.execute(
            """
            UPDATE retry_queue
            SET
                retry_count = ?,
                status = ?,
                last_error = ?,
                next_retry_timestamp = ?,
                updated_at = ?,
                last_attempt_timestamp = ?,
                completed_at = ?
            WHERE task_id = ?
        """,
            (
                retry_count,
                next_status,
                error,
                next_retry,
                now,
                now,
                completed_at,
                task_id,
            ),
        )
        return next_status


def mark_retry_task_failed(
    storage,
    task_id: str,
    error: str,
    increment_retry_count: bool = False,
) -> None:
    now = int(time.time())
    with storage._write_transaction() as conn:
        row = conn.execute(
            "SELECT retry_count FROM retry_queue WHERE task_id = ?",
            (task_id,),
        ).fetchone()
        retry_count = int(row["retry_count"] or 0) if row else 0
        if increment_retry_count:
            retry_count += 1
        conn.execute(
            """
            UPDATE retry_queue
            SET
                retry_count = ?,
                status = ?,
                last_error = ?,
                next_retry_timestamp = 0,
                updated_at = ?,
                last_attempt_timestamp = ?,
                completed_at = ?
            WHERE task_id = ?
        """,
            (
                retry_count,
                RetryTaskStatus.FAILED.value,
                error,
                now,
                now,
                now,
                task_id,
            ),
        )


def cleanup_retry_tasks(
    storage,
    statuses: Optional[List[str]] = None,
    older_than_timestamp: Optional[int] = None,
) -> int:
    terminal_statuses = statuses or [
        RetryTaskStatus.COMPLETED.value,
        RetryTaskStatus.FAILED.value,
    ]
    placeholders = ", ".join(["?"] * len(terminal_statuses))
    params: List[Union[int, str]] = list(terminal_statuses)
    query = f"DELETE FROM retry_queue WHERE status IN ({placeholders})"
    if older_than_timestamp is not None:
        query += " AND updated_at <= ?"
        params.append(int(older_than_timestamp))
    with storage._write_transaction() as conn:
        res = conn.execute(query, tuple(params))
        return res.rowcount
