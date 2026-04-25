import sys
import os
import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tg_msg_manager.core.models.message import MessageData
from tg_msg_manager.services.exporter import ExportService
from tg_msg_manager.services.context_engine import DeepModeEngine
from tg_msg_manager.services.private_archive import PrivateArchiveService

class AsyncIterator:
    def __init__(self, items):
        self.items = items
    def __aiter__(self):
        return self
    async def __anext__(self):
        if not self.items:
            raise StopAsyncIteration
        return self.items.pop(0)

class TestServices(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.mock_storage = MagicMock()
        self.mock_storage.save_message = AsyncMock()
        self.mock_storage.save_messages = AsyncMock()
        self.mock_storage.upsert_chat = MagicMock()
        self.mock_storage.upsert_user = MagicMock()
        self.mock_storage.register_target = MagicMock()
        self.mock_storage.update_last_sync_at = MagicMock()
        self.mock_storage.get_last_msg_id.return_value = 10
        self.mock_storage.get_message_count.return_value = 0
        self.mock_storage.get_sync_status.return_value = {
            "last_msg_id": 0,
            "tail_msg_id": 0,
            "is_complete": 0,
            "deep_mode": 0,
            "recursive_depth": 0,
        }
        self.mock_storage.has_target_link.return_value = False
        self.mock_storage.get_message.return_value = None
        self.mock_client.get_messages = AsyncMock(return_value=[])
        self.mock_client.get_entity = AsyncMock()
        self.mock_client.download_media = AsyncMock()

    def _message(
        self,
        message_id,
        *,
        chat_id=1,
        user_id=1,
        author_name="User",
        text="msg",
        timestamp=None,
        reply_to_id=None,
        raw_payload=None,
        is_service=False,
    ):
        return MessageData(
            message_id=message_id,
            chat_id=chat_id,
            user_id=user_id,
            author_name=author_name,
            timestamp=timestamp or datetime.now(),
            text=text,
            media_type=None,
            reply_to_id=reply_to_id,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload=raw_payload or {},
            is_service=is_service,
        )

    def _saved_message_ids(self):
        saved_batches = [call.args[0] for call in self.mock_storage.save_messages.await_args_list]
        return [msg.message_id for batch in saved_batches for msg in batch]

    async def test_exporter_sync(self):
        # Mock last_id in storage
        self.mock_storage.get_last_msg_id.return_value = 10
        
        # Create mock message stream
        msg1 = MessageData(message_id=15, chat_id=1, user_id=1, author_name="Exporter User",
                          timestamp=datetime.now(), 
                          text="New", media_type=None, reply_to_id=None, 
                          fwd_from_id=None, context_group_id=None, raw_payload={})
        
        self.mock_client.get_messages.return_value = [msg1]
        self.mock_client.iter_messages.return_value = AsyncIterator([msg1])
        
        service = ExportService(self.mock_client, self.mock_storage)
        count = await service.sync_chat(MagicMock(id=1), limit=10)
        
        self.assertGreaterEqual(count, 0)

    async def test_export_limit_uses_single_worker_range(self):
        msg1 = MessageData(message_id=15, chat_id=1, user_id=1, author_name="Exporter User",
                          timestamp=datetime.now(),
                          text="New", media_type=None, reply_to_id=None,
                          fwd_from_id=None, context_group_id=None, raw_payload={})

        self.mock_client.get_messages.return_value = [msg1]
        self.mock_client.iter_messages.return_value = AsyncIterator([msg1])

        service = ExportService(self.mock_client, self.mock_storage)
        await service.sync_chat(MagicMock(id=1), limit=1)

        self.assertEqual(self.mock_client.iter_messages.call_count, 1)
        self.assertEqual(self.mock_client.iter_messages.call_args.kwargs["limit"], 1)

    async def test_deep_mode_clustering(self):
        target = self._message(100, user_id=1, author_name="Deep User", text="Target")
        direct_reply = self._message(
            101,
            user_id=2,
            author_name="Reply User",
            text="Reply",
            reply_to_id=100,
            timestamp=target.timestamp + timedelta(seconds=30),
            raw_payload={"reply_to": {"reply_to_msg_id": 100}},
        )
        unrelated = self._message(
            99,
            user_id=3,
            author_name="Noise User",
            text="Noise",
            timestamp=target.timestamp - timedelta(seconds=30),
        )

        self.mock_client.iter_messages.side_effect = lambda *args, **kwargs: AsyncIterator([direct_reply, unrelated, target])
        engine = DeepModeEngine(self.mock_client, self.mock_storage)
        cluster_id = await engine.extract_context(MagicMock(id=1), target, window_size=1)

        self.assertTrue(cluster_id)
        self.mock_storage.save_messages.assert_awaited()
        saved_ids = self._saved_message_ids()
        self.assertIn(100, saved_ids)
        self.assertIn(101, saved_ids)
        self.assertNotIn(99, saved_ids)

    async def test_deep_mode_includes_parent_message(self):
        parent = self._message(50, user_id=2, author_name="Parent", text="Parent")
        target = self._message(
            100,
            user_id=1,
            author_name="Deep User",
            text="Target",
            reply_to_id=50,
            raw_payload={"reply_to": {"reply_to_msg_id": 50}},
        )

        self.mock_client.iter_messages.side_effect = lambda *args, **kwargs: AsyncIterator([target])
        self.mock_client.get_messages.return_value = [parent]

        engine = DeepModeEngine(self.mock_client, self.mock_storage)
        await engine.extract_batch_context(MagicMock(id=1), [target], target_id=1, recursive_depth=1)

        saved_ids = self._saved_message_ids()
        self.assertIn(50, saved_ids)

    async def test_deep_mode_same_topic_requires_topic_match(self):
        target = self._message(
            100,
            user_id=1,
            author_name="Deep User",
            text="Topic target",
            raw_payload={"reply_to": {"reply_to_top_id": 900}},
        )
        same_topic = self._message(
            104,
            user_id=2,
            author_name="Topic User",
            text="Same topic",
            raw_payload={"reply_to": {"reply_to_top_id": 900}},
            timestamp=target.timestamp + timedelta(seconds=20),
        )
        other_topic = self._message(
            105,
            user_id=3,
            author_name="Other Topic",
            text="Other topic",
            raw_payload={"reply_to": {"reply_to_top_id": 901}},
            timestamp=target.timestamp + timedelta(seconds=25),
        )

        self.mock_client.iter_messages.side_effect = lambda *args, **kwargs: AsyncIterator([other_topic, same_topic, target])

        engine = DeepModeEngine(self.mock_client, self.mock_storage)
        await engine.extract_batch_context(MagicMock(id=1), [target], target_id=1, recursive_depth=2)

        saved_ids = self._saved_message_ids()
        self.assertIn(104, saved_ids)
        self.assertNotIn(105, saved_ids)

    async def test_deep_mode_time_fallback_requires_missing_structural_metadata(self):
        base_time = datetime.now()
        target = self._message(100, user_id=1, author_name="Deep User", text="Target", timestamp=base_time)
        prev_msg = self._message(
            99,
            user_id=2,
            author_name="Before",
            text="Before",
            timestamp=base_time - timedelta(seconds=45),
        )
        next_msg = self._message(
            101,
            user_id=3,
            author_name="After",
            text="After",
            timestamp=base_time + timedelta(seconds=50),
        )

        self.mock_client.iter_messages.side_effect = lambda *args, **kwargs: AsyncIterator([next_msg, target, prev_msg])

        engine = DeepModeEngine(self.mock_client, self.mock_storage)
        await engine.extract_batch_context(MagicMock(id=1), [target], target_id=1, recursive_depth=3)

        saved_ids = self._saved_message_ids()
        self.assertIn(99, saved_ids)
        self.assertIn(101, saved_ids)

        self.mock_storage.save_messages.reset_mock()
        parent = self._message(50, user_id=9, author_name="Parent", text="Parent")
        structural_target = self._message(
            200,
            user_id=1,
            author_name="Deep User",
            text="Reply target",
            timestamp=base_time,
            reply_to_id=50,
            raw_payload={"reply_to": {"reply_to_msg_id": 50}},
        )
        noise = self._message(
            201,
            user_id=8,
            author_name="Noise",
            text="Noise",
            timestamp=base_time + timedelta(seconds=30),
        )
        self.mock_client.get_messages.return_value = [parent]
        self.mock_client.iter_messages.side_effect = lambda *args, **kwargs: AsyncIterator([noise, structural_target])

        engine = DeepModeEngine(self.mock_client, self.mock_storage)
        await engine.extract_batch_context(MagicMock(id=1), [structural_target], target_id=1, recursive_depth=3)

        saved_ids = self._saved_message_ids()
        self.assertIn(50, saved_ids)
        self.assertNotIn(201, saved_ids)

    async def test_deep_mode_skips_service_messages(self):
        base_time = datetime.now()
        target = self._message(100, user_id=1, author_name="Deep User", text="Target", timestamp=base_time)
        service = self._message(
            101,
            user_id=2,
            author_name="Service",
            text="joined",
            timestamp=base_time + timedelta(seconds=20),
            is_service=True,
        )

        self.mock_client.iter_messages.side_effect = lambda *args, **kwargs: AsyncIterator([service, target])

        engine = DeepModeEngine(self.mock_client, self.mock_storage)
        await engine.extract_batch_context(MagicMock(id=1), [target], target_id=1, recursive_depth=3)

        saved_ids = self._saved_message_ids()
        self.assertIn(100, saved_ids)
        self.assertNotIn(101, saved_ids)

    async def test_deep_mode_processed_ids_do_not_leak_between_chats(self):
        self.mock_client.iter_messages.side_effect = lambda *args, **kwargs: AsyncIterator([])

        engine = DeepModeEngine(self.mock_client, self.mock_storage)
        target_chat_1 = MessageData(
            message_id=100, chat_id=1, user_id=1, author_name="Chat One",
            timestamp=datetime.now(),
            text="Target 1", media_type=None, reply_to_id=None,
            fwd_from_id=None, context_group_id=None, raw_payload={}
        )
        target_chat_2 = MessageData(
            message_id=100, chat_id=2, user_id=1, author_name="Chat Two",
            timestamp=datetime.now(),
            text="Target 2", media_type=None, reply_to_id=None,
            fwd_from_id=None, context_group_id=None, raw_payload={}
        )

        await engine.extract_batch_context(MagicMock(id=1), [target_chat_1], target_id=1, recursive_depth=1)
        await engine.extract_batch_context(MagicMock(id=2), [target_chat_2], target_id=1, recursive_depth=1)

        self.assertEqual(self.mock_storage.save_messages.await_count, 2)

    async def test_private_archive_downloads_media(self):
        self.mock_client.iter_messages.return_value = AsyncIterator([
            MessageData(
                message_id=5,
                chat_id=1,
                user_id=9,
                author_name="PM User",
                timestamp=datetime.now(),
                text="photo",
                media_type="Photo",
                reply_to_id=None,
                fwd_from_id=None,
                context_group_id=None,
                raw_payload={},
                media_ref=MagicMock()
            )
        ])
        self.mock_client.download_media.return_value = "/tmp/test_media.jpg"
        self.mock_storage.get_last_msg_id.return_value = 0
        self.mock_storage.register_target = MagicMock()

        service = PrivateArchiveService(self.mock_client, self.mock_storage, base_dir="/tmp/tg_pm_test")
        result_dir = await service.archive_pm(MagicMock(id=1, first_name="PM", last_name="User", username="pmuser"))

        self.assertIn("/tmp/tg_pm_test", result_dir)
        self.mock_client.download_media.assert_awaited()
        self.mock_storage.save_message.assert_awaited()
        self.assertEqual(self.mock_storage.save_message.await_args.kwargs["target_id"], 1)
        self.mock_storage.update_last_sync_at.assert_called_once_with(1, 1)

if __name__ == "__main__":
    unittest.main()
