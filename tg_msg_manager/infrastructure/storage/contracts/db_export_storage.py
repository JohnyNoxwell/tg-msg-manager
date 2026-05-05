from typing import Optional, Protocol, runtime_checkable

from .common import UserReadStorage


@runtime_checkable
class DBExportStorage(UserReadStorage, Protocol):
    def start_export_run(self, *, target_user_id: int) -> int:
        """Creates a DB-backed export run and returns its id."""

    def finish_export_run(
        self,
        run_id: int,
        *,
        status: str,
        new_messages_count: int = 0,
        last_new_message_ts: Optional[int] = None,
        error: Optional[str] = None,
    ) -> None:
        """Closes a DB-backed export run."""

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
        """Persists DB-backed export state for a target user."""
