import time
from typing import Optional

from ..link_types import CONTEXT_ALGO_REPLY_CONTEXT_V1, CONTEXT_LINK_REPLY_PARENT


def upsert_context_link_in_conn(
    storage,
    conn,
    chat_id: int,
    message_id: int,
    reply_to_id: Optional[int],
):
    del storage
    if reply_to_id:
        conn.execute(
            """
            INSERT OR REPLACE INTO message_context_links (
                chat_id,
                message_id,
                context_message_id,
                link_type,
                distance,
                algorithm_version,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                chat_id,
                message_id,
                reply_to_id,
                CONTEXT_LINK_REPLY_PARENT,
                None,
                CONTEXT_ALGO_REPLY_CONTEXT_V1,
                int(time.time()),
            ),
        )


def refresh_missing_reply_state_in_conn(
    storage,
    conn,
    chat_id: int,
    message_id: int,
    reply_to_id: Optional[int],
) -> None:
    del storage
    if not reply_to_id:
        return
    now = int(time.time())
    parent_exists = conn.execute(
        """
        SELECT 1
        FROM messages
        WHERE chat_id = ? AND message_id = ?
    """,
        (chat_id, reply_to_id),
    ).fetchone()
    if parent_exists:
        conn.execute(
            """
            UPDATE missing_reply_refs
            SET status = 'resolved'
            WHERE chat_id = ?
              AND message_id = ?
              AND missing_reply_to_id = ?
        """,
            (chat_id, message_id, reply_to_id),
        )
        return

    conn.execute(
        """
        INSERT INTO missing_reply_refs (
            chat_id,
            message_id,
            missing_reply_to_id,
            detected_at,
            status
        )
        VALUES (?, ?, ?, ?, 'missing')
        ON CONFLICT(chat_id, message_id, missing_reply_to_id) DO UPDATE SET
            detected_at = excluded.detected_at,
            status = 'missing'
    """,
        (chat_id, message_id, reply_to_id, now),
    )


def resolve_missing_reply_refs_for_parent_in_conn(
    storage,
    conn,
    chat_id: int,
    message_id: int,
) -> None:
    del storage
    conn.execute(
        """
        UPDATE missing_reply_refs
        SET status = 'resolved'
        WHERE chat_id = ?
          AND missing_reply_to_id = ?
          AND status != 'resolved'
    """,
        (chat_id, message_id),
    )
