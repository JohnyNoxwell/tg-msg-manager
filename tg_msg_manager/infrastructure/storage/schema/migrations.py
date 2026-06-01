import logging
import sqlite3
import time

from ....core.models.retry import RetryTaskStatus

logger = logging.getLogger(__name__)


def run_migrations(
    conn: sqlite3.Connection,
    *,
    migrate_existing_links,
    sync_targets_has_composite_primary_key,
    migrate_sync_targets_to_composite_pk,
    ensure_user_identity_schema,
    create_user_identity_indexes,
    backfill_user_identity_state,
    migrate_message_context_links_to_chat_safe,
    migrate_message_target_links_metadata,
    backfill_export_targets,
    create_export_runs_table,
    create_export_runs_indexes,
    create_missing_reply_refs_table,
    create_missing_reply_ref_indexes,
    backfill_missing_reply_refs,
    normalize_context_link_types,
    create_context_link_indexes,
    reclassify_target_link_types,
    ensure_export_target_columns,
) -> None:
    current_version = conn.execute("PRAGMA user_version").fetchone()[0]
    if current_version < 2:
        logger.info("Running Database Migration: Version 2 (Target Attribution)...")
        migrate_existing_links()
        conn.execute("PRAGMA user_version = 2")
        logger.info("Database migration to Version 2 successful.")

    if current_version < 3:
        logger.info(
            "Running Database Migration: Version 3 (Composite PK for sync_targets)..."
        )
        if not sync_targets_has_composite_primary_key(conn):
            migrate_sync_targets_to_composite_pk()
        conn.execute("PRAGMA user_version = 3")
        logger.info("Database migration to Version 3 successful.")

    if current_version < 4:
        logger.info(
            "Running Database Migration: Version 4 (Persistent Sync Settings)..."
        )
        try:
            conn.execute(
                "ALTER TABLE sync_targets ADD COLUMN deep_mode INTEGER DEFAULT 0"
            )
            conn.execute(
                "ALTER TABLE sync_targets ADD COLUMN recursive_depth INTEGER DEFAULT 0"
            )
            conn.execute("ALTER TABLE sync_targets ADD COLUMN last_sync_at INTEGER")
        except Exception as e:
            logger.debug(f"Columns might already exist: {e}")
        conn.execute("PRAGMA user_version = 4")
        logger.info("Database migration to Version 4 successful.")

    if current_version < 5:
        logger.info("Running Database Migration: Version 5 (Retry lifecycle)...")
        now = int(time.time())
        conn.execute(
            """
            UPDATE retry_queue
            SET
                target_user_id = CASE
                    WHEN target_user_id IS NULL OR target_user_id = 0 THEN chat_id
                    ELSE target_user_id
                END,
                status = CASE
                    WHEN status IS NULL OR status = '' THEN ?
                    WHEN LOWER(status) = 'pending' AND COALESCE(retry_count, 0) > 0
                        THEN ?
                    ELSE LOWER(status)
                END,
                payload_json = COALESCE(NULLIF(payload_json, ''), '{}'),
                max_attempts = CASE
                    WHEN max_attempts IS NULL OR max_attempts <= 0 THEN 5
                    ELSE max_attempts
                END,
                next_retry_timestamp = COALESCE(next_retry_timestamp, 0),
                created_at = CASE
                    WHEN created_at IS NULL OR created_at = 0 THEN ?
                    ELSE created_at
                END,
                updated_at = CASE
                    WHEN updated_at IS NULL OR updated_at = 0 THEN ?
                    ELSE updated_at
                END,
                last_attempt_timestamp = COALESCE(last_attempt_timestamp, 0),
                completed_at = COALESCE(completed_at, 0)
        """,
            (
                RetryTaskStatus.RETRYING.value,
                RetryTaskStatus.RETRYING.value,
                now,
                now,
            ),
        )
        conn.execute("PRAGMA user_version = 5")
        logger.info("Database migration to Version 5 successful.")

    if current_version < 6:
        logger.info("Running Database Migration: Version 6 (User identity history)...")
        ensure_user_identity_schema(conn)
        create_user_identity_indexes(conn)
        backfill_user_identity_state(conn)
        conn.execute("PRAGMA user_version = 6")
        logger.info("Database migration to Version 6 successful.")

    if current_version < 7:
        logger.info(
            "Running Database Migration: Version 7 (Chat-safe context links)..."
        )
        migrate_message_context_links_to_chat_safe(conn)
        conn.execute("PRAGMA user_version = 7")
        logger.info("Database migration to Version 7 successful.")

    if current_version < 8:
        logger.info("Running Database Migration: Version 8 (Target link metadata)...")
        migrate_message_target_links_metadata(conn)
        conn.execute("PRAGMA user_version = 8")
        logger.info("Database migration to Version 8 successful.")

    if current_version < 9:
        logger.info("Running Database Migration: Version 9 (Export targets state)...")
        backfill_export_targets(conn)
        conn.execute("PRAGMA user_version = 9")
        logger.info("Database migration to Version 9 successful.")

    if current_version < 10:
        logger.info("Running Database Migration: Version 10 (Export runs journal)...")
        create_export_runs_table(conn)
        create_export_runs_indexes(conn)
        conn.execute("PRAGMA user_version = 10")
        logger.info("Database migration to Version 10 successful.")

    if current_version < 11:
        logger.info("Running Database Migration: Version 11 (Missing reply refs)...")
        create_missing_reply_refs_table(conn)
        create_missing_reply_ref_indexes(conn)
        backfill_missing_reply_refs(conn)
        conn.execute("PRAGMA user_version = 11")
        logger.info("Database migration to Version 11 successful.")

    if current_version < 12:
        logger.info(
            "Running Database Migration: Version 12 (Context link type normalization)..."
        )
        normalize_context_link_types(conn)
        create_context_link_indexes(conn)
        conn.execute("PRAGMA user_version = 12")
        logger.info("Database migration to Version 12 successful.")

    if current_version < 13:
        logger.info(
            "Running Database Migration: Version 13 (Target link reclassification)..."
        )
        reclassify_target_link_types(conn)
        conn.execute("PRAGMA user_version = 13")
        logger.info("Database migration to Version 13 successful.")

    if current_version < 14:
        logger.info(
            "Running Database Migration: Version 14 (DB-backed export artifact manifest)..."
        )
        ensure_export_target_columns(conn)
        conn.execute("PRAGMA user_version = 14")
        logger.info("Database migration to Version 14 successful.")
    else:
        logger.debug(
            f"Database migration skipped (already at version {current_version})."
        )
