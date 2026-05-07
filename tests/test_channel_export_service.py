import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from tg_msg_manager.core.models.message import MessageData
from tg_msg_manager.services.channel_export import (
    ChannelExportOptions,
    ChannelExportService,
)


class FakeChannelEntity:
    def __init__(self, entity_id=123, title="Daily", username="daily"):
        self.id = entity_id
        self.title = title
        self.username = username
        self.broadcast = True
        self.is_channel = True


class FakeChannelClient:
    def __init__(self, entity, messages):
        self.entity = entity
        self.messages = list(messages)
        self.calls = []
        self.download_media_calls = 0

    async def get_entity(self, channel):
        self.calls.append(("get_entity", channel))
        return self.entity

    async def iter_messages(self, entity, limit=None):
        self.calls.append(("iter_messages", getattr(entity, "id", entity), limit))
        yielded = 0
        for message in self.messages:
            yield message
            yielded += 1
            if limit is not None and yielded >= limit:
                break

    async def download_media(self, media, file=None):
        self.download_media_calls += 1
        return None


def make_message(
    message_id, *, text, media_type=None, media_ref=None, is_service=False
):
    return MessageData(
        message_id=message_id,
        chat_id=123,
        user_id=1,
        author_name="Poster",
        timestamp=datetime(2026, 5, 7, 10 + message_id, 0, tzinfo=timezone.utc),
        text=text,
        media_type=media_type,
        reply_to_id=None,
        fwd_from_id=None,
        context_group_id=None,
        raw_payload={},
        is_service=is_service,
        media_ref=media_ref,
    )


class TestChannelExportService(unittest.IsolatedAsyncioTestCase):
    async def test_export_channel_writes_dataset_files_for_two_posts(self):
        entity = FakeChannelEntity()
        client = FakeChannelClient(
            entity,
            [
                make_message(
                    1,
                    text="First",
                    media_type="Photo",
                    media_ref={"mime_type": "image/jpeg", "file_name": "a.jpg"},
                ),
                make_message(2, text="Second"),
            ],
        )

        with tempfile.TemporaryDirectory(prefix="tg_channel_service_") as tmpdir:
            service = ChannelExportService(client=client, base_dir=Path(tmpdir))
            result = await service.export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=10,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                )
            )

            self.assertEqual(result.message_count, 2)
            self.assertEqual(result.media_count, 1)
            self.assertTrue(result.manifest_path.exists())
            self.assertTrue(result.messages_jsonl_path.exists())
            self.assertTrue(result.messages_txt_path.exists())
            self.assertTrue(result.media_manifest_path.exists())
            manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["export"]["message_count"], 2)
            self.assertEqual(manifest["export"]["media_count"], 1)
            self.assertEqual(manifest["source"]["username"], "daily")

    async def test_export_channel_handles_empty_channel(self):
        entity = FakeChannelEntity(entity_id=456, title="Empty", username="empty")
        client = FakeChannelClient(entity, [])

        with tempfile.TemporaryDirectory(prefix="tg_channel_service_empty_") as tmpdir:
            service = ChannelExportService(client=client, base_dir=Path(tmpdir))
            result = await service.export_channel(
                ChannelExportOptions(
                    channel="@empty",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                )
            )

            self.assertEqual(result.message_count, 0)
            self.assertEqual(result.media_count, 0)
            self.assertEqual(result.messages_jsonl_path.read_text(encoding="utf-8"), "")
            self.assertEqual(result.media_manifest_path.read_text(encoding="utf-8"), "")

    async def test_export_channel_does_not_download_media_in_metadata_mode(self):
        entity = FakeChannelEntity()
        client = FakeChannelClient(
            entity,
            [
                make_message(
                    1,
                    text="Photo",
                    media_type="Photo",
                    media_ref={"mime_type": "image/jpeg", "file_name": "a.jpg"},
                )
            ],
        )

        with tempfile.TemporaryDirectory(prefix="tg_channel_service_media_") as tmpdir:
            service = ChannelExportService(client=client, base_dir=Path(tmpdir))
            await service.export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                )
            )

            self.assertEqual(client.download_media_calls, 0)

    async def test_export_channel_emits_completion_event(self):
        entity = FakeChannelEntity()
        client = FakeChannelClient(entity, [make_message(1, text="Done")])
        events = []

        with tempfile.TemporaryDirectory(prefix="tg_channel_service_events_") as tmpdir:
            service = ChannelExportService(
                client=client,
                base_dir=Path(tmpdir),
                event_sink=events.append,
            )
            await service.export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                )
            )

            self.assertEqual(events[-1].name, "channel_export.completed")
            self.assertEqual(events[-1].payload["message_count"], 1)


if __name__ == "__main__":
    unittest.main()
