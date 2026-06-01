import sqlite3
import time

from ..link_types import (
    CONTEXT_ALGO_LEGACY,
    CONTEXT_ALGO_REPLY_CONTEXT_V1,
    CONTEXT_LINK_REPLY_PARENT,
    CONTEXT_LINK_UNKNOWN,
    TARGET_LINK_LEGACY,
    TARGET_LINK_REPLY_CONTEXT,
    TARGET_LINK_TARGET_AUTHOR,
)
from .inspection import table_exists, target_links_has_metadata


def normalize_context_link_types(conn: sqlite3.Connection) -> None:
    if not table_exists(conn, "message_context_links"):
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


def reclassify_target_link_types(conn: sqlite3.Connection) -> None:
    if not table_exists(conn, "message_target_links"):
        return
    if not target_links_has_metadata(conn):
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


def backfill_export_targets(conn: sqlite3.Connection) -> None:
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


def backfill_missing_reply_refs(conn: sqlite3.Connection) -> None:
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
