import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from tg_msg_manager.services.channel_export.jsonl_renderer import ChannelJsonlRenderer
from tg_msg_manager.services.channel_export.media_manifest_writer import (
    ChannelMediaManifestWriter,
)
from tg_msg_manager.services.channel_export.models import (
    ChannelExportPlan,
    ChannelMediaRecord,
    ChannelPostRecord,
)
from tg_msg_manager.services.channel_export.payload_writer import ChannelPayloadWriter
from tg_msg_manager.services.channel_export.txt_renderer import ChannelTxtRenderer


def make_post(*, message_id, text, timestamp, media=()):
    return ChannelPostRecord(
        message_id=message_id,
        channel_id=7,
        channel_title="Updates",
        channel_username="updates",
        timestamp=timestamp,
        text=text,
        views=None,
        forwards=None,
        replies_count=None,
        reactions={},
        media=media,
        raw_payload={},
    )


class TestChannelPayloadWriter(unittest.TestCase):
    def test_write_records_writes_files_and_counts_messages_and_media(self):
        with tempfile.TemporaryDirectory(prefix="tg_channel_writer_") as tmpdir:
            output_dir = Path(tmpdir) / "channel"
            plan = ChannelExportPlan(
                output_dir=output_dir,
                manifest_path=output_dir / "manifest.json",
                messages_jsonl_path=output_dir / "messages.jsonl",
                messages_txt_path=output_dir / "messages.txt",
                media_manifest_path=output_dir / "media_manifest.jsonl",
                media_dir=output_dir / "media",
            )
            media = (
                ChannelMediaRecord(
                    media_id="1_01",
                    message_id=1,
                    media_index=1,
                    media_type="photo",
                    mime_type="image/jpeg",
                    file_name="a.jpg",
                    file_size=10,
                    width=100,
                    height=50,
                    duration=None,
                    local_path="media/photos/0000000001_01.jpg",
                    sha256=None,
                    download_status="metadata_only",
                ),
            )
            records = [
                make_post(
                    message_id=1,
                    text="Привіт",
                    timestamp=datetime(2026, 5, 7, 10, 0, tzinfo=timezone.utc),
                    media=media,
                ),
                make_post(
                    message_id=2,
                    text="World",
                    timestamp=datetime(2026, 5, 7, 11, 0, tzinfo=timezone.utc),
                ),
            ]

            message_count, media_count, date_from, date_to = (
                ChannelPayloadWriter().write_records(
                    plan=plan,
                    records=records,
                    jsonl_renderer=ChannelJsonlRenderer(),
                    txt_renderer=ChannelTxtRenderer(),
                    media_manifest_writer=ChannelMediaManifestWriter(),
                )
            )

            self.assertEqual(message_count, 2)
            self.assertEqual(media_count, 1)
            self.assertEqual(date_from.isoformat(), "2026-05-07T10:00:00+00:00")
            self.assertEqual(date_to.isoformat(), "2026-05-07T11:00:00+00:00")
            jsonl_lines = plan.messages_jsonl_path.read_text(
                encoding="utf-8"
            ).splitlines()
            self.assertEqual(len(jsonl_lines), 2)
            self.assertEqual(json.loads(jsonl_lines[0])["text"], "Привіт")
            self.assertIn("Привіт", plan.messages_txt_path.read_text(encoding="utf-8"))
            self.assertEqual(
                len(plan.media_manifest_path.read_text(encoding="utf-8").splitlines()),
                1,
            )

    def test_write_records_handles_empty_channel_and_creates_files(self):
        with tempfile.TemporaryDirectory(prefix="tg_channel_writer_empty_") as tmpdir:
            output_dir = Path(tmpdir) / "channel"
            plan = ChannelExportPlan(
                output_dir=output_dir,
                manifest_path=output_dir / "manifest.json",
                messages_jsonl_path=output_dir / "messages.jsonl",
                messages_txt_path=output_dir / "messages.txt",
                media_manifest_path=output_dir / "media_manifest.jsonl",
                media_dir=output_dir / "media",
            )

            counts = ChannelPayloadWriter().write_records(
                plan=plan,
                records=[],
                jsonl_renderer=ChannelJsonlRenderer(),
                txt_renderer=ChannelTxtRenderer(),
                media_manifest_writer=ChannelMediaManifestWriter(),
            )

            self.assertEqual(counts, (0, 0, None, None))
            self.assertEqual(plan.messages_jsonl_path.read_text(encoding="utf-8"), "")
            self.assertEqual(plan.messages_txt_path.read_text(encoding="utf-8"), "")
            self.assertEqual(plan.media_manifest_path.read_text(encoding="utf-8"), "")


if __name__ == "__main__":
    unittest.main()
