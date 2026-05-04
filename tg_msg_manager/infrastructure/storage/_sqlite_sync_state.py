import logging
import json
import time
from typing import Optional
from typing import List, Optional, Union

from .records import DeleteUserDataResult, TerminalRepairCandidate
from ...core.models.retry import RetryTaskStatus

logger = logging.getLogger(__name__)


class SQLiteSyncStateMixin:
    _EXPORT_RUN_ACTIVE = "running"

    def repair_terminal_incomplete_targets(
        self, tail_threshold: int = 1
    ) -> List[TerminalRepairCandidate]:
        """
        Reconcile sync targets that are logically complete at the bottom of history
        but still carry a stale `is_complete = 0` flag from older interrupted flows.

        Safe scope:
        - only targets with `last_msg_id > 0`
        - only targets with `is_complete = 0`
        - only targets with `tail_msg_id <= tail_threshold`

        The repair intentionally preserves `last_sync_at`; this is metadata cleanup,
        not a new successful sync.
        """
        with self._write_transaction() as conn:
            rows = conn.execute(
                """
                SELECT user_id, chat_id, author_name, last_msg_id, tail_msg_id, is_complete, last_sync_at
                FROM sync_targets
                WHERE is_complete = 0
                  AND last_msg_id > 0
                  AND tail_msg_id <= ?
                ORDER BY chat_id, user_id
                """,
                (tail_threshold,),
            ).fetchall()
            repaired = [TerminalRepairCandidate.coerce(dict(row)) for row in rows]
            if repaired:
                conn.execute(
                    """
                    UPDATE sync_targets
                    SET tail_msg_id = 0, is_complete = 1
                    WHERE is_complete = 0
                      AND last_msg_id > 0
                      AND tail_msg_id <= ?
                    """,
                    (tail_threshold,),
                )
            return repaired

    def update_sync_tail(
        self, chat_id: int, user_id: int, tail_id: int, is_complete: bool = False
    ):
        with self._write_transaction() as conn:
            conn.execute(
                """
                UPDATE sync_targets
                SET tail_msg_id = ?, is_complete = ?
                WHERE user_id = ? AND chat_id = ?
            """,
                (tail_id, 1 if is_complete else 0, user_id, chat_id),
            )

    def update_last_msg_id(self, chat_id: int, user_id: int, last_msg_id: int):
        with self._write_transaction() as conn:
            conn.execute(
                """
                UPDATE sync_targets
                SET last_msg_id = MAX(last_msg_id, ?)
                WHERE user_id = ? AND chat_id = ?
            """,
                (last_msg_id, user_id, chat_id),
            )

    def update_last_sync_at(self, chat_id: int, user_id: int):
        with self._write_transaction() as conn:
            conn.execute(
                """
                UPDATE sync_targets SET last_sync_at = ?
                WHERE user_id = ? AND chat_id = ?
            """,
                (int(time.time()), user_id, chat_id),
            )

    def get_last_target_msg_id(self, chat_id: int, user_id: int) -> int:
        status = self.get_sync_status(chat_id, user_id)
        return status.last_msg_id

    def upsert_user(
        self,
        user_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
        phone: Optional[str] = None,
        author_name: Optional[str] = None,
    ):
        with self._write_transaction() as conn:
            self._upsert_user_in_conn(
                conn, user_id, first_name, last_name, username, phone, author_name
            )
            self._record_user_identity_in_conn(
                conn,
                user_id=user_id,
                author_name=author_name,
                username=username,
            )

    def _upsert_user_in_conn(
        self,
        conn,
        user_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
        phone: Optional[str] = None,
        author_name: Optional[str] = None,
    ):
        normalized_author_name = self._normalize_identity_text(author_name)
        conn.execute(
            """
            INSERT INTO users (user_id, first_name, last_name, username, phone, current_author_name)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                first_name = COALESCE(excluded.first_name, users.first_name),
                last_name = COALESCE(excluded.last_name, users.last_name),
                username = COALESCE(excluded.username, users.username),
                phone = COALESCE(excluded.phone, users.phone),
                current_author_name = COALESCE(excluded.current_author_name, users.current_author_name)
        """,
            (user_id, first_name, last_name, username, phone, normalized_author_name),
        )
        self._refresh_target_author_name_in_conn(conn, user_id, normalized_author_name)

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
    ):
        now = int(time.time())
        with self._write_transaction() as conn:
            conn.execute(
                """
                INSERT INTO sync_targets (user_id, chat_id, author_name, added_at, last_sync_at, deep_mode, recursive_depth)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id, chat_id) DO UPDATE SET
                    author_name = excluded.author_name,
                    deep_mode = MAX(sync_targets.deep_mode, excluded.deep_mode),
                    recursive_depth = MAX(sync_targets.recursive_depth, excluded.recursive_depth)
            """,
                (
                    user_id,
                    chat_id,
                    author_name,
                    now,
                    now,
                    1 if deep_mode else 0,
                    recursive_depth,
                ),
            )
            self._upsert_user_in_conn(
                conn,
                user_id,
                first_name,
                last_name,
                username,
                author_name=author_name,
            )
            self._record_user_identity_in_conn(
                conn,
                user_id=user_id,
                author_name=author_name,
                username=username,
                observed_at=now,
                chat_id=chat_id,
                source_message_id=None,
            )

    def upsert_chat(self, chat_id: int, title: str, chat_type: Optional[str] = None):
        with self._write_transaction() as conn:
            self._upsert_chat_in_conn(conn, chat_id, title, chat_type)

    def upsert_export_target(
        self,
        *,
        target_user_id: int,
        export_filename: Optional[str] = None,
        export_dir: Optional[str] = None,
        last_exported_message_ts: Optional[int] = None,
        last_exported_message_id: Optional[int] = None,
        last_known_author_name: Optional[str] = None,
        last_known_username: Optional[str] = None,
    ):
        now = int(time.time())
        with self._write_transaction() as conn:
            conn.execute(
                """
                INSERT INTO export_targets (
                    target_user_id,
                    export_filename,
                    export_dir,
                    last_exported_message_ts,
                    last_exported_message_id,
                    last_known_author_name,
                    last_known_username,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(target_user_id) DO UPDATE SET
                    export_filename = COALESCE(excluded.export_filename, export_targets.export_filename),
                    export_dir = COALESCE(excluded.export_dir, export_targets.export_dir),
                    last_exported_message_ts = COALESCE(
                        excluded.last_exported_message_ts,
                        export_targets.last_exported_message_ts
                    ),
                    last_exported_message_id = COALESCE(
                        excluded.last_exported_message_id,
                        export_targets.last_exported_message_id
                    ),
                    last_known_author_name = COALESCE(
                        excluded.last_known_author_name,
                        export_targets.last_known_author_name
                    ),
                    last_known_username = COALESCE(
                        excluded.last_known_username,
                        export_targets.last_known_username
                    ),
                    updated_at = excluded.updated_at
            """,
                (
                    target_user_id,
                    export_filename,
                    export_dir,
                    last_exported_message_ts,
                    last_exported_message_id,
                    self._normalize_identity_text(last_known_author_name),
                    self._normalize_identity_text(last_known_username),
                    now,
                    now,
                ),
            )

    def start_export_run(self, *, target_user_id: int) -> int:
        now = int(time.time())
        with self._write_transaction() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO export_targets (
                    target_user_id,
                    export_filename,
                    export_dir,
                    last_exported_message_ts,
                    last_exported_message_id,
                    last_known_author_name,
                    last_known_username,
                    created_at,
                    updated_at
                )
                VALUES (?, NULL, NULL, NULL, NULL, NULL, NULL, ?, ?)
            """,
                (target_user_id, now, now),
            )
            cursor = conn.execute(
                """
                INSERT INTO export_runs (
                    target_user_id,
                    started_at,
                    finished_at,
                    new_messages_count,
                    last_new_message_ts,
                    status,
                    error
                )
                VALUES (?, ?, NULL, 0, NULL, ?, NULL)
            """,
                (target_user_id, now, self._EXPORT_RUN_ACTIVE),
            )
            return int(cursor.lastrowid)

    def finish_export_run(
        self,
        run_id: int,
        *,
        status: str,
        new_messages_count: int = 0,
        last_new_message_ts: Optional[int] = None,
        error: Optional[str] = None,
    ) -> None:
        finished_at = int(time.time())
        with self._write_transaction() as conn:
            conn.execute(
                """
                UPDATE export_runs
                SET
                    finished_at = ?,
                    new_messages_count = ?,
                    last_new_message_ts = ?,
                    status = ?,
                    error = ?
                WHERE id = ?
            """,
                (
                    finished_at,
                    int(new_messages_count),
                    last_new_message_ts,
                    str(status),
                    str(error) if error else None,
                    run_id,
                ),
            )

    def _upsert_chat_in_conn(
        self, conn, chat_id: int, title: str, chat_type: Optional[str] = None
    ):
        conn.execute(
            """
            INSERT INTO chats (chat_id, title, type)
            VALUES (?, ?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET
                title = COALESCE(NULLIF(excluded.title, ''), chats.title),
                type = COALESCE(excluded.type, chats.type)
        """,
            (chat_id, title, chat_type),
        )

    def delete_messages(self, chat_id: int, message_ids: List[int]) -> int:
        if not message_ids:
            return 0
        placeholders = ", ".join(["?"] * len(message_ids))
        with self._write_transaction() as conn:
            conn.execute(
                f"DELETE FROM message_target_links WHERE chat_id = ? AND message_id IN ({placeholders})",
                (chat_id, *message_ids),
            )
            res = conn.execute(
                f"DELETE FROM messages WHERE chat_id = ? AND message_id IN ({placeholders})",
                (chat_id, *message_ids),
            )
            return res.rowcount

    def delete_user_data(self, user_id: int) -> DeleteUserDataResult:
        with self._write_transaction() as conn:
            conn.execute(
                "DELETE FROM message_target_links WHERE target_user_id = ?", (user_id,)
            )
            res = conn.execute("""
                DELETE FROM messages
                WHERE NOT EXISTS (
                    SELECT 1 FROM message_target_links
                    WHERE message_target_links.chat_id = messages.chat_id
                    AND message_target_links.message_id = messages.message_id
                )
            """)
            deleted_msgs = res.rowcount
            target_res = conn.execute(
                "DELETE FROM sync_targets WHERE user_id = ?", (user_id,)
            )
            return DeleteUserDataResult(
                deleted_messages=deleted_msgs,
                deleted_targets=target_res.rowcount,
            )

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
    ):
        now = int(time.time())
        next_retry = (
            int(next_retry_timestamp) if next_retry_timestamp is not None else now + 300
        )
        payload_json = json.dumps(payload or {}, sort_keys=True)
        resolved_target_user_id = chat_id if target_user_id is None else target_user_id
        with self._write_transaction() as conn:
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

    def remove_retry_task(self, task_id: str):
        with self._write_transaction() as conn:
            conn.execute("DELETE FROM retry_queue WHERE task_id = ?", (task_id,))

    def mark_retry_task_completed(self, task_id: str):
        now = int(time.time())
        with self._write_transaction() as conn:
            conn.execute(
                """
                UPDATE retry_queue
                SET status = ?, updated_at = ?, completed_at = ?, last_error = NULL
                WHERE task_id = ?
            """,
                (RetryTaskStatus.COMPLETED.value, now, now, task_id),
            )

    def mark_retry_task_rescheduled(
        self, task_id: str, error: str, next_retry_timestamp: int
    ) -> str:
        now = int(time.time())
        with self._write_transaction() as conn:
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
                0
                if next_status == RetryTaskStatus.FAILED.value
                else next_retry_timestamp
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
        self, task_id: str, error: str, increment_retry_count: bool = False
    ) -> None:
        now = int(time.time())
        with self._write_transaction() as conn:
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
        self,
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
        with self._write_transaction() as conn:
            res = conn.execute(query, tuple(params))
            return res.rowcount
