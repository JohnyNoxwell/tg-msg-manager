import logging
import sqlite3
import time

from ...core.models.retry import RetryTaskStatus
from .link_types import (
    CONTEXT_ALGO_LEGACY,
    CONTEXT_ALGO_REPLY_CONTEXT_V1,
    CONTEXT_LINK_LEGACY,
    CONTEXT_LINK_REPLY_PARENT,
    CONTEXT_LINK_UNKNOWN,
    TARGET_LINK_LEGACY,
    TARGET_LINK_REPLY_CONTEXT,
    TARGET_LINK_TARGET_AUTHOR,
)

logger = logging.getLogger(__name__)


class SQLiteSchemaMixin:
    def _init_db(self):
        """Initializes database schema and applies migrations."""
        conn = self._conn
        self._create_tables(conn)
        self._ensure_user_identity_schema(conn)
        self._ensure_export_target_columns(conn)
        self._ensure_sync_target_columns(conn)
        self._ensure_retry_queue_columns(conn)
        self._create_indexes(conn)
        self._run_migrations(conn)
        conn.commit()
        logger.info(
            f"SQLite Storage initialized at {self.db_path} with target attribution support."
        )

    def _create_tables(self, conn: sqlite3.Connection):
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                chat_id INTEGER,
                message_id INTEGER,
                user_id INTEGER,
                author_name TEXT,
                timestamp INTEGER,
                text TEXT,
                media_type TEXT,
                reply_to_id INTEGER,
                fwd_from_id INTEGER,
                context_group_id TEXT,
                raw_payload TEXT,
                payload_hash TEXT,
                schema_version INTEGER,
                PRIMARY KEY (chat_id, message_id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                username TEXT,
                phone TEXT,
                current_author_name TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                chat_id INTEGER PRIMARY KEY,
                title TEXT,
                type TEXT
            )
        """)
        # Legacy compatibility relation table. Active hot paths currently rely on
        # messages.reply_to_id, messages.context_group_id, and message_target_links.
        conn.execute("""
            CREATE TABLE IF NOT EXISTS message_context_links (
                chat_id INTEGER NOT NULL,
                message_id INTEGER,
                context_message_id INTEGER,
                link_type TEXT NOT NULL DEFAULT 'unknown',
                distance INTEGER,
                algorithm_version TEXT NOT NULL DEFAULT 'legacy',
                created_at INTEGER NOT NULL,
                PRIMARY KEY (chat_id, message_id, context_message_id, link_type, algorithm_version)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS message_target_links (
                chat_id INTEGER,
                message_id INTEGER,
                target_user_id INTEGER,
                link_type TEXT NOT NULL DEFAULT 'legacy',
                created_at INTEGER NOT NULL,
                PRIMARY KEY (chat_id, message_id, target_user_id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sync_state (
                chat_id INTEGER PRIMARY KEY,
                last_msg_id INTEGER DEFAULT 0,
                last_sync_timestamp INTEGER
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS retry_queue (
                task_id TEXT PRIMARY KEY,
                chat_id INTEGER,
                target_user_id INTEGER,
                task_type TEXT,
                status TEXT DEFAULT 'pending',
                payload_json TEXT DEFAULT '{}',
                retry_count INTEGER DEFAULT 0,
                max_attempts INTEGER DEFAULT 5,
                last_error TEXT,
                next_retry_timestamp INTEGER,
                created_at INTEGER DEFAULT 0,
                updated_at INTEGER DEFAULT 0,
                last_attempt_timestamp INTEGER DEFAULT 0,
                completed_at INTEGER DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sync_targets (
                user_id INTEGER,
                chat_id INTEGER,
                author_name TEXT,
                last_msg_id INTEGER DEFAULT 0,
                tail_msg_id INTEGER DEFAULT 0,
                is_complete INTEGER DEFAULT 0,
                deep_mode INTEGER DEFAULT 0,
                recursive_depth INTEGER DEFAULT 0,
                added_at INTEGER,
                last_sync_at INTEGER,
                PRIMARY KEY (user_id, chat_id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS export_targets (
                target_user_id INTEGER PRIMARY KEY,
                export_filename TEXT,
                export_dir TEXT,
                last_exported_message_ts INTEGER,
                last_exported_message_id INTEGER,
                export_part_count INTEGER,
                artifact_message_count INTEGER,
                artifact_first_message_id INTEGER,
                artifact_last_message_id INTEGER,
                artifact_first_timestamp INTEGER,
                artifact_last_timestamp INTEGER,
                artifact_as_json INTEGER,
                artifact_include_date INTEGER,
                artifact_json_profile TEXT,
                last_known_author_name TEXT,
                last_known_username TEXT,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS export_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_user_id INTEGER NOT NULL,
                started_at INTEGER NOT NULL,
                finished_at INTEGER,
                new_messages_count INTEGER NOT NULL DEFAULT 0,
                last_new_message_ts INTEGER,
                status TEXT NOT NULL,
                error TEXT,
                FOREIGN KEY (target_user_id)
                    REFERENCES export_targets(target_user_id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS missing_reply_refs (
                chat_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                missing_reply_to_id INTEGER NOT NULL,
                detected_at INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'missing',
                PRIMARY KEY (chat_id, message_id, missing_reply_to_id)
            )
        """)

    def _create_indexes(self, conn: sqlite3.Connection):
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_msg_user_chat_time ON messages (user_id, chat_id, timestamp)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_msg_standalone_id ON messages (message_id)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_msg_chat_reply ON messages (chat_id, reply_to_id)"
        )
        self._create_context_link_indexes(conn)
        self._create_target_link_indexes(conn)
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_export_targets_updated_at ON export_targets (updated_at)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_export_runs_target_started_at ON export_runs (target_user_id, started_at DESC)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_export_runs_status ON export_runs (status, started_at DESC)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_msg_context_group ON messages (context_group_id)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_retry_queue_due ON retry_queue (status, next_retry_timestamp)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_retry_queue_type ON retry_queue (task_type, status)"
        )
        self._create_missing_reply_ref_indexes(conn)
        self._create_user_identity_indexes(conn)

    def _ensure_sync_target_columns(self, conn: sqlite3.Connection):
        for col, col_type in [
            ("last_msg_id", "INTEGER DEFAULT 0"),
            ("tail_msg_id", "INTEGER DEFAULT 0"),
            ("is_complete", "INTEGER DEFAULT 0"),
            ("deep_mode", "INTEGER DEFAULT 0"),
            ("recursive_depth", "INTEGER DEFAULT 0"),
            ("last_sync_at", "INTEGER"),
        ]:
            try:
                conn.execute(f"ALTER TABLE sync_targets ADD COLUMN {col} {col_type}")
            except sqlite3.OperationalError:
                pass

    def _ensure_export_target_columns(self, conn: sqlite3.Connection):
        for col, col_type in [
            ("export_part_count", "INTEGER"),
            ("artifact_message_count", "INTEGER"),
            ("artifact_first_message_id", "INTEGER"),
            ("artifact_last_message_id", "INTEGER"),
            ("artifact_first_timestamp", "INTEGER"),
            ("artifact_last_timestamp", "INTEGER"),
            ("artifact_as_json", "INTEGER"),
            ("artifact_include_date", "INTEGER"),
            ("artifact_json_profile", "TEXT"),
        ]:
            try:
                conn.execute(f"ALTER TABLE export_targets ADD COLUMN {col} {col_type}")
            except sqlite3.OperationalError:
                pass

    def _ensure_retry_queue_columns(self, conn: sqlite3.Connection):
        for col, col_type in [
            ("target_user_id", "INTEGER"),
            ("status", f"TEXT DEFAULT '{RetryTaskStatus.PENDING.value}'"),
            ("payload_json", "TEXT DEFAULT '{}'"),
            ("max_attempts", "INTEGER DEFAULT 5"),
            ("created_at", "INTEGER DEFAULT 0"),
            ("updated_at", "INTEGER DEFAULT 0"),
            ("last_attempt_timestamp", "INTEGER DEFAULT 0"),
            ("completed_at", "INTEGER DEFAULT 0"),
        ]:
            try:
                conn.execute(f"ALTER TABLE retry_queue ADD COLUMN {col} {col_type}")
            except sqlite3.OperationalError:
                pass

    def _run_migrations(self, conn: sqlite3.Connection):
        current_version = conn.execute("PRAGMA user_version").fetchone()[0]
        if current_version < 2:
            logger.info("Running Database Migration: Version 2 (Target Attribution)...")
            self.migrate_existing_links()
            conn.execute("PRAGMA user_version = 2")
            logger.info("Database migration to Version 2 successful.")

        if current_version < 3:
            logger.info(
                "Running Database Migration: Version 3 (Composite PK for sync_targets)..."
            )
            self._migrate_sync_targets_to_composite_pk()
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
            logger.info(
                "Running Database Migration: Version 6 (User identity history)..."
            )
            self._ensure_user_identity_schema(conn)
            self._create_user_identity_indexes(conn)
            self._backfill_user_identity_state(conn)
            conn.execute("PRAGMA user_version = 6")
            logger.info("Database migration to Version 6 successful.")

        if current_version < 7:
            logger.info(
                "Running Database Migration: Version 7 (Chat-safe context links)..."
            )
            self._migrate_message_context_links_to_chat_safe(conn)
            conn.execute("PRAGMA user_version = 7")
            logger.info("Database migration to Version 7 successful.")

        if current_version < 8:
            logger.info(
                "Running Database Migration: Version 8 (Target link metadata)..."
            )
            self._migrate_message_target_links_metadata(conn)
            conn.execute("PRAGMA user_version = 8")
            logger.info("Database migration to Version 8 successful.")

        if current_version < 9:
            logger.info(
                "Running Database Migration: Version 9 (Export targets state)..."
            )
            self._backfill_export_targets(conn)
            conn.execute("PRAGMA user_version = 9")
            logger.info("Database migration to Version 9 successful.")

        if current_version < 10:
            logger.info(
                "Running Database Migration: Version 10 (Export runs journal)..."
            )
            self._create_export_runs_table(conn)
            self._create_export_runs_indexes(conn)
            conn.execute("PRAGMA user_version = 10")
            logger.info("Database migration to Version 10 successful.")

        if current_version < 11:
            logger.info(
                "Running Database Migration: Version 11 (Missing reply refs)..."
            )
            self._create_missing_reply_refs_table(conn)
            self._create_missing_reply_ref_indexes(conn)
            self._backfill_missing_reply_refs(conn)
            conn.execute("PRAGMA user_version = 11")
            logger.info("Database migration to Version 11 successful.")

        if current_version < 12:
            logger.info(
                "Running Database Migration: Version 12 (Context link type normalization)..."
            )
            self._normalize_context_link_types(conn)
            self._create_context_link_indexes(conn)
            conn.execute("PRAGMA user_version = 12")
            logger.info("Database migration to Version 12 successful.")

        if current_version < 13:
            logger.info(
                "Running Database Migration: Version 13 (Target link reclassification)..."
            )
            self._reclassify_target_link_types(conn)
            conn.execute("PRAGMA user_version = 13")
            logger.info("Database migration to Version 13 successful.")

        if current_version < 14:
            logger.info(
                "Running Database Migration: Version 14 (DB-backed export artifact manifest)..."
            )
            self._ensure_export_target_columns(conn)
            conn.execute("PRAGMA user_version = 14")
            logger.info("Database migration to Version 14 successful.")
        else:
            logger.debug(
                f"Database migration skipped (already at version {current_version})."
            )

    def _create_context_link_indexes(self, conn: sqlite3.Connection):
        if not self._context_links_has_chat_scope(conn):
            return
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_context_links_source
            ON message_context_links (chat_id, message_id)
        """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_context_links_context
            ON message_context_links (chat_id, context_message_id)
        """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_context_links_type
            ON message_context_links (link_type, algorithm_version)
        """
        )

    def _create_target_link_indexes(self, conn: sqlite3.Connection):
        if not self._target_links_has_chat_scope(conn):
            return
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_mt_link_target
            ON message_target_links (target_user_id)
        """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_mt_link_message
            ON message_target_links (chat_id, message_id)
        """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_mt_link_chat_target_msg
            ON message_target_links (chat_id, target_user_id, message_id)
        """
        )

    def _create_missing_reply_ref_indexes(self, conn: sqlite3.Connection):
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_missing_reply_refs_status
            ON missing_reply_refs (status, detected_at)
        """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_missing_reply_refs_parent
            ON missing_reply_refs (chat_id, missing_reply_to_id, status)
        """
        )

    def _context_links_has_chat_scope(self, conn: sqlite3.Connection) -> bool:
        columns = {
            row["name"]
            for row in conn.execute(
                "PRAGMA table_info(message_context_links)"
            ).fetchall()
        }
        return "chat_id" in columns and "algorithm_version" in columns

    def _target_links_has_chat_scope(self, conn: sqlite3.Connection) -> bool:
        columns = {
            row["name"]
            for row in conn.execute(
                "PRAGMA table_info(message_target_links)"
            ).fetchall()
        }
        return "chat_id" in columns

    def _target_links_has_metadata(self, conn: sqlite3.Connection) -> bool:
        columns = {
            row["name"]
            for row in conn.execute(
                "PRAGMA table_info(message_target_links)"
            ).fetchall()
        }
        return (
            "chat_id" in columns and "link_type" in columns and "created_at" in columns
        )

    def _migrate_message_context_links_to_chat_safe(self, conn: sqlite3.Connection):
        if not self._table_exists(conn, "message_context_links"):
            self._create_context_link_indexes(conn)
            return

        if self._context_links_has_chat_scope(conn):
            self._create_context_link_indexes(conn)
            return

        now = int(time.time())
        backup_table = "message_context_links_legacy_backup"
        new_table = "message_context_links_new"
        if self._table_exists(conn, new_table):
            conn.execute(f"DROP TABLE {new_table}")

        conn.execute(
            f"""
            CREATE TABLE {new_table} (
                chat_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                context_message_id INTEGER NOT NULL,
                link_type TEXT NOT NULL DEFAULT 'unknown',
                distance INTEGER,
                algorithm_version TEXT NOT NULL DEFAULT 'legacy',
                created_at INTEGER NOT NULL,
                PRIMARY KEY (chat_id, message_id, context_message_id, link_type, algorithm_version),
                FOREIGN KEY (chat_id, message_id)
                    REFERENCES messages(chat_id, message_id),
                FOREIGN KEY (chat_id, context_message_id)
                    REFERENCES messages(chat_id, message_id)
            )
        """
        )

        chat_rows = conn.execute(
            """
            SELECT DISTINCT chat_id
            FROM messages
            ORDER BY chat_id ASC
        """
        ).fetchall()
        if len(chat_rows) == 1:
            conn.execute(
                f"""
                INSERT OR IGNORE INTO {new_table} (
                    chat_id,
                    message_id,
                    context_message_id,
                    link_type,
                    distance,
                    algorithm_version,
                    created_at
                )
                SELECT
                    ?,
                    l.message_id,
                    l.context_message_id,
                    ?,
                    NULL,
                    ?,
                    ?
                FROM message_context_links l
                CROSS JOIN messages src INDEXED BY idx_msg_standalone_id
                CROSS JOIN messages ctx INDEXED BY idx_msg_standalone_id
                WHERE src.message_id = l.message_id
                  AND src.chat_id = ?
                  AND ctx.message_id = l.context_message_id
                  AND ctx.chat_id = ?
            """,
                (
                    int(chat_rows[0]["chat_id"]),
                    CONTEXT_LINK_LEGACY,
                    CONTEXT_ALGO_LEGACY,
                    now,
                    int(chat_rows[0]["chat_id"]),
                    int(chat_rows[0]["chat_id"]),
                ),
            )
        else:
            ambiguous_rows = conn.execute(
                """
                SELECT
                    l.message_id,
                    l.context_message_id,
                    COUNT(
                        DISTINCT CASE
                            WHEN ctx.message_id IS NOT NULL THEN src.chat_id
                            ELSE NULL
                        END
                    ) AS matched_chats
                FROM message_context_links l
                LEFT JOIN messages src
                  ON src.message_id = l.message_id
                LEFT JOIN messages ctx
                  ON ctx.chat_id = src.chat_id
                 AND ctx.message_id = l.context_message_id
                GROUP BY l.message_id, l.context_message_id
                HAVING matched_chats > 1
                LIMIT 1
            """
            ).fetchall()
            if ambiguous_rows:
                row = ambiguous_rows[0]
                conn.execute(f"DROP TABLE {new_table}")
                raise RuntimeError(
                    "Context-link migration aborted: could not resolve a unique chat_id for "
                    f"legacy link ({int(row['message_id'])} -> {int(row['context_message_id'])})."
                )

            conn.execute(
                f"""
                INSERT INTO {new_table} (
                    chat_id,
                    message_id,
                    context_message_id,
                    link_type,
                    distance,
                    algorithm_version,
                    created_at
                )
                SELECT
                    src.chat_id,
                    l.message_id,
                    l.context_message_id,
                    ?,
                    NULL,
                    ?,
                    ?
                FROM message_context_links l
                CROSS JOIN messages src INDEXED BY idx_msg_standalone_id
                CROSS JOIN messages ctx INDEXED BY idx_msg_standalone_id
                WHERE src.message_id = l.message_id
                  AND ctx.chat_id = src.chat_id
                  AND ctx.message_id = l.context_message_id
            """,
                (
                    CONTEXT_LINK_LEGACY,
                    CONTEXT_ALGO_LEGACY,
                    now,
                ),
            )

        if self._table_exists(conn, backup_table):
            conn.execute(f"DROP TABLE {backup_table}")
        conn.execute(f"ALTER TABLE message_context_links RENAME TO {backup_table}")
        conn.execute(f"ALTER TABLE {new_table} RENAME TO message_context_links")
        self._create_context_link_indexes(conn)

    def _normalize_context_link_types(self, conn: sqlite3.Connection):
        if not self._table_exists(conn, "message_context_links"):
            return
        conn.execute(
            """
            UPDATE message_context_links
            SET
                link_type = ?,
                distance = NULL
            WHERE link_type = 'reply'
        """,
            (CONTEXT_LINK_REPLY_PARENT,),
        )
        conn.execute(
            """
            UPDATE message_context_links
            SET algorithm_version = ?
            WHERE algorithm_version = 'reply_chain_v1'
        """,
            (CONTEXT_ALGO_REPLY_CONTEXT_V1,),
        )
        conn.execute(
            """
            UPDATE message_context_links
            SET link_type = ?
            WHERE COALESCE(TRIM(link_type), '') = ''
        """,
            (CONTEXT_LINK_UNKNOWN,),
        )
        conn.execute(
            """
            UPDATE message_context_links
            SET algorithm_version = ?
            WHERE COALESCE(TRIM(algorithm_version), '') = ''
        """,
            (CONTEXT_ALGO_LEGACY,),
        )

    def _migrate_message_target_links_metadata(self, conn: sqlite3.Connection):
        if not self._table_exists(conn, "message_target_links"):
            self._create_target_link_indexes(conn)
            return

        if self._target_links_has_metadata(conn):
            self._create_target_link_indexes(conn)
            return

        now = int(time.time())
        backup_table = "message_target_links_legacy_backup"
        new_table = "message_target_links_new"
        if self._table_exists(conn, new_table):
            conn.execute(f"DROP TABLE {new_table}")

        conn.execute(
            f"""
            CREATE TABLE {new_table} (
                chat_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                target_user_id INTEGER NOT NULL,
                link_type TEXT NOT NULL DEFAULT 'legacy',
                created_at INTEGER NOT NULL,
                PRIMARY KEY (chat_id, message_id, target_user_id),
                FOREIGN KEY (chat_id, message_id)
                    REFERENCES messages(chat_id, message_id)
            )
        """
        )

        columns = {
            row["name"]
            for row in conn.execute(
                "PRAGMA table_info(message_target_links)"
            ).fetchall()
        }
        if "chat_id" in columns:
            ambiguous_rows = conn.execute(
                """
                SELECT
                    l.message_id,
                    l.target_user_id,
                    COUNT(DISTINCT src.chat_id) AS matched_chats
                FROM message_target_links l
                LEFT JOIN messages src
                  ON src.message_id = l.message_id
                WHERE l.chat_id IS NULL
                GROUP BY l.message_id, l.target_user_id
                HAVING matched_chats > 1
                LIMIT 1
            """,
            ).fetchall()
            if ambiguous_rows:
                row = ambiguous_rows[0]
                conn.execute(f"DROP TABLE {new_table}")
                raise RuntimeError(
                    "Target-link migration aborted: could not resolve a unique chat_id for "
                    f"legacy target link ({int(row['message_id'])} -> {int(row['target_user_id'])})."
                )

            conn.execute(
                f"""
                INSERT OR IGNORE INTO {new_table} (
                    chat_id,
                    message_id,
                    target_user_id,
                    link_type,
                    created_at
                )
                SELECT
                    COALESCE(l.chat_id, src.chat_id),
                    l.message_id,
                    l.target_user_id,
                    ?,
                    ?
                FROM message_target_links l
                CROSS JOIN messages src INDEXED BY idx_msg_standalone_id
                WHERE src.message_id = l.message_id
                  AND (l.chat_id IS NULL OR src.chat_id = l.chat_id)
            """,
                ("legacy", now),
            )
        else:
            ambiguous_rows = conn.execute(
                """
                SELECT
                    l.message_id,
                    l.target_user_id,
                    COUNT(DISTINCT src.chat_id) AS matched_chats
                FROM message_target_links l
                LEFT JOIN messages src
                  ON src.message_id = l.message_id
                GROUP BY l.message_id, l.target_user_id
                HAVING matched_chats > 1
                LIMIT 1
            """
            ).fetchall()
            if ambiguous_rows:
                row = ambiguous_rows[0]
                conn.execute(f"DROP TABLE {new_table}")
                raise RuntimeError(
                    "Target-link migration aborted: could not resolve a unique chat_id for "
                    f"legacy target link ({int(row['message_id'])} -> {int(row['target_user_id'])})."
                )

            conn.execute(
                f"""
                INSERT OR IGNORE INTO {new_table} (
                    chat_id,
                    message_id,
                    target_user_id,
                    link_type,
                    created_at
                )
                SELECT
                    src.chat_id,
                    l.message_id,
                    l.target_user_id,
                    ?,
                    ?
                FROM message_target_links l
                CROSS JOIN messages src INDEXED BY idx_msg_standalone_id
                WHERE src.message_id = l.message_id
            """,
                ("legacy", now),
            )

        if self._table_exists(conn, backup_table):
            conn.execute(f"DROP TABLE {backup_table}")
        conn.execute(f"ALTER TABLE message_target_links RENAME TO {backup_table}")
        conn.execute(f"ALTER TABLE {new_table} RENAME TO message_target_links")
        self._create_target_link_indexes(conn)

    def _reclassify_target_link_types(self, conn: sqlite3.Connection):
        if not self._table_exists(conn, "message_target_links"):
            return
        if not self._target_links_has_metadata(conn):
            return

        conn.execute(
            """
            UPDATE message_target_links AS l
            SET link_type = ?
            WHERE EXISTS (
                SELECT 1
                FROM messages m
                WHERE m.chat_id = l.chat_id
                  AND m.message_id = l.message_id
                  AND m.user_id = l.target_user_id
            )
              AND l.link_type != ?
        """,
            (TARGET_LINK_TARGET_AUTHOR, TARGET_LINK_TARGET_AUTHOR),
        )
        conn.execute(
            """
            UPDATE message_target_links AS l
            SET link_type = ?
            WHERE l.link_type = ?
              AND EXISTS (
                  SELECT 1
                  FROM messages m
                  WHERE m.chat_id = l.chat_id
                    AND m.message_id = l.message_id
                    AND m.reply_to_id IS NOT NULL
              )
        """,
            (TARGET_LINK_REPLY_CONTEXT, TARGET_LINK_LEGACY),
        )

    def _resolve_legacy_context_link_chat_id(
        self,
        conn: sqlite3.Connection,
        *,
        message_id: int,
        context_message_id: int,
    ) -> int:
        chat_rows = conn.execute(
            """
            SELECT DISTINCT chat_id
            FROM messages
            ORDER BY chat_id ASC
        """
        ).fetchall()
        if len(chat_rows) == 1:
            return int(chat_rows[0]["chat_id"])

        rows = conn.execute(
            """
            SELECT src.chat_id
            FROM messages src
            JOIN messages ctx
              ON ctx.chat_id = src.chat_id
             AND ctx.message_id = ?
            WHERE src.message_id = ?
            GROUP BY src.chat_id
        """,
            (context_message_id, message_id),
        ).fetchall()
        if len(rows) == 1:
            return int(rows[0]["chat_id"])
        raise RuntimeError(
            "Context-link migration aborted: could not resolve a unique chat_id for "
            f"legacy link ({message_id} -> {context_message_id})."
        )

    def _resolve_legacy_target_link_chat_id(
        self,
        conn: sqlite3.Connection,
        *,
        message_id: int,
    ) -> int:
        chat_rows = conn.execute(
            """
            SELECT DISTINCT chat_id
            FROM messages
            ORDER BY chat_id ASC
        """
        ).fetchall()
        if len(chat_rows) == 1:
            return int(chat_rows[0]["chat_id"])

        rows = conn.execute(
            """
            SELECT DISTINCT chat_id
            FROM messages
            WHERE message_id = ?
        """,
            (message_id,),
        ).fetchall()
        if len(rows) == 1:
            return int(rows[0]["chat_id"])
        raise RuntimeError(
            "Target-link migration aborted: could not resolve a unique chat_id for "
            f"legacy target link message_id={message_id}."
        )

    def _table_exists(self, conn: sqlite3.Connection, table_name: str) -> bool:
        row = conn.execute(
            """
            SELECT 1
            FROM sqlite_master
            WHERE type = 'table' AND name = ?
        """,
            (table_name,),
        ).fetchone()
        return row is not None

    def _backfill_export_targets(self, conn: sqlite3.Connection):
        now = int(time.time())
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
            SELECT
                t.user_id,
                NULL,
                NULL,
                NULL,
                NULL,
                COALESCE(
                    NULLIF(u.current_author_name, ''),
                    NULLIF(t.author_name, '')
                ),
                NULLIF(u.username, ''),
                ?,
                ?
            FROM sync_targets t
            LEFT JOIN users u ON u.user_id = t.user_id
            GROUP BY t.user_id
        """,
            (now, now),
        )

    def _create_export_runs_table(self, conn: sqlite3.Connection):
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS export_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_user_id INTEGER NOT NULL,
                started_at INTEGER NOT NULL,
                finished_at INTEGER,
                new_messages_count INTEGER NOT NULL DEFAULT 0,
                last_new_message_ts INTEGER,
                status TEXT NOT NULL,
                error TEXT,
                FOREIGN KEY (target_user_id)
                    REFERENCES export_targets(target_user_id)
            )
        """
        )

    def _create_export_runs_indexes(self, conn: sqlite3.Connection):
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_export_runs_target_started_at
            ON export_runs (target_user_id, started_at DESC)
        """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_export_runs_status
            ON export_runs (status, started_at DESC)
        """
        )

    def _create_missing_reply_refs_table(self, conn: sqlite3.Connection):
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS missing_reply_refs (
                chat_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                missing_reply_to_id INTEGER NOT NULL,
                detected_at INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'missing',
                PRIMARY KEY (chat_id, message_id, missing_reply_to_id)
            )
        """
        )

    def _backfill_missing_reply_refs(self, conn: sqlite3.Connection):
        now = int(time.time())
        conn.execute(
            """
            INSERT OR IGNORE INTO missing_reply_refs (
                chat_id,
                message_id,
                missing_reply_to_id,
                detected_at,
                status
            )
            SELECT
                m.chat_id,
                m.message_id,
                m.reply_to_id,
                ?,
                'missing'
            FROM messages m
            LEFT JOIN messages parent
              ON parent.chat_id = m.chat_id
             AND parent.message_id = m.reply_to_id
            WHERE m.reply_to_id IS NOT NULL
              AND parent.message_id IS NULL
        """,
            (now,),
        )

    def _migrate_sync_targets_to_composite_pk(self):
        """Migration helper to move sync_targets to composite PRIMARY KEY."""
        conn = self._conn
        try:
            cursor = conn.execute("PRAGMA table_info(sync_targets)")
            cols = [row[1] for row in cursor.fetchall()]

            col_defs = []
            for c in cols:
                if c in ("user_id", "chat_id"):
                    col_defs.append(f"{c} INTEGER")
                elif c in (
                    "last_msg_id",
                    "tail_msg_id",
                    "is_complete",
                    "deep_mode",
                    "recursive_depth",
                    "added_at",
                    "last_sync_at",
                ):
                    col_defs.append(f"{c} INTEGER DEFAULT 0")
                else:
                    col_defs.append(f"{c} TEXT")

            col_list = ", ".join(col_defs)
            conn.execute(
                f"CREATE TABLE sync_targets_new ({col_list}, PRIMARY KEY (user_id, chat_id))"
            )

            col_names = ", ".join(cols)
            conn.execute(
                f"INSERT INTO sync_targets_new ({col_names}) SELECT {col_names} FROM sync_targets"
            )

            conn.execute("DROP TABLE sync_targets")
            conn.execute("ALTER TABLE sync_targets_new RENAME TO sync_targets")
            conn.commit()
            logger.info("Sync targets successfully migrated to composite Primary Key.")
        except Exception as e:
            logger.error(f"Migration error during PK update: {e}")
            try:
                conn.execute("DROP TABLE IF EXISTS sync_targets_new")
            except Exception:
                pass
            raise

    def migrate_existing_links(self):
        """
        Retroactively populates message_target_links for existing data.
        """
        now = int(time.time())
        with self._write_transaction() as conn:
            columns = {
                row["name"]
                for row in conn.execute(
                    "PRAGMA table_info(message_target_links)"
                ).fetchall()
            }
            if "link_type" in columns and "created_at" in columns:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO message_target_links (
                        chat_id,
                        message_id,
                        target_user_id,
                        link_type,
                        created_at
                    )
                    SELECT chat_id, message_id, user_id, 'legacy', ? FROM messages
                    WHERE user_id IN (SELECT user_id FROM sync_targets)
                """,
                    (now,),
                )
                conn.execute(
                    """
                    INSERT OR IGNORE INTO message_target_links (
                        chat_id,
                        message_id,
                        target_user_id,
                        link_type,
                        created_at
                    )
                    SELECT m.chat_id, m.message_id, t.target_user_id, 'legacy', ?
                    FROM messages m
                    JOIN (
                        SELECT DISTINCT m1.context_group_id, l.target_user_id, l.chat_id
                        FROM message_target_links l
                        JOIN messages m1 ON l.chat_id = m1.chat_id AND l.message_id = m1.message_id
                        WHERE m1.context_group_id IS NOT NULL
                    ) t ON m.chat_id = t.chat_id AND m.context_group_id = t.context_group_id
                """,
                    (now,),
                )
            else:
                conn.execute("""
                    INSERT OR IGNORE INTO message_target_links (chat_id, message_id, target_user_id)
                    SELECT chat_id, message_id, user_id FROM messages
                    WHERE user_id IN (SELECT user_id FROM sync_targets)
                """)
                conn.execute("""
                    INSERT OR IGNORE INTO message_target_links (chat_id, message_id, target_user_id)
                    SELECT m.chat_id, m.message_id, t.target_user_id
                    FROM messages m
                    JOIN (
                        SELECT DISTINCT m1.context_group_id, l.target_user_id, l.chat_id
                        FROM message_target_links l
                        JOIN messages m1 ON l.chat_id = m1.chat_id AND l.message_id = m1.message_id
                        WHERE m1.context_group_id IS NOT NULL
                    ) t ON m.chat_id = t.chat_id AND m.context_group_id = t.context_group_id
                """)
        logger.info("Database migration: Message attribution links populated.")
