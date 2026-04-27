import sys
import os
import asyncio
import time
import unittest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from telethon.errors import FloodWaitError

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tg_msg_manager.core.telegram.throttler import RateThrottler
from tg_msg_manager.core.telegram.client import TelethonClientWrapper


class TestTelegramCore(unittest.IsolatedAsyncioTestCase):
    class AsyncIterator:
        def __init__(self, items):
            self.items = list(items)

        def __aiter__(self):
            return self

        async def __anext__(self):
            if not self.items:
                raise StopAsyncIteration
            return self.items.pop(0)

    def _telethon_message(self, *, message_id: int, sender_id: int, text: str = "ok"):
        return MagicMock(
            id=message_id,
            sender=None,
            sender_id=sender_id,
            date=datetime.now(),
            message=text,
            media=None,
            reply_to=None,
            fwd_from=None,
            to_dict=MagicMock(return_value={}),
        )

    async def test_throttler_limits(self):
        # Allow 10 requests per second (0.1 interval)
        throttler = RateThrottler(max_requests_per_second=10.0, burst=1)

        start_time = time.perf_counter()
        # Perform 5 requests
        for _ in range(5):
            await throttler.throttle()
        end_time = time.perf_counter()

        elapsed = end_time - start_time
        # 5 requests should take at least 0.4 seconds (0.1 delay between them)
        # Sequence: Request 1 (no wait), R2 (+0.1), R3 (+0.1), R4 (+0.1), R5 (+0.1)
        self.assertGreaterEqual(elapsed, 0.39)

    async def test_wrapper_delegation(self):
        # Mock Telethon client
        wrapper = TelethonClientWrapper("dummy", 1, "hash", max_rps=100)
        wrapper.client = AsyncMock()

        # Test get_me
        await wrapper.get_me()
        wrapper.client.get_me.assert_awaited_once()

        # Test delete_messages
        await wrapper.delete_messages("entity", [1, 2, 3])
        wrapper.client.delete_messages.assert_awaited_once_with("entity", [1, 2, 3])

    async def test_get_messages_retry_preserves_limit(self):
        wrapper = TelethonClientWrapper("dummy", 1, "hash", max_rps=100)
        wrapper.client = AsyncMock()
        wrapper.client.get_messages.side_effect = [
            FloodWaitError(request=None, capture=0),
            [
                MagicMock(
                    id=1,
                    sender=None,
                    sender_id=1,
                    date=datetime.now(),
                    message="ok",
                    media=None,
                    reply_to=None,
                    fwd_from=None,
                    to_dict=MagicMock(return_value={}),
                )
            ],
        ]

        original_sleep = asyncio.sleep
        try:
            asyncio.sleep = AsyncMock()
            result = await wrapper.get_messages("entity", limit=1)
        finally:
            asyncio.sleep = original_sleep

        self.assertEqual(len(result), 1)
        self.assertEqual(wrapper.client.get_messages.await_count, 2)
        self.assertEqual(
            wrapper.client.get_messages.await_args_list[0].kwargs["limit"], 1
        )
        self.assertEqual(
            wrapper.client.get_messages.await_args_list[1].kwargs["limit"], 1
        )

    async def test_iter_messages_falls_back_to_local_sender_filter_for_unresolved_numeric_user(
        self,
    ):
        wrapper = TelethonClientWrapper("dummy", 1, "hash", max_rps=100)
        wrapper.client = MagicMock()
        wrapper.client.get_input_entity = AsyncMock(
            side_effect=ValueError("not cached")
        )
        wrapper.client.iter_messages = MagicMock(
            return_value=self.AsyncIterator(
                [
                    self._telethon_message(message_id=3, sender_id=11, text="noise"),
                    self._telethon_message(message_id=2, sender_id=42, text="target"),
                    self._telethon_message(message_id=1, sender_id=12, text="noise"),
                ]
            )
        )

        messages = []
        async for item in wrapper.iter_messages("chat", from_user=42):
            messages.append(item)

        self.assertEqual([item.message_id for item in messages], [2])
        self.assertIsNone(wrapper.client.iter_messages.call_args.kwargs["from_user"])


if __name__ == "__main__":
    unittest.main()
