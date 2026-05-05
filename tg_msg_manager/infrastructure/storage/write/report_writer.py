import time
from typing import Optional


def upsert_export_target(
    storage,
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
    now = int(time.time())
    with storage._write_transaction() as conn:
        conn.execute(
            """
            INSERT INTO export_targets (
                target_user_id,
                export_filename,
                export_dir,
                last_exported_message_ts,
                last_exported_message_id,
                export_part_count,
                artifact_message_count,
                artifact_first_message_id,
                artifact_last_message_id,
                artifact_first_timestamp,
                artifact_last_timestamp,
                artifact_as_json,
                artifact_include_date,
                artifact_json_profile,
                last_known_author_name,
                last_known_username,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(target_user_id) DO UPDATE SET
                export_filename = COALESCE(excluded.export_filename, export_targets.export_filename),
                export_dir = COALESCE(excluded.export_dir, export_targets.export_dir),
                last_exported_message_ts = COALESCE(excluded.last_exported_message_ts, export_targets.last_exported_message_ts),
                last_exported_message_id = COALESCE(excluded.last_exported_message_id, export_targets.last_exported_message_id),
                export_part_count = COALESCE(excluded.export_part_count, export_targets.export_part_count),
                artifact_message_count = COALESCE(excluded.artifact_message_count, export_targets.artifact_message_count),
                artifact_first_message_id = COALESCE(excluded.artifact_first_message_id, export_targets.artifact_first_message_id),
                artifact_last_message_id = COALESCE(excluded.artifact_last_message_id, export_targets.artifact_last_message_id),
                artifact_first_timestamp = COALESCE(excluded.artifact_first_timestamp, export_targets.artifact_first_timestamp),
                artifact_last_timestamp = COALESCE(excluded.artifact_last_timestamp, export_targets.artifact_last_timestamp),
                artifact_as_json = COALESCE(excluded.artifact_as_json, export_targets.artifact_as_json),
                artifact_include_date = COALESCE(excluded.artifact_include_date, export_targets.artifact_include_date),
                artifact_json_profile = COALESCE(excluded.artifact_json_profile, export_targets.artifact_json_profile),
                last_known_author_name = COALESCE(excluded.last_known_author_name, export_targets.last_known_author_name),
                last_known_username = COALESCE(excluded.last_known_username, export_targets.last_known_username),
                updated_at = excluded.updated_at
        """,
            (
                target_user_id,
                export_filename,
                export_dir,
                last_exported_message_ts,
                last_exported_message_id,
                export_part_count,
                artifact_message_count,
                artifact_first_message_id,
                artifact_last_message_id,
                artifact_first_timestamp,
                artifact_last_timestamp,
                1 if artifact_as_json else 0 if artifact_as_json is not None else None,
                1 if artifact_include_date else 0 if artifact_include_date is not None else None,
                str(artifact_json_profile) if artifact_json_profile else None,
                storage._normalize_identity_text(last_known_author_name),
                storage._normalize_identity_text(last_known_username),
                now,
                now,
            ),
        )


def start_export_run(storage, *, target_user_id: int) -> int:
    now = int(time.time())
    with storage._write_transaction() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO export_targets (
                target_user_id,
                export_filename,
                export_dir,
                last_exported_message_ts,
                last_exported_message_id,
                export_part_count,
                artifact_message_count,
                artifact_first_message_id,
                artifact_last_message_id,
                artifact_first_timestamp,
                artifact_last_timestamp,
                artifact_as_json,
                artifact_include_date,
                artifact_json_profile,
                last_known_author_name,
                last_known_username,
                created_at,
                updated_at
            )
            VALUES (?, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, ?, ?)
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
            (target_user_id, now, storage._EXPORT_RUN_ACTIVE),
        )
        return int(cursor.lastrowid)


def finish_export_run(
    storage,
    run_id: int,
    *,
    status: str,
    new_messages_count: int = 0,
    last_new_message_ts: Optional[int] = None,
    error: Optional[str] = None,
) -> None:
    finished_at = int(time.time())
    with storage._write_transaction() as conn:
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
