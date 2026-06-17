import asyncio
import json
import logging
import time
from typing import List, Optional

from ...core.models.message import MessageData, SCHEMA_VERSION
from ...core.telemetry import telemetry
from .write import (
    checkpoint_writer,
    context_writer,
    message_writer,
    target_link_writer,
    user_writer,
)

logger = logging.getLogger(__name__)


class SQLiteWritePathMixin:
    """
    DEPRECATED compatibility aggregator for the split SQLite write-side modules.
    """

    async def _enqueue_write_item(
        self, item: tuple[MessageData, Optional[int]]
    ) -> None:
        queue_was_full = self._write_queue.full()
        started_at = time.perf_counter() if queue_was_full else None
        await self._write_queue.put(item)
        if started_at is not None:
            telemetry.track_counter("storage.queue_backpressure.wait_events", 1)
            telemetry.track_duration(
                "storage.queue_backpressure.wait_seconds",
                time.perf_counter() - started_at,
            )

    async def save_message(
        self, msg: MessageData, target_id: Optional[int] = None, flush: bool = True
    ) -> bool:
        """Queues a single message for background saving."""
        await self._ensure_worker_started()
        await self._enqueue_write_item((msg, target_id))
        telemetry.track_counter("storage.queue_messages", 1)
        telemetry.track_counter("storage.queue_batches", 1)
        if flush:
            await self.flush()
        return True

    async def save_messages(
        self,
        msgs: List[MessageData],
        target_id: Optional[int] = None,
        flush: bool = True,
    ) -> int:
        """Queues a batch of messages for background saving."""
        if not msgs:
            return 0
        await self._ensure_worker_started()
        for msg in msgs:
            await self._enqueue_write_item((msg, target_id))
        telemetry.track_counter("storage.queue_messages", len(msgs))
        telemetry.track_counter("storage.queue_batches", 1)
        if flush:
            await self.flush()
        return len(msgs)

    def _save_message_sync(
        self, msg: MessageData, target_id: Optional[int] = None
    ) -> bool:
        try:
            with self._write_transaction() as conn:
                self._save_msg_internal(conn, msg, target_id)
            return True
        except Exception as e:
            logger.error(f"Error saving message {msg.message_id} in {msg.chat_id}: {e}")
            return False

    async def _background_writer(self):
        """Background loop that commits queued messages in large batches."""
        logger.debug("SQLite Background Writer started.")
        while not self._shutdown_event.is_set() or not self._write_queue.empty():
            items = []
            try:
                timeout = 0.5 if not self._shutdown_event.is_set() else 0.05
                try:
                    item = await asyncio.wait_for(
                        self._write_queue.get(), timeout=timeout
                    )
                    items.append(item)
                    while len(items) < 500 and not self._write_queue.empty():
                        items.append(self._write_queue.get_nowait())
                except (asyncio.TimeoutError, asyncio.QueueEmpty):
                    pass

                if items:
                    started_at = time.perf_counter()
                    try:
                        await asyncio.to_thread(self._save_batches_by_target, items)
                    except Exception as e:
                        self._background_writer_error = e
                        raise
                    else:
                        telemetry.track_duration(
                            "storage.background_commit.total",
                            time.perf_counter() - started_at,
                        )
                        telemetry.track_counter("storage.background_commit.batches", 1)
                        telemetry.track_counter(
                            "storage.background_commit.messages", len(items)
                        )
                        logger.debug(
                            f"Background Writer committed {len(items)} items."
                        )
                    finally:
                        for _ in range(len(items)):
                            self._write_queue.task_done()

                if self._shutdown_event.is_set() and self._write_queue.empty():
                    break

            except Exception as e:
                logger.error(f"Error in background writer commit: {e}")
                await asyncio.sleep(1)
        logger.debug("SQLite Background Writer stopped.")

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
                    data["raw_payload"], ensure_ascii=False, default=self._json_serial
                ),
                payload_hash,
                SCHEMA_VERSION,
            ),
        )

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
