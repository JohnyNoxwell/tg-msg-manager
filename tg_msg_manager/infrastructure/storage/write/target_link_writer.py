import time
from typing import Optional

from ..link_types import (
    TARGET_LINK_LEGACY,
    TARGET_LINK_REPLY_CONTEXT,
    TARGET_LINK_TARGET_AUTHOR,
)


def ensure_target_link_in_conn(
    storage,
    conn,
    chat_id: int,
    message_id: int,
    target_id: int,
    *,
    source_user_id: Optional[int] = None,
    reply_to_id: Optional[int] = None,
):
    del storage
    link_type = TARGET_LINK_LEGACY
    if source_user_id is not None and source_user_id == target_id:
        link_type = TARGET_LINK_TARGET_AUTHOR
    elif reply_to_id is not None:
        link_type = TARGET_LINK_REPLY_CONTEXT
    conn.execute(
        """
        INSERT INTO message_target_links (
            chat_id,
            message_id,
            target_user_id,
            link_type,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(chat_id, message_id, target_user_id) DO UPDATE SET
            link_type = CASE
                WHEN message_target_links.link_type = 'legacy' AND excluded.link_type != 'legacy'
                    THEN excluded.link_type
                WHEN message_target_links.link_type = 'reply_context' AND excluded.link_type = 'target_author'
                    THEN excluded.link_type
                ELSE message_target_links.link_type
            END
    """,
        (chat_id, message_id, target_id, link_type, int(time.time())),
    )
