import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

from tg_msg_manager.core.models.message import MessageData
from tg_msg_manager.services.channel_export.models import ChannelIdentity
from tg_msg_manager.services.channel_export.post_mapper import ChannelPostMapper


def make_message(
    *,
    message_id=100,
    text="hello",
    media_type=None,
    raw_payload=None,
    media_ref=None,
):
    return MessageData(
        message_id=message_id,
        chat_id=77,
        user_id=11,
        author_name="Poster",
        timestamp=datetime(2026, 5, 7, 12, 0, tzinfo=timezone.utc),
        text=text,
        media_type=media_type,
        reply_to_id=None,
        fwd_from_id=None,
        context_group_id=None,
        raw_payload=raw_payload or {},
        media_ref=media_ref,
    )


class TestChannelPostMapper(unittest.TestCase):
    def setUp(self):
        self.channel = ChannelIdentity(channel_id=77, title="Title", username="title")
        self.mapper = ChannelPostMapper(media_policy=SimpleNamespace())

    def test_map_post_handles_text_only_message(self):
        record = self.mapper.map_post(
            make_message(), self.channel, media_mode="metadata"
        )

        self.assertEqual(record.message_id, 100)
        self.assertEqual(record.text, "hello")
        self.assertEqual(record.media, ())
        self.assertEqual(record.channel_title, "Title")

    def test_map_post_extracts_media_metadata(self):
        message = make_message(
            message_id=12345,
            media_type="Photo",
            raw_payload={"views": 10, "forwards": 2, "replies_count": 1},
            media_ref={
                "mime_type": "image/jpeg",
                "file_name": "post.jpg",
                "file_size": 512,
                "width": 640,
                "height": 480,
            },
        )

        record = self.mapper.map_post(message, self.channel, media_mode="metadata")

        self.assertEqual(len(record.media), 1)
        self.assertEqual(record.media[0].media_id, "12345_01")
        self.assertEqual(
            record.media[0].local_path, "media/photos/0000012345_01_post.jpg"
        )
        self.assertEqual(record.media[0].media_type, "photo")
        self.assertEqual(record.media[0].download_status, "metadata_only")
        self.assertEqual(record.media[0].filename_strategy, "original_filename")
        self.assertEqual(record.media[0].final_filename, "0000012345_01_post.jpg")
        self.assertEqual(record.views, 10)
        self.assertEqual(record.forwards, 2)
        self.assertEqual(record.replies_count, 1)

    def test_map_post_reads_top_level_replies_count(self):
        record = self.mapper.map_post(
            make_message(raw_payload={"replies_count": "4"}),
            self.channel,
            media_mode="metadata",
        )

        self.assertEqual(record.replies_count, 4)

    def test_map_post_reads_nested_replies_count(self):
        record = self.mapper.map_post(
            make_message(raw_payload={"replies": {"replies": "7"}}),
            self.channel,
            media_mode="metadata",
        )

        self.assertEqual(record.replies_count, 7)

    def test_map_post_prefers_top_level_replies_count_over_nested(self):
        record = self.mapper.map_post(
            make_message(
                raw_payload={
                    "replies_count": 2,
                    "replies": {"replies": 99},
                }
            ),
            self.channel,
            media_mode="metadata",
        )

        self.assertEqual(record.replies_count, 2)

    def test_map_post_ignores_invalid_nested_replies_count(self):
        record = self.mapper.map_post(
            make_message(raw_payload={"replies": {"replies": "invalid"}}),
            self.channel,
            media_mode="metadata",
        )

        self.assertIsNone(record.replies_count)

    def test_map_post_ignores_missing_and_non_dict_nested_replies_count(self):
        missing = self.mapper.map_post(
            make_message(raw_payload={}),
            self.channel,
            media_mode="metadata",
        )
        non_dict = self.mapper.map_post(
            make_message(raw_payload={"replies": "invalid"}),
            self.channel,
            media_mode="metadata",
        )

        self.assertIsNone(missing.replies_count)
        self.assertIsNone(non_dict.replies_count)

    def test_map_post_handles_missing_views_forwards_and_reactions(self):
        record = self.mapper.map_post(
            make_message(raw_payload={}),
            self.channel,
            media_mode="metadata",
        )

        self.assertIsNone(record.views)
        self.assertIsNone(record.forwards)
        self.assertEqual(record.reactions, {})

    def test_map_post_handles_empty_text(self):
        record = self.mapper.map_post(
            make_message(text=None, raw_payload={"message": None}),
            self.channel,
            media_mode="metadata",
        )

        self.assertIsNone(record.text)

    def test_map_post_uses_raw_payload_when_optional_fields_exist_there(self):
        record = self.mapper.map_post(
            SimpleNamespace(
                message_id=100,
                text=None,
                message=None,
                timestamp=None,
                date=None,
                media_type=None,
                raw_payload={
                    "message": "from raw payload",
                    "date": "2026-05-07T13:00:00+00:00",
                    "reactions": {"fire": 5},
                },
                media_ref=None,
            ),
            self.channel,
            media_mode="metadata",
        )

        self.assertEqual(record.text, "from raw payload")
        self.assertEqual(record.timestamp.isoformat(), "2026-05-07T13:00:00+00:00")
        self.assertEqual(record.reactions, {"fire": 5})

    def test_map_post_omits_detailed_media_in_none_mode(self):
        record = self.mapper.map_post(
            make_message(media_type="Photo", media_ref={"mime_type": "image/jpeg"}),
            self.channel,
            media_mode="none",
        )

        self.assertEqual(record.media, ())


if __name__ == "__main__":
    unittest.main()
