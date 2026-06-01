import sqlite3
from collections.abc import Callable

from .inspection import (
    context_links_has_chat_scope,
    target_links_has_chat_scope,
)


def create_indexes(
    conn: sqlite3.Connection,
    *,
    create_user_identity_indexes: Callable[[sqlite3.Connection], None],
) -> None:
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_msg_user_chat_time ON messages (user_id, chat_id, timestamp)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_msg_standalone_id ON messages (message_id)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_msg_chat_reply ON messages (chat_id, reply_to_id)"
    )
    create_context_link_indexes(conn)
    create_target_link_indexes(conn)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_export_targets_updated_at ON export_targets (updated_at)"
    )
    create_export_runs_indexes(conn)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_msg_context_group ON messages (context_group_id)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_retry_queue_due ON retry_queue (status, next_retry_timestamp)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_retry_queue_type ON retry_queue (task_type, status)"
    )
    create_missing_reply_ref_indexes(conn)
    create_user_identity_indexes(conn)


def create_context_link_indexes(conn: sqlite3.Connection) -> None:
    if not context_links_has_chat_scope(conn):
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


def create_target_link_indexes(conn: sqlite3.Connection) -> None:
    if not target_links_has_chat_scope(conn):
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


def create_missing_reply_ref_indexes(conn: sqlite3.Connection) -> None:
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


def create_export_runs_indexes(conn: sqlite3.Connection) -> None:
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
