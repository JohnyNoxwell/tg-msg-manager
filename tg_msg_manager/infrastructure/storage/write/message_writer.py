import json
import logging
from datetime import datetime
from typing import Optional

from ....core.models.message import MessageData, SCHEMA_VERSION
from .checkpoint_writer import update_sync_state_for_message_in_conn
from .context_writer import (
    refresh_missing_reply_state_in_conn,
    resolve_missing_reply_refs_for_parent_in_conn,
    upsert_context_link_in_conn,
)
from .target_link_writer import ensure_target_link_in_conn
from .user_writer import upsert_chat_in_conn, upsert_user_from_payload_in_conn

logger = logging.getLogger(__name__)


def normalize_raw_payload(storage, raw):
    del storage
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except Exception:
            return {}
    return raw


def json_serial(storage, obj):
    del storage
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, bytes):
        return obj.hex()
    return f"<<Unserializable: {type(obj)}>>"


def save_batches_by_target(
    storage, items: list[tuple[MessageData, Optional[int]]]
) -> int:
    try:
        saved_count = 0
        with storage._write_transaction() as conn:
            for msg, target_id in items:
                save_msg_internal(storage, conn, msg, target_id)
                saved_count += 1
        return saved_count
    except Exception as exc:
        logger.error("Error saving batch of messages with attribution: %s", exc)
        return 0


def save_msg_internal(
    storage,
    conn,
    msg: MessageData,
    target_id: Optional[int] = None,
):
    payload_hash = msg.get_payload_hash()
    existing_hash_row = conn.execute(
        "SELECT payload_hash FROM messages WHERE chat_id = ? AND message_id = ?",
        (msg.chat_id, msg.message_id),
    ).fetchone()
    if target_id is not None:
        ensure_target_link_in_conn(
            storage,
            conn,
            msg.chat_id,
            msg.message_id,
            target_id,
            source_user_id=msg.user_id,
            reply_to_id=msg.reply_to_id,
        )
    if existing_hash_row and existing_hash_row["payload_hash"] == payload_hash:
        return

    data = msg.to_dict()
    raw = normalize_raw_payload(storage, data.get("raw_payload", {}))
    if data["user_id"]:
        upsert_user_from_payload_in_conn(
            storage,
            conn,
            data["user_id"],
            raw,
            author_name=data.get("author_name"),
            observed_at=data.get("timestamp"),
            chat_id=data.get("chat_id"),
            source_message_id=data.get("message_id"),
        )
        storage._refresh_target_author_name_in_conn(
            conn, data["user_id"], data.get("author_name")
        )

    upsert_chat_in_conn(
        storage,
        conn,
        data["chat_id"],
        raw.get("chat_title") or raw.get("title") or "",
        raw.get("chat_type") or raw.get("_") or "Channel/Group",
    )
    upsert_context_link_in_conn(
        storage,
        conn,
        data["chat_id"],
        data["message_id"],
        data.get("reply_to_id"),
    )
    conn.execute(
        """
        INSERT OR REPLACE INTO messages (
            chat_id, message_id, user_id, author_name, timestamp, text,
            media_type, reply_to_id, fwd_from_id,
            context_group_id, raw_payload, payload_hash, schema_version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            data["chat_id"],
            data["message_id"],
            data["user_id"],
            data["author_name"],
            data["timestamp"],
            data["text"],
            data["media_type"],
            data["reply_to_id"],
            data["fwd_from_id"],
            data["context_group_id"],
            json.dumps(
                data["raw_payload"],
                ensure_ascii=False,
                default=lambda obj: json_serial(storage, obj),
            ),
            payload_hash,
            SCHEMA_VERSION,
        ),
    )
    refresh_missing_reply_state_in_conn(
        storage,
        conn,
        data["chat_id"],
        data["message_id"],
        data.get("reply_to_id"),
    )
    resolve_missing_reply_refs_for_parent_in_conn(
        storage,
        conn,
        data["chat_id"],
        data["message_id"],
    )
    update_sync_state_for_message_in_conn(
        storage,
        conn,
        data["chat_id"],
        data["message_id"],
        target_id,
    )


def delete_messages(storage, chat_id: int, message_ids: list[int]) -> int:
    if not message_ids:
        return 0
    placeholders = ", ".join(["?"] * len(message_ids))
    with storage._write_transaction() as conn:
        conn.execute(
            f"DELETE FROM message_target_links WHERE chat_id = ? AND message_id IN ({placeholders})",
            (chat_id, *message_ids),
        )
        res = conn.execute(
            f"DELETE FROM messages WHERE chat_id = ? AND message_id IN ({placeholders})",
            (chat_id, *message_ids),
        )
        return res.rowcount


def delete_user_data(storage, user_id: int):
    from ..records import DeleteUserDataResult

    with storage._write_transaction() as conn:
        conn.execute(
            "DELETE FROM message_target_links WHERE target_user_id = ?", (user_id,)
        )
        res = conn.execute(
            """
            DELETE FROM messages
            WHERE NOT EXISTS (
                SELECT 1 FROM message_target_links
                WHERE message_target_links.chat_id = messages.chat_id
                AND message_target_links.message_id = messages.message_id
            )
        """
        )
        deleted_msgs = res.rowcount
        target_res = conn.execute(
            "DELETE FROM sync_targets WHERE user_id = ?",
            (user_id,),
        )
        return DeleteUserDataResult(
            deleted_messages=deleted_msgs,
            deleted_targets=target_res.rowcount,
        )
