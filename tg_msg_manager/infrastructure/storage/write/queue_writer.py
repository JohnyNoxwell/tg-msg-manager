import asyncio
import logging
import time
from typing import Optional

from ....core.models.message import MessageData
from ....core.telemetry import telemetry

logger = logging.getLogger(__name__)


async def enqueue_write_item(storage, item: tuple[MessageData, Optional[int]]) -> None:
    queue_was_full = storage._write_queue.full()
    started_at = time.perf_counter() if queue_was_full else None
    await storage._write_queue.put(item)
    if started_at is not None:
        telemetry.track_counter("storage.queue_backpressure.wait_events", 1)
        telemetry.track_duration(
            "storage.queue_backpressure.wait_seconds",
            time.perf_counter() - started_at,
        )


async def save_message(
    storage, msg: MessageData, target_id: Optional[int] = None, flush: bool = True
) -> bool:
    await storage._ensure_worker_started()
    await storage._enqueue_write_item((msg, target_id))
    telemetry.track_counter("storage.queue_messages", 1)
    telemetry.track_counter("storage.queue_batches", 1)
    if flush:
        await storage.flush()
    return True


async def save_messages(
    storage,
    msgs: list[MessageData],
    target_id: Optional[int] = None,
    flush: bool = True,
) -> int:
    if not msgs:
        return 0
    await storage._ensure_worker_started()
    for msg in msgs:
        await storage._enqueue_write_item((msg, target_id))
    telemetry.track_counter("storage.queue_messages", len(msgs))
    telemetry.track_counter("storage.queue_batches", 1)
    if flush:
        await storage.flush()
    return len(msgs)


def save_message_sync(
    storage, msg: MessageData, target_id: Optional[int] = None
) -> bool:
    try:
        with storage._write_transaction() as conn:
            storage._save_msg_internal(conn, msg, target_id)
        return True
    except Exception as exc:
        logger.error(
            "Error saving message %s in %s: %s",
            msg.message_id,
            msg.chat_id,
            exc,
        )
        return False


async def background_writer(storage):
    logger.debug("SQLite Background Writer started.")
    while not storage._shutdown_event.is_set() or not storage._write_queue.empty():
        items = []
        try:
            timeout = 0.5 if not storage._shutdown_event.is_set() else 0.05
            try:
                item = await asyncio.wait_for(
                    storage._write_queue.get(), timeout=timeout
                )
                items.append(item)
                while len(items) < 500 and not storage._write_queue.empty():
                    items.append(storage._write_queue.get_nowait())
            except (asyncio.TimeoutError, asyncio.QueueEmpty):
                pass

            if items:
                started_at = time.perf_counter()
                try:
                    await asyncio.to_thread(storage._save_batches_by_target, items)
                except Exception as exc:
                    storage._background_writer_error = exc
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
                    logger.debug("Background Writer committed %s items.", len(items))
                finally:
                    for _ in range(len(items)):
                        storage._write_queue.task_done()

            if storage._shutdown_event.is_set() and storage._write_queue.empty():
                break

        except Exception as exc:
            logger.error("Error in background writer commit: %s", exc)
            await asyncio.sleep(1)
    logger.debug("SQLite Background Writer stopped.")
