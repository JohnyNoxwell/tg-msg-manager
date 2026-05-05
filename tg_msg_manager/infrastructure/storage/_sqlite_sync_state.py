import logging
from typing import List, Optional

from .write import (
    checkpoint_writer,
    message_writer,
    report_writer,
    retry_writer,
    user_writer,
)

logger = logging.getLogger(__name__)


class SQLiteSyncStateMixin:
    """
    DEPRECATED compatibility wrapper over the split SQLite state/write modules.
    """

    _EXPORT_RUN_ACTIVE = "running"

    def repair_terminal_incomplete_targets(self, tail_threshold: int = 1):
        return checkpoint_writer.repair_terminal_incomplete_targets(
            self, tail_threshold
        )

    def update_sync_tail(
        self, chat_id: int, user_id: int, tail_id: int, is_complete: bool = False
    ):
        return checkpoint_writer.update_sync_tail(
            self, chat_id, user_id, tail_id, is_complete
        )

    def update_last_msg_id(self, chat_id: int, user_id: int, last_msg_id: int):
        return checkpoint_writer.update_last_msg_id(
            self, chat_id, user_id, last_msg_id
        )

    def update_last_sync_at(self, chat_id: int, user_id: int):
        return checkpoint_writer.update_last_sync_at(self, chat_id, user_id)

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
        return user_writer.upsert_user(
            self,
            user_id,
            first_name,
            last_name,
            username,
            phone,
            author_name,
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
        return user_writer.upsert_user_in_conn(
            self,
            conn,
            user_id,
            first_name,
            last_name,
            username,
            phone,
            author_name,
        )

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
        return user_writer.register_target(
            self,
            user_id,
            author_name,
            chat_id,
            first_name,
            last_name,
            username,
            deep_mode,
            recursive_depth,
        )

    def upsert_chat(self, chat_id: int, title: str, chat_type: Optional[str] = None):
        return user_writer.upsert_chat(self, chat_id, title, chat_type)

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
    ):
        return report_writer.upsert_export_target(
            self,
            target_user_id=target_user_id,
            export_filename=export_filename,
            export_dir=export_dir,
            last_exported_message_ts=last_exported_message_ts,
            last_exported_message_id=last_exported_message_id,
            export_part_count=export_part_count,
            artifact_message_count=artifact_message_count,
            artifact_first_message_id=artifact_first_message_id,
            artifact_last_message_id=artifact_last_message_id,
            artifact_first_timestamp=artifact_first_timestamp,
            artifact_last_timestamp=artifact_last_timestamp,
            artifact_as_json=artifact_as_json,
            artifact_include_date=artifact_include_date,
            artifact_json_profile=artifact_json_profile,
            last_known_author_name=last_known_author_name,
            last_known_username=last_known_username,
        )

    def start_export_run(self, *, target_user_id: int) -> int:
        return report_writer.start_export_run(self, target_user_id=target_user_id)

    def finish_export_run(
        self,
        run_id: int,
        *,
        status: str,
        new_messages_count: int = 0,
        last_new_message_ts: Optional[int] = None,
        error: Optional[str] = None,
    ) -> None:
        return report_writer.finish_export_run(
            self,
            run_id,
            status=status,
            new_messages_count=new_messages_count,
            last_new_message_ts=last_new_message_ts,
            error=error,
        )

    def _upsert_chat_in_conn(
        self, conn, chat_id: int, title: str, chat_type: Optional[str] = None
    ):
        return user_writer.upsert_chat_in_conn(self, conn, chat_id, title, chat_type)

    def delete_messages(self, chat_id: int, message_ids: List[int]) -> int:
        return message_writer.delete_messages(self, chat_id, message_ids)

    def delete_user_data(self, user_id: int):
        return message_writer.delete_user_data(self, user_id)

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
        status: str = "pending",
    ):
        return retry_writer.enqueue_retry_task(
            self,
            task_id,
            chat_id,
            task_type,
            error,
            target_user_id=target_user_id,
            payload=payload,
            next_retry_timestamp=next_retry_timestamp,
            max_attempts=max_attempts,
            status=status,
        )

    def remove_retry_task(self, task_id: str):
        return retry_writer.remove_retry_task(self, task_id)

    def mark_retry_task_completed(self, task_id: str):
        return retry_writer.mark_retry_task_completed(self, task_id)

    def mark_retry_task_rescheduled(
        self, task_id: str, error: str, next_retry_timestamp: int
    ) -> str:
        return retry_writer.mark_retry_task_rescheduled(
            self, task_id, error, next_retry_timestamp
        )

    def mark_retry_task_failed(
        self, task_id: str, error: str, increment_retry_count: bool = False
    ) -> None:
        return retry_writer.mark_retry_task_failed(
            self,
            task_id,
            error,
            increment_retry_count=increment_retry_count,
        )

    def cleanup_retry_tasks(
        self,
        statuses: Optional[List[str]] = None,
        older_than_timestamp: Optional[int] = None,
    ) -> int:
        return retry_writer.cleanup_retry_tasks(
            self,
            statuses=statuses,
            older_than_timestamp=older_than_timestamp,
        )
