import asyncio
import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from tg_msg_manager.core.models.message import MessageData
from tg_msg_manager.services.private_archive.archive_writer import PrivateArchiveWriter
from tg_msg_manager.services.private_archive.event_emitter import (
    PrivateArchiveEventEmitter,
)
from tg_msg_manager.services.private_archive.media_downloader import (
    PrivateArchiveMediaDownloader,
)
from tg_msg_manager.services.private_archive.media_policy import (
    PrivateArchiveMediaPolicy,
)
from tg_msg_manager.services.private_archive.planner import PrivateArchivePlanner
from tg_msg_manager.services.private_archive.source_resolver import (
    PrivateArchiveSourceResolver,
)
from tg_msg_manager.services.private_archive.service import PrivateArchiveService
from tg_msg_manager.services.private_archive.stream_processor import (
    PrivateArchiveStreamProcessor,
)


class TestPrivateArchiveComponents(unittest.IsolatedAsyncioTestCase):
    def test_source_resolver_and_planner_create_deterministic_context(self):
        entity = SimpleNamespace(
            id=42,
            first_name="PM",
            last_name="User",
            username="pmuser",
        )

        descriptor = PrivateArchiveSourceResolver().resolve(entity)
        context = PrivateArchivePlanner(base_dir="/tmp/archive").build_context(
            descriptor
        )

        self.assertEqual(descriptor.user_id, 42)
        self.assertTrue(context.user_dir.endswith("PM_User_42"))
        self.assertTrue(context.chat_log_path.endswith("chat_log.txt"))

    def test_media_policy_categorizes_known_media_types(self):
        policy = PrivateArchiveMediaPolicy()

        self.assertEqual(policy.media_category("Photo"), "photos")
        self.assertEqual(policy.media_category("Video"), "videos")
        self.assertEqual(policy.media_category("Voice"), "voices")
        self.assertEqual(policy.media_category("Document"), "documents")

    def test_archive_writer_formats_pm_log(self):
        message = MessageData(
            message_id=5,
            chat_id=1,
            user_id=9,
            author_name="PM User",
            timestamp=datetime.fromtimestamp(1700000000),
            text="hello",
            media_type="Photo",
            reply_to_id=None,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={},
        )

        rendered = PrivateArchiveWriter().format_pm_log(message)

        self.assertIn("<PM User>", rendered)
        self.assertIn("<Attached Photo>", rendered)
        self.assertIn("hello", rendered)

    async def test_stream_processor_handles_empty_stream(self):
        client = MagicMock()
        client.iter_messages.return_value = EmptyAsyncIterator()
        storage = MagicMock()
        storage.save_message = AsyncMock()
        writer = MagicMock()
        archive_writer = MagicMock()
        archive_writer.append_message = AsyncMock()
        processor = PrivateArchiveStreamProcessor(
            client=client,
            storage=storage,
            archive_writer=archive_writer,
            event_emitter=PrivateArchiveEventEmitter(),
            media_policy=PrivateArchiveMediaPolicy(),
            media_downloader=MagicMock(),
        )

        count, stats, archive_stats = await processor.process_stream(
            object(),
            user_id=1,
            last_id=0,
            media_dir="/tmp/media",
            writer=writer,
        )

        self.assertEqual(count, 0)
        self.assertEqual(stats.total, 0)
        self.assertEqual(archive_stats.downloaded, 0)
        storage.save_message.assert_not_awaited()
        archive_writer.append_message.assert_not_awaited()

    async def test_stream_processor_calls_writer_for_new_messages(self):
        message = MessageData(
            message_id=5,
            chat_id=1,
            user_id=9,
            author_name="PM User",
            timestamp=datetime.fromtimestamp(1700000000),
            text="hello",
            media_type=None,
            reply_to_id=None,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={},
        )
        client = MagicMock()
        client.iter_messages.return_value = AsyncIterator([message])
        storage = MagicMock()
        storage.save_message = AsyncMock()
        archive_writer = MagicMock()
        archive_writer.append_message = AsyncMock()
        processor = PrivateArchiveStreamProcessor(
            client=client,
            storage=storage,
            archive_writer=archive_writer,
            event_emitter=PrivateArchiveEventEmitter(),
            media_policy=PrivateArchiveMediaPolicy(),
            media_downloader=MagicMock(),
        )

        count, _, _ = await processor.process_stream(
            object(),
            user_id=1,
            last_id=0,
            media_dir="/tmp/media",
            writer=MagicMock(),
        )

        self.assertEqual(count, 1)
        storage.save_message.assert_awaited_once_with(message, target_id=1, flush=False)
        archive_writer.append_message.assert_awaited_once()

    async def test_private_archive_flushes_before_marking_synced(self):
        order = []
        storage = MagicMock()
        storage.flush = AsyncMock(side_effect=lambda: order.append("flush"))
        archive_writer = MagicMock()
        archive_writer.create_log_writer.return_value = MagicMock()
        state_manager = MagicMock()
        state_manager.get_last_msg_id.return_value = 0
        state_manager.mark_synced.side_effect = lambda user_id: order.append("mark")
        event_emitter = MagicMock()
        event_emitter.emit_completed.side_effect = lambda **kwargs: order.append(
            "completed"
        )
        stream_processor = MagicMock()
        stream_processor.process_stream = AsyncMock(
            side_effect=lambda *args, **kwargs: (
                order.append("stream"),
                (
                    0,
                    PrivateArchiveStreamProcessor.initial_media_stats(),
                    PrivateArchiveStreamProcessor.initial_archive_stats(),
                ),
            )[1]
        )
        service = PrivateArchiveService(
            MagicMock(),
            storage,
            archive_writer=archive_writer,
            state_manager=state_manager,
            event_emitter=event_emitter,
            stream_processor=stream_processor,
        )

        await service.archive_pm(SimpleNamespace(id=1, first_name="PM"))

        self.assertEqual(order, ["stream", "flush", "completed", "mark"])

    async def test_private_archive_does_not_mark_synced_when_stream_raises(self):
        storage = MagicMock()
        storage.flush = AsyncMock()
        archive_writer = MagicMock()
        archive_writer.create_log_writer.return_value = MagicMock()
        state_manager = MagicMock()
        state_manager.get_last_msg_id.return_value = 0
        event_emitter = MagicMock()
        stream_processor = MagicMock()
        stream_processor.process_stream = AsyncMock(side_effect=RuntimeError("boom"))
        service = PrivateArchiveService(
            MagicMock(),
            storage,
            archive_writer=archive_writer,
            state_manager=state_manager,
            event_emitter=event_emitter,
            stream_processor=stream_processor,
        )

        with self.assertRaises(RuntimeError):
            await service.archive_pm(SimpleNamespace(id=1, first_name="PM"))

        storage.flush.assert_not_awaited()
        event_emitter.emit_completed.assert_not_called()
        state_manager.mark_synced.assert_not_called()

    async def test_media_downloader_returns_none_when_policy_skips(self):
        policy = PrivateArchiveMediaPolicy()
        client = MagicMock()
        client.download_media = AsyncMock()
        downloader = PrivateArchiveMediaDownloader(
            client,
            media_policy=policy,
            download_semaphore=asyncio.Semaphore(1),
        )
        message = MessageData(
            message_id=1,
            chat_id=1,
            user_id=1,
            author_name="User",
            timestamp=datetime.fromtimestamp(1700000000),
            text="hello",
            media_type=None,
            reply_to_id=None,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={},
        )

        result = await downloader.download(message, media_dir="/tmp/media")

        self.assertIsNone(result)
        client.download_media.assert_not_awaited()

    async def test_stream_processor_marks_media_failure_as_skipped(self):
        message = MessageData(
            message_id=5,
            chat_id=1,
            user_id=9,
            author_name="PM User",
            timestamp=datetime.fromtimestamp(1700000000),
            text="photo",
            media_type="Photo",
            reply_to_id=None,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={},
            media_ref=object(),
        )
        storage = MagicMock()
        storage.save_message = AsyncMock()
        archive_writer = MagicMock()
        archive_writer.append_message = AsyncMock()
        downloader = MagicMock()
        downloader.download = AsyncMock(return_value=None)
        processor = PrivateArchiveStreamProcessor(
            client=MagicMock(),
            storage=storage,
            archive_writer=archive_writer,
            event_emitter=PrivateArchiveEventEmitter(),
            media_policy=PrivateArchiveMediaPolicy(),
            media_downloader=downloader,
        )

        stats = processor.initial_media_stats()
        archive_stats = processor.initial_archive_stats()
        await processor.process_message(
            message,
            user_id=1,
            media_dir="/tmp/media",
            writer=MagicMock(),
            stats=stats,
            archive_stats=archive_stats,
        )

        self.assertEqual(stats.photo, 1)
        self.assertEqual(archive_stats.skipped, 1)


class AsyncIterator:
    def __init__(self, items):
        self._items = iter(items)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self._items)
        except StopIteration as exc:
            raise StopAsyncIteration from exc


class EmptyAsyncIterator(AsyncIterator):
    def __init__(self):
        super().__init__([])


if __name__ == "__main__":
    unittest.main()
