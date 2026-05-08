import unittest
from types import SimpleNamespace

from tg_msg_manager.services.channel_export.discussions.models import (
    DISCUSSION_SOURCE_STATUS_FAILED,
    DISCUSSION_SOURCE_STATUS_NOT_LINKED,
    DISCUSSION_SOURCE_STATUS_RESOLVED,
)
from tg_msg_manager.services.channel_export.discussions.resolver import (
    ChannelDiscussionResolver,
)


class FakeDiscussionClient:
    def __init__(self, entity=None, error=None):
        self.entity = entity
        self.error = error
        self.get_entity_calls = []
        self.iter_messages_calls = []

    async def get_entity(self, entity_id):
        self.get_entity_calls.append(entity_id)
        if self.error is not None:
            raise self.error
        return self.entity

    async def iter_messages(self, *args, **kwargs):
        self.iter_messages_calls.append((args, kwargs))
        yield None


class TestChannelDiscussionResolver(unittest.IsolatedAsyncioTestCase):
    async def test_no_linked_discussion_returns_not_linked(self):
        client = FakeDiscussionClient(entity=SimpleNamespace(id=222))
        channel_entity = SimpleNamespace(id=111)

        result = await ChannelDiscussionResolver(client).resolve(channel_entity)

        self.assertEqual(result.status, DISCUSSION_SOURCE_STATUS_NOT_LINKED)
        self.assertIsNone(result.discussion_chat_id)
        self.assertEqual(client.get_entity_calls, [])
        self.assertEqual(client.iter_messages_calls, [])

    async def test_resolved_linked_discussion_returns_resolved(self):
        discussion_entity = SimpleNamespace(id=222, title="Comments")
        client = FakeDiscussionClient(entity=discussion_entity)
        channel_entity = SimpleNamespace(id=111, linked_chat_id=222)

        result = await ChannelDiscussionResolver(client).resolve(channel_entity)

        self.assertEqual(result.status, DISCUSSION_SOURCE_STATUS_RESOLVED)
        self.assertEqual(result.discussion_chat_id, 222)
        self.assertIs(result.discussion_entity, discussion_entity)
        self.assertEqual(client.get_entity_calls, [222])
        self.assertEqual(client.iter_messages_calls, [])

    async def test_linked_discussion_can_be_read_from_full_chat_attribute(self):
        discussion_entity = SimpleNamespace(id=333, title="Comments")
        client = FakeDiscussionClient(entity=discussion_entity)
        channel_entity = SimpleNamespace(
            id=111,
            full_chat=SimpleNamespace(linked_chat_id=333),
        )

        result = await ChannelDiscussionResolver(client).resolve(channel_entity)

        self.assertEqual(result.status, DISCUSSION_SOURCE_STATUS_RESOLVED)
        self.assertEqual(result.discussion_chat_id, 333)

    async def test_unexpected_client_error_returns_failed(self):
        client = FakeDiscussionClient(error=RuntimeError("boom"))
        channel_entity = SimpleNamespace(id=111, linked_chat_id=222)

        result = await ChannelDiscussionResolver(client).resolve(channel_entity)

        self.assertEqual(result.status, DISCUSSION_SOURCE_STATUS_FAILED)
        self.assertEqual(result.discussion_chat_id, 222)
        self.assertEqual(result.error, "boom")
        self.assertEqual(client.iter_messages_calls, [])


if __name__ == "__main__":
    unittest.main()
