from typing import List, Optional

from ...core.models.message import MessageData
from .write import (
    checkpoint_writer,
    context_writer,
    message_writer,
    queue_writer,
    target_link_writer,
    user_writer,
)


class SQLiteWritePathMixin:
    """
    DEPRECATED compatibility aggregator for the split SQLite write-side modules.
    """

    async def _enqueue_write_item(
        self, item: tuple[MessageData, Optional[int]]
    ) -> None:
        return await queue_writer.enqueue_write_item(self, item)

    async def save_message(
        self, msg: MessageData, target_id: Optional[int] = None, flush: bool = True
    ) -> bool:
        """Queues a single message for background saving."""
        return await queue_writer.save_message(self, msg, target_id, flush)

    async def save_messages(
        self,
        msgs: List[MessageData],
        target_id: Optional[int] = None,
        flush: bool = True,
    ) -> int:
        """Queues a batch of messages for background saving."""
        return await queue_writer.save_messages(self, msgs, target_id, flush)

    def _save_message_sync(
        self, msg: MessageData, target_id: Optional[int] = None
    ) -> bool:
        return queue_writer.save_message_sync(self, msg, target_id)

    async def _background_writer(self):
        """Background loop that commits queued messages in large batches."""
        return await queue_writer.background_writer(self)

    def _save_batches_by_target(
        self, items: List[tuple[MessageData, Optional[int]]]
    ) -> int:
        return message_writer.save_batches_by_target(self, items)

    def _save_msg_internal(
        self, conn, msg: MessageData, target_id: Optional[int] = None
    ):
        return message_writer.save_msg_internal(self, conn, msg, target_id)

    def _normalize_raw_payload(self, raw):
        return message_writer.normalize_raw_payload(self, raw)

    def _json_serial(self, obj):
        return message_writer.json_serial(self, obj)

    def _ensure_target_link_in_conn(
        self,
        conn,
        chat_id: int,
        message_id: int,
        target_id: int,
        *,
        source_user_id: Optional[int] = None,
        reply_to_id: Optional[int] = None,
    ):
        return target_link_writer.ensure_target_link_in_conn(
            self,
            conn,
            chat_id,
            message_id,
            target_id,
            source_user_id=source_user_id,
            reply_to_id=reply_to_id,
        )

    def _upsert_user_from_payload_in_conn(
        self,
        conn,
        user_id: int,
        raw: dict,
        *,
        author_name: Optional[str] = None,
        observed_at: Optional[int] = None,
        chat_id: Optional[int] = None,
        source_message_id: Optional[int] = None,
    ):
        return user_writer.upsert_user_from_payload_in_conn(
            self,
            conn,
            user_id,
            raw,
            author_name=author_name,
            observed_at=observed_at,
            chat_id=chat_id,
            source_message_id=source_message_id,
        )

    def _upsert_chat_from_payload_in_conn(self, conn, chat_id: int, raw: dict):
        return user_writer.upsert_chat_in_conn(
            self,
            conn,
            chat_id,
            raw.get("chat_title") or raw.get("title") or "",
            raw.get("chat_type") or raw.get("_") or "Channel/Group",
        )

    def _upsert_context_link_in_conn(
        self,
        conn,
        chat_id: int,
        message_id: int,
        reply_to_id: Optional[int],
    ):
        return context_writer.upsert_context_link_in_conn(
            self, conn, chat_id, message_id, reply_to_id
        )

    def _upsert_message_row_in_conn(self, conn, data: dict, payload_hash: str):
        return message_writer.upsert_message_row_in_conn(self, conn, data, payload_hash)

    def _refresh_missing_reply_state_in_conn(
        self,
        conn,
        chat_id: int,
        message_id: int,
        reply_to_id: Optional[int],
    ) -> None:
        return context_writer.refresh_missing_reply_state_in_conn(
            self,
            conn,
            chat_id,
            message_id,
            reply_to_id,
        )

    def _resolve_missing_reply_refs_for_parent_in_conn(
        self,
        conn,
        chat_id: int,
        message_id: int,
    ) -> None:
        return context_writer.resolve_missing_reply_refs_for_parent_in_conn(
            self, conn, chat_id, message_id
        )

    def _update_sync_state_for_message_in_conn(
        self, conn, chat_id: int, message_id: int, target_id: Optional[int]
    ):
        return checkpoint_writer.update_sync_state_for_message_in_conn(
            self, conn, chat_id, message_id, target_id
        )
