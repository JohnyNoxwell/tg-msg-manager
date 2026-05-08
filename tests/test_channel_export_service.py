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

    async def iter_messages(self, entity, limit=None, min_id=None):
        self.calls.append(
            ("iter_messages", getattr(entity, "id", entity), limit, min_id)
        )
        yielded = 0
        for message in self.messages:
            if min_id is not None and message.message_id <= min_id:
                continue
            yield message
            yielded += 1
            if limit is not None and yielded >= limit:
                break

    async def download_media(self, media, file=None):
        self.download_media_calls += 1
        return None


class FailingManifestWriter:
    def write(self, path, manifest):
        del path, manifest
        raise RuntimeError("manifest write failed")


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
    async def test_export_channel_writes_dataset_files_and_state(self):
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

            self.assertEqual(result.run_mode, "full")
            self.assertEqual(result.message_count, 2)
            self.assertEqual(result.media_count, 1)
            self.assertEqual(result.posts_exported_this_run, 2)
            self.assertTrue(result.manifest_path.exists())
            self.assertTrue(result.state_path.exists())
            manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
            state = json.loads(result.state_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["export"]["message_count"], 2)
            self.assertEqual(manifest["export"]["media_count"], 1)
            self.assertEqual(manifest["source"]["username"], "daily")
            self.assertEqual(state["last_exported_message_id"], 2)

    async def test_second_incremental_export_appends_only_new_posts(self):
        entity = FakeChannelEntity()
        first_client = FakeChannelClient(
            entity,
            [make_message(1, text="First"), make_message(2, text="Second")],
        )
        second_client = FakeChannelClient(
            entity,
            [
                make_message(1, text="First"),
                make_message(2, text="Second"),
                make_message(3, text="Third"),
                make_message(4, text="Fourth"),
            ],
        )

        with tempfile.TemporaryDirectory(
            prefix="tg_channel_service_incremental_"
        ) as tmpdir:
            first_service = ChannelExportService(
                client=first_client,
                base_dir=Path(tmpdir),
            )
            await first_service.export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                )
            )

            second_service = ChannelExportService(
                client=second_client,
                base_dir=Path(tmpdir),
            )
            result = await second_service.export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                )
            )

            jsonl_lines = result.messages_jsonl_path.read_text(
                encoding="utf-8"
            ).splitlines()
            exported_ids = [json.loads(line)["message_id"] for line in jsonl_lines]
            state = json.loads(result.state_path.read_text(encoding="utf-8"))
            self.assertEqual(result.run_mode, "incremental")
            self.assertEqual(result.posts_exported_this_run, 2)
            self.assertEqual(result.message_count, 4)
            self.assertEqual(exported_ids, [1, 2, 3, 4])
            self.assertEqual(state["message_count_total"], 4)
            self.assertEqual(state["last_exported_message_id"], 4)
            self.assertEqual(second_client.calls[-1][-1], 2)

    async def test_no_new_posts_emits_event_and_keeps_state_unchanged(self):
        entity = FakeChannelEntity()
        client = FakeChannelClient(entity, [make_message(1, text="Only")])

        with tempfile.TemporaryDirectory(prefix="tg_channel_service_no_new_") as tmpdir:
            service = ChannelExportService(client=client, base_dir=Path(tmpdir))
            await service.export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                )
            )
            state_path = Path(tmpdir) / "@daily__123" / "channel_export_state.json"
            initial_state = state_path.read_text(encoding="utf-8")
            events = []
            second_service = ChannelExportService(
                client=client,
                base_dir=Path(tmpdir),
                event_sink=events.append,
            )

            result = await second_service.export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                )
            )

            self.assertEqual(result.run_mode, "incremental")
            self.assertEqual(result.posts_exported_this_run, 0)
            self.assertEqual(result.message_count, 1)
            self.assertEqual(state_path.read_text(encoding="utf-8"), initial_state)
            self.assertEqual(events[-2].name, "channel_export.no_new_posts")

    async def test_force_reexport_overwrites_existing_dataset(self):
        entity = FakeChannelEntity()
        first_client = FakeChannelClient(entity, [make_message(1, text="First")])
        second_client = FakeChannelClient(entity, [make_message(2, text="Second")])

        with tempfile.TemporaryDirectory(prefix="tg_channel_service_force_") as tmpdir:
            await ChannelExportService(
                client=first_client,
                base_dir=Path(tmpdir),
            ).export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                )
            )

            result = await ChannelExportService(
                client=second_client,
                base_dir=Path(tmpdir),
            ).export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                    force=True,
                )
            )

            exported_ids = [
                json.loads(line)["message_id"]
                for line in result.messages_jsonl_path.read_text(
                    encoding="utf-8"
                ).splitlines()
            ]
            self.assertEqual(result.run_mode, "force_full")
            self.assertEqual(exported_ids, [2])
            self.assertEqual(result.message_count, 1)

    async def test_state_is_not_updated_when_manifest_write_fails(self):
        entity = FakeChannelEntity()
        first_client = FakeChannelClient(entity, [make_message(1, text="First")])
        second_client = FakeChannelClient(
            entity,
            [make_message(1, text="First"), make_message(2, text="Second")],
        )

        with tempfile.TemporaryDirectory(
            prefix="tg_channel_service_failure_"
        ) as tmpdir:
            await ChannelExportService(
                client=first_client,
                base_dir=Path(tmpdir),
            ).export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                )
            )

            state_path = Path(tmpdir) / "@daily__123" / "channel_export_state.json"
            initial_state = json.loads(state_path.read_text(encoding="utf-8"))

            with self.assertRaisesRegex(RuntimeError, "manifest write failed"):
                await ChannelExportService(
                    client=second_client,
                    base_dir=Path(tmpdir),
                    manifest_writer=FailingManifestWriter(),
                ).export_channel(
                    ChannelExportOptions(
                        channel="@daily",
                        limit=None,
                        media_mode="metadata",
                        output_dir=Path(tmpdir),
                    )
                )

            state_after_failure = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(state_after_failure, initial_state)

    async def test_export_channel_emits_progress_and_completion_events(self):
        entity = FakeChannelEntity()
        client = FakeChannelClient(
            entity,
            [
                make_message(1, text="One"),
                make_message(2, text="Two"),
                make_message(3, text="Three"),
            ],
        )
        events = []

        with tempfile.TemporaryDirectory(prefix="tg_channel_service_events_") as tmpdir:
            service = ChannelExportService(
                client=client,
                base_dir=Path(tmpdir),
                event_sink=events.append,
                progress_interval=2,
            )
            await service.export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                )
            )

            event_names = [event.name for event in events]
            self.assertIn("channel_export.started", event_names)
            self.assertIn("channel_export.channel_resolved", event_names)
            self.assertIn("channel_export.state_loaded", event_names)
            self.assertIn("channel_export.progress", event_names)
            self.assertEqual(events[-1].name, "channel_export.completed")
            progress_payloads = [
                event.payload
                for event in events
                if event.name == "channel_export.progress"
            ]
            self.assertEqual(progress_payloads[-1]["processed_posts"], 3)

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


if __name__ == "__main__":
    unittest.main()
