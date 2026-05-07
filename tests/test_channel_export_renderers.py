import json
import unittest
from datetime import datetime, timezone

from tg_msg_manager.services.channel_export.jsonl_renderer import (
    ChannelJsonlRenderer,
    channel_post_to_dict,
)
from tg_msg_manager.services.channel_export.media_manifest_writer import (
    ChannelMediaManifestWriter,
)
from tg_msg_manager.services.channel_export.models import (
    ChannelMediaRecord,
    ChannelPostRecord,
)
from tg_msg_manager.services.channel_export.txt_renderer import (
    ChannelTxtRenderer,
    NO_TEXT_PLACEHOLDER,
    SEPARATOR,
)


def make_media_record() -> ChannelMediaRecord:
    return ChannelMediaRecord(
        media_id="m1",
        message_id=12345,
        media_index=1,
        media_type="photo",
        mime_type="image/jpeg",
        file_name="photo.jpg",
        file_size=512,
        width=640,
        height=480,
        duration=None,
        local_path="media/photos/0000012345_01.jpg",
        sha256=None,
        download_status="metadata_only",
    )


def make_post_record(*, text: str = "Привіт, світ!") -> ChannelPostRecord:
    return ChannelPostRecord(
        message_id=12345,
        channel_id=99,
        channel_title="Daily Briefing",
        channel_username="dailybrief",
        timestamp=datetime(2026, 5, 7, 10, 11, 12, tzinfo=timezone.utc),
        text=text,
        views=100,
        forwards=5,
        replies_count=2,
        reactions={"like": 3},
        media=(make_media_record(),),
        raw_payload={"source": "fixture"},
    )


class TestChannelExportRenderers(unittest.TestCase):
    def test_jsonl_renderer_returns_valid_one_line_json(self):
        line = ChannelJsonlRenderer().render_line(make_post_record())

        self.assertNotIn("\n", line)
        data = json.loads(line)
        self.assertEqual(data["message_id"], 12345)
        self.assertEqual(data["timestamp"], "2026-05-07T10:11:12+00:00")
        self.assertEqual(
            data["media"][0]["local_path"], "media/photos/0000012345_01.jpg"
        )
        self.assertEqual(data["text"], "Привіт, світ!")

    def test_channel_post_to_dict_preserves_unicode_and_media(self):
        data = channel_post_to_dict(make_post_record())

        self.assertEqual(data["channel_title"], "Daily Briefing")
        self.assertEqual(data["text"], "Привіт, світ!")
        self.assertEqual(data["media"][0]["media_type"], "photo")

    def test_jsonl_renderer_normalizes_nested_datetime_values_in_raw_payload(self):
        record = make_post_record()
        nested_dt = datetime(2026, 5, 7, 15, 30, 0, tzinfo=timezone.utc)
        record = ChannelPostRecord(
            message_id=record.message_id,
            channel_id=record.channel_id,
            channel_title=record.channel_title,
            channel_username=record.channel_username,
            timestamp=record.timestamp,
            text=record.text,
            views=record.views,
            forwards=record.forwards,
            replies_count=record.replies_count,
            reactions={"items": [{"when": nested_dt}]},
            media=record.media,
            raw_payload={
                "source": "fixture",
                "edited_at": nested_dt,
                "nested": {"items": [nested_dt]},
            },
        )

        data = json.loads(ChannelJsonlRenderer().render_line(record))

        self.assertEqual(data["raw_payload"]["edited_at"], "2026-05-07T15:30:00+00:00")
        self.assertEqual(
            data["raw_payload"]["nested"]["items"][0],
            "2026-05-07T15:30:00+00:00",
        )
        self.assertEqual(
            data["reactions"]["items"][0]["when"],
            "2026-05-07T15:30:00+00:00",
        )

    def test_txt_renderer_renders_message_id_separator_and_media(self):
        block = ChannelTxtRenderer().render_block(make_post_record())

        self.assertIn("message_id=12345", block)
        self.assertIn("[2026-05-07 10:11:12 UTC]", block)
        self.assertIn("Daily Briefing (@dailybrief)", block)
        self.assertIn("Привіт, світ!", block)
        self.assertIn("Media:", block)
        self.assertIn("- photo: media/photos/0000012345_01.jpg [metadata_only]", block)
        self.assertTrue(block.endswith(SEPARATOR))

    def test_txt_renderer_handles_empty_text_consistently(self):
        record = make_post_record(text=None)

        block = ChannelTxtRenderer().render_block(record)

        self.assertIn(NO_TEXT_PLACEHOLDER, block)

    def test_media_manifest_writer_renders_one_json_line(self):
        line = ChannelMediaManifestWriter().render_line(make_media_record())

        self.assertNotIn("\n", line)
        data = json.loads(line)
        self.assertEqual(data["media_id"], "m1")
        self.assertEqual(data["message_id"], 12345)
        self.assertEqual(data["download_status"], "metadata_only")
        self.assertEqual(data["width"], 640)
        self.assertEqual(data["height"], 480)


if __name__ == "__main__":
    unittest.main()
