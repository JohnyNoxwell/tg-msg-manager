import unittest
from datetime import datetime

from tg_msg_manager.core.models.message import MessageData
from tg_msg_manager.services.channel_export.post_fetcher import ChannelPostFetcher


class FakeFetcherClient:
    def __init__(self, messages):
        self.messages = list(messages)
        self.calls = []

    async def iter_messages(self, entity, limit=None):
        self.calls.append({"entity": entity, "limit": limit})
        yielded = 0
        for message in self.messages:
            yield message
            yielded += 1
            if limit is not None and yielded >= limit:
                break


def make_message(message_id, *, is_service=False):
    return MessageData(
        message_id=message_id,
        chat_id=1,
        user_id=10,
        author_name="Author",
        timestamp=datetime.fromtimestamp(1700000000),
        text=f"message {message_id}",
        media_type=None,
        reply_to_id=None,
        fwd_from_id=None,
        context_group_id=None,
        raw_payload={},
        is_service=is_service,
    )


class TestChannelPostFetcher(unittest.IsolatedAsyncioTestCase):
    async def test_iter_posts_passes_limit_to_client(self):
        client = FakeFetcherClient([make_message(1)])

        posts = [
            message
            async for message in ChannelPostFetcher(client).iter_posts(7, limit=5)
        ]

        self.assertEqual(len(posts), 1)
        self.assertEqual(client.calls[0]["limit"], 5)

    async def test_iter_posts_yields_messages_and_skips_service_messages(self):
        client = FakeFetcherClient(
            [make_message(1), make_message(2, is_service=True), make_message(3)]
        )

        posts = [
            message.message_id
            async for message in ChannelPostFetcher(client).iter_posts(7)
        ]

        self.assertEqual(posts, [1, 3])

    async def test_iter_posts_handles_empty_channel(self):
        client = FakeFetcherClient([])

        posts = [message async for message in ChannelPostFetcher(client).iter_posts(7)]

        self.assertEqual(posts, [])


if __name__ == "__main__":
    unittest.main()
