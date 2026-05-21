import unittest
from types import SimpleNamespace

from tg_msg_manager.services.channel_export.source_resolver import (
    ChannelResolveError,
    ChannelSourceResolver,
    InvalidChannelError,
)


class FakeResolverClient:
    def __init__(self, entity=None, error=None, entities=None):
        self.entity = entity
        self.error = error
        self.entities = entities or {}
        self.calls = []

    async def get_entity(self, channel):
        self.calls.append(channel)
        if channel in self.entities:
            value = self.entities[channel]
            if isinstance(value, Exception):
                raise value
            return value
        if self.error is not None:
            raise self.error
        return self.entity


class TestChannelSourceResolver(unittest.IsolatedAsyncioTestCase):
    async def test_resolve_username_returns_entity_and_identity(self):
        entity = SimpleNamespace(
            id=123,
            title="News",
            username="news",
            access_hash=777,
            broadcast=True,
            is_channel=True,
        )

        resolved_entity, identity = await ChannelSourceResolver(
            FakeResolverClient(entity=entity)
        ).resolve("@news")

        self.assertIs(resolved_entity, entity)
        self.assertEqual(identity.channel_id, 123)
        self.assertEqual(identity.title, "News")
        self.assertEqual(identity.username, "news")
        self.assertEqual(identity.access_hash, 777)

    async def test_resolve_handles_missing_username_and_title(self):
        entity = SimpleNamespace(
            id=456,
            title=None,
            username=None,
            broadcast=True,
            is_channel=True,
        )

        _, identity = await ChannelSourceResolver(
            FakeResolverClient(entity=entity)
        ).resolve("456")

        self.assertIsNone(identity.title)
        self.assertIsNone(identity.username)

    async def test_resolve_rejects_invalid_entity_without_id(self):
        with self.assertRaises(InvalidChannelError):
            await ChannelSourceResolver(
                FakeResolverClient(entity=SimpleNamespace(title="broken"))
            ).resolve("@broken")

    async def test_resolve_rejects_non_channel_entity(self):
        entity = SimpleNamespace(id=5, entity_type="user", is_user=True)

        with self.assertRaises(InvalidChannelError) as raised:
            await ChannelSourceResolver(FakeResolverClient(entity=entity)).resolve(
                "@user"
            )

        self.assertIn("is a user", str(raised.exception))

    async def test_resolve_rejects_group_with_specific_message(self):
        entity = SimpleNamespace(id=5, entity_type="group", megagroup=True)

        with self.assertRaises(InvalidChannelError) as raised:
            await ChannelSourceResolver(FakeResolverClient(entity=entity)).resolve(
                "-1001274306614"
            )

        self.assertIn("group/supergroup", str(raised.exception))
        self.assertIn("broadcast channels only", str(raised.exception))

    async def test_resolve_wraps_get_entity_failure(self):
        with self.assertRaises(ChannelResolveError):
            await ChannelSourceResolver(
                FakeResolverClient(error=ValueError("boom"))
            ).resolve("@missing")

    async def test_resolve_numeric_channel_id_tries_peer_variants(self):
        entity = SimpleNamespace(
            id=1274306614,
            title="Numeric Channel",
            username=None,
            access_hash=999,
            broadcast=True,
            is_channel=True,
        )
        client = FakeResolverClient(
            entities={
                -1001274306614: ValueError("full peer id not cached"),
                1274306614: entity,
            }
        )

        resolved_entity, identity = await ChannelSourceResolver(client).resolve(
            "-1001274306614"
        )

        self.assertIs(resolved_entity, entity)
        self.assertEqual(identity.channel_id, 1274306614)
        self.assertEqual(client.calls, [-1001274306614, 1274306614])


if __name__ == "__main__":
    unittest.main()
