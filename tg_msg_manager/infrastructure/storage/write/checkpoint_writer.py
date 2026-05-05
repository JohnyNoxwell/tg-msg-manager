import time
from typing import Optional

from ..records import TerminalRepairCandidate


def repair_terminal_incomplete_targets(storage, tail_threshold: int = 1):
    with storage._write_transaction() as conn:
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
    storage, chat_id: int, user_id: int, tail_id: int, is_complete: bool = False
):
    with storage._write_transaction() as conn:
        conn.execute(
            """
            UPDATE sync_targets
            SET tail_msg_id = ?, is_complete = ?
            WHERE user_id = ? AND chat_id = ?
        """,
            (tail_id, 1 if is_complete else 0, user_id, chat_id),
        )


def update_last_msg_id(storage, chat_id: int, user_id: int, last_msg_id: int):
    with storage._write_transaction() as conn:
        conn.execute(
            """
            UPDATE sync_targets
            SET last_msg_id = MAX(last_msg_id, ?)
            WHERE user_id = ? AND chat_id = ?
        """,
            (last_msg_id, user_id, chat_id),
        )


def update_last_sync_at(storage, chat_id: int, user_id: int):
    with storage._write_transaction() as conn:
        conn.execute(
            """
            UPDATE sync_targets SET last_sync_at = ?
            WHERE user_id = ? AND chat_id = ?
        """,
            (int(time.time()), user_id, chat_id),
        )


def update_sync_state_for_message_in_conn(
    storage,
    conn,
    chat_id: int,
    message_id: int,
    target_id: Optional[int],
):
    del storage
    now = int(time.time())
    conn.execute(
        """
        INSERT INTO sync_state (chat_id, last_msg_id, last_sync_timestamp)
        VALUES (?, ?, ?)
        ON CONFLICT(chat_id) DO UPDATE SET
            last_msg_id = MAX(last_msg_id, excluded.last_msg_id),
            last_sync_timestamp = excluded.last_sync_timestamp
    """,
        (chat_id, message_id, now),
    )
    if target_id is not None:
        conn.execute(
            """
            UPDATE sync_targets
            SET last_msg_id = MAX(last_msg_id, ?)
            WHERE user_id = ? AND chat_id = ?
        """,
            (message_id, target_id, chat_id),
        )
