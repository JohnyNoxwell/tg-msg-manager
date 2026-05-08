import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

from tg_msg_manager.services.channel_export.discussions.fetcher import (
    ChannelDiscussionFetcher,
)


class FakeDiscussionClient:
    def __init__(self, comments=None, error=None):
        self.comments = list(comments or [])
        self.error = error
        self.calls = []

    async def iter_messages(self, entity, limit=None, reply_to=None):
        self.calls.append(
            {
                "entity": entity,
                "limit": limit,
                "reply_to": reply_to,
            }
        )
        if self.error is not None:
            raise self.error
        yielded = 0
        for comment in self.comments:
            if limit is not None and yielded >= limit:
                break
            yield comment
            yielded += 1


def make_comment(message_id: int, hour: int):
    return SimpleNamespace(
        id=message_id,
        date=datetime(2026, 5, 8, hour, 0, tzinfo=timezone.utc),
    )


class TestChannelDiscussionFetcher(unittest.IsolatedAsyncioTestCase):
    async def test_fetches_comments_for_one_post_in_chronological_order(self):
        comments = [make_comment(2, 12), make_comment(1, 11)]
        client = FakeDiscussionClient(comments=comments)
        post = SimpleNamespace(message_id=5001)
        discussion_entity = SimpleNamespace(id=222)

        result = await ChannelDiscussionFetcher(client).fetch_comments_for_post(
            discussion_entity=discussion_entity,
            channel_post_record=post,
            max_comments_per_post=100,
        )

        self.assertIsNone(result.error)
        self.assertEqual([comment.id for comment in result.comments], [1, 2])
        self.assertEqual(client.calls[0]["entity"], discussion_entity)
        self.assertEqual(client.calls[0]["reply_to"], 5001)

    async def test_respects_max_comments_per_post(self):
        client = FakeDiscussionClient(
            comments=[make_comment(3, 13), make_comment(2, 12), make_comment(1, 11)]
        )

        result = await ChannelDiscussionFetcher(client).fetch_comments_for_post(
            discussion_entity=SimpleNamespace(id=222),
            channel_post_record=SimpleNamespace(message_id=5001),
            max_comments_per_post=2,
        )

        self.assertEqual(len(result.comments), 2)
        self.assertTrue(result.has_more)
        self.assertEqual(client.calls[0]["limit"], 3)
        self.assertEqual(client.calls[0]["reply_to"], 5001)

    async def test_no_comments_returns_empty_result(self):
        result = await ChannelDiscussionFetcher(
            FakeDiscussionClient()
        ).fetch_comments_for_post(
            discussion_entity=SimpleNamespace(id=222),
            channel_post_record=SimpleNamespace(message_id=5001),
            max_comments_per_post=100,
        )

        self.assertEqual(result.comments, ())
        self.assertFalse(result.has_more)
        self.assertIsNone(result.error)

    async def test_per_thread_error_is_represented_in_result(self):
        result = await ChannelDiscussionFetcher(
            FakeDiscussionClient(error=RuntimeError("thread unavailable"))
        ).fetch_comments_for_post(
            discussion_entity=SimpleNamespace(id=222),
            channel_post_record=SimpleNamespace(message_id=5001),
            max_comments_per_post=100,
        )

        self.assertEqual(result.comments, ())
        self.assertEqual(result.error, "thread unavailable")


if __name__ == "__main__":
    unittest.main()
