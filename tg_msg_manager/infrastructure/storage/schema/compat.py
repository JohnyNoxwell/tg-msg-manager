import logging
import sqlite3
import time

from ....core.models.retry import RetryTaskStatus
from ..link_types import (
    CONTEXT_ALGO_LEGACY,
    CONTEXT_LINK_LEGACY,
)
from .indexes import create_context_link_indexes, create_target_link_indexes
from .inspection import (
    context_links_has_chat_scope,
    table_exists,
    target_links_has_metadata,
)

logger = logging.getLogger(__name__)


def ensure_sync_target_columns(conn: sqlite3.Connection) -> None:
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


def ensure_export_target_columns(conn: sqlite3.Connection) -> None:
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


def ensure_retry_queue_columns(conn: sqlite3.Connection) -> None:
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


def migrate_message_context_links_to_chat_safe(conn: sqlite3.Connection) -> None:
    if not table_exists(conn, "message_context_links"):
        create_context_link_indexes(conn)
        return

    if context_links_has_chat_scope(conn):
        create_context_link_indexes(conn)
        return

    now = int(time.time())
    backup_table = "message_context_links_legacy_backup"
    new_table = "message_context_links_new"
    if table_exists(conn, new_table):
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

    if table_exists(conn, backup_table):
        conn.execute(f"DROP TABLE {backup_table}")
    conn.execute(f"ALTER TABLE message_context_links RENAME TO {backup_table}")
    conn.execute(f"ALTER TABLE {new_table} RENAME TO message_context_links")
    create_context_link_indexes(conn)


def migrate_message_target_links_metadata(conn: sqlite3.Connection) -> None:
    if not table_exists(conn, "message_target_links"):
        create_target_link_indexes(conn)
        return

    if target_links_has_metadata(conn):
        create_target_link_indexes(conn)
        return

    now = int(time.time())
    backup_table = "message_target_links_legacy_backup"
    new_table = "message_target_links_new"
    if table_exists(conn, new_table):
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
        for row in conn.execute("PRAGMA table_info(message_target_links)").fetchall()
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

    if table_exists(conn, backup_table):
        conn.execute(f"DROP TABLE {backup_table}")
    conn.execute(f"ALTER TABLE message_target_links RENAME TO {backup_table}")
    conn.execute(f"ALTER TABLE {new_table} RENAME TO message_target_links")
    create_target_link_indexes(conn)


def resolve_legacy_context_link_chat_id(
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


def resolve_legacy_target_link_chat_id(
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


def migrate_sync_targets_to_composite_pk(conn: sqlite3.Connection) -> None:
    """Migration helper to move sync_targets to composite PRIMARY KEY."""
    try:
        conn.execute("DROP TABLE IF EXISTS sync_targets_new")
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


def migrate_existing_links(write_transaction) -> None:
    """
    Retroactively populates message_target_links for existing data.
    """
    now = int(time.time())
    with write_transaction() as conn:
        columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(message_target_links)").fetchall()
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
