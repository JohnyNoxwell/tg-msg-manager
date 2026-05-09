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


class FakeRequestClient(FakeDiscussionClient):
    def __init__(self, *, full_result=None, request_error=None, entity=None):
        super().__init__(entity=entity)
        self.full_result = full_result
        self.request_error = request_error
        self.request_calls = []

    async def request(self, request):
        self.request_calls.append(request)
        if self.request_error is not None:
            raise self.request_error
        return self.full_result


class FakeCallableClient(FakeDiscussionClient):
    def __init__(self, *, full_result=None, entity=None):
        super().__init__(entity=entity)
        self.full_result = full_result
        self.call_requests = []

    async def __call__(self, request):
        self.call_requests.append(request)
        return self.full_result


def post_with_replies(channel_id):
    return SimpleNamespace(
        raw_payload={
            "replies": {
                "comments": True,
                "channel_id": channel_id,
                "replies": 3,
            }
        }
    )


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

    async def test_get_full_channel_uses_wrapper_request_method(self):
        discussion_entity = SimpleNamespace(id=444, title="Comments")
        full_result = SimpleNamespace(
            full_chat=SimpleNamespace(linked_chat_id=444),
            chats=[discussion_entity],
        )
        client = FakeRequestClient(full_result=full_result)

        result = await ChannelDiscussionResolver(client).resolve(
            SimpleNamespace(id=111)
        )

        self.assertEqual(result.status, DISCUSSION_SOURCE_STATUS_RESOLVED)
        self.assertEqual(result.discussion_chat_id, 444)
        self.assertIs(result.discussion_entity, discussion_entity)
        self.assertEqual(len(client.request_calls), 1)
        self.assertEqual(client.get_entity_calls, [])

    async def test_get_full_channel_keeps_callable_client_fallback(self):
        discussion_entity = SimpleNamespace(id=445, title="Comments")
        full_result = SimpleNamespace(
            full_chat=SimpleNamespace(linked_chat_id=445),
            chats=[discussion_entity],
        )
        client = FakeCallableClient(full_result=full_result)

        result = await ChannelDiscussionResolver(client).resolve(
            SimpleNamespace(id=111)
        )

        self.assertEqual(result.status, DISCUSSION_SOURCE_STATUS_RESOLVED)
        self.assertEqual(result.discussion_chat_id, 445)
        self.assertEqual(len(client.call_requests), 1)

    async def test_request_exception_returns_failed_source(self):
        client = FakeRequestClient(request_error=RuntimeError("full failed"))

        result = await ChannelDiscussionResolver(client).resolve(
            SimpleNamespace(id=111)
        )

        self.assertEqual(result.status, DISCUSSION_SOURCE_STATUS_FAILED)
        self.assertIsNone(result.discussion_chat_id)
        self.assertEqual(result.error, "full failed")

    async def test_post_replies_metadata_resolves_discussion_source(self):
        discussion_entity = SimpleNamespace(id=555, title="Comments")
        client = FakeDiscussionClient(entity=discussion_entity)

        result = await ChannelDiscussionResolver(client).resolve(
            SimpleNamespace(id=111),
            posts=[post_with_replies(555)],
        )

        self.assertEqual(result.status, DISCUSSION_SOURCE_STATUS_RESOLVED)
        self.assertEqual(result.discussion_chat_id, 555)
        self.assertIs(result.discussion_entity, discussion_entity)
        self.assertEqual(client.get_entity_calls, [555])

    async def test_missing_post_replies_metadata_remains_not_linked(self):
        client = FakeDiscussionClient(entity=SimpleNamespace(id=555))

        result = await ChannelDiscussionResolver(client).resolve(
            SimpleNamespace(id=111),
            posts=[SimpleNamespace(raw_payload={})],
        )

        self.assertEqual(result.status, DISCUSSION_SOURCE_STATUS_NOT_LINKED)
        self.assertIsNone(result.discussion_chat_id)
        self.assertEqual(client.get_entity_calls, [])

    async def test_invalid_post_replies_channel_id_is_ignored(self):
        client = FakeDiscussionClient(entity=SimpleNamespace(id=555))

        result = await ChannelDiscussionResolver(client).resolve(
            SimpleNamespace(id=111),
            posts=[post_with_replies("not-int")],
        )

        self.assertEqual(result.status, DISCUSSION_SOURCE_STATUS_NOT_LINKED)
        self.assertEqual(client.get_entity_calls, [])

    async def test_multiple_post_replies_channel_ids_use_deterministic_most_frequent(
        self,
    ):
        discussion_entity = SimpleNamespace(id=777, title="Comments")
        client = FakeDiscussionClient(entity=discussion_entity)

        result = await ChannelDiscussionResolver(client).resolve(
            SimpleNamespace(id=111),
            posts=[
                post_with_replies(888),
                post_with_replies(777),
                post_with_replies(777),
            ],
        )

        self.assertEqual(result.status, DISCUSSION_SOURCE_STATUS_RESOLVED)
        self.assertEqual(result.discussion_chat_id, 777)
        self.assertEqual(client.get_entity_calls, [777])

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
