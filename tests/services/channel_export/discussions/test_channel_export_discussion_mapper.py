import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

from tg_msg_manager.services.channel_export.discussions.mapper import (
    ChannelDiscussionMapper,
)


class TestChannelDiscussionMapper(unittest.TestCase):
    def test_maps_author_text_timestamp_and_reply_to_id(self):
        timestamp = datetime(2026, 5, 8, 12, 0, tzinfo=timezone.utc)
        comment = SimpleNamespace(
            id=98770,
            sender=SimpleNamespace(id=123, first_name="Test", last_name="User"),
            username="user",
            date=timestamp,
            message="comment text",
            reply_to_id=98765,
            reactions={"like": 2},
            raw_payload={"id": 98770},
        )
        post = SimpleNamespace(channel_id=111, message_id=5001)

        record = ChannelDiscussionMapper().map_comment(
            comment,
            channel_post_record=post,
            discussion_chat_id=222,
            discussion_root_message_id=98765,
        )

        self.assertEqual(record.message_id, 98770)
        self.assertEqual(record.author_id, 123)
        self.assertEqual(record.author_name, "Test User")
        self.assertEqual(record.username, "user")
        self.assertEqual(record.timestamp, timestamp)
        self.assertEqual(record.text, "comment text")
        self.assertEqual(record.reply_to_id, 98765)
        self.assertEqual(record.reactions, {"like": 2})

    def test_handles_missing_author_and_text(self):
        record = ChannelDiscussionMapper().map_comment(
            SimpleNamespace(id=1),
            channel_post_record=SimpleNamespace(channel_id=111, message_id=5001),
            discussion_chat_id=222,
            discussion_root_message_id=None,
        )

        self.assertIsNone(record.author_id)
        self.assertIsNone(record.author_name)
        self.assertIsNone(record.username)
        self.assertIsNone(record.text)

    def test_maps_media_metadata_without_download(self):
        comment = SimpleNamespace(
            id=1,
            date=datetime(2026, 5, 8, 12, 0, tzinfo=timezone.utc),
            media_type="photo",
            media={
                "mime_type": "image/jpeg",
                "file_name": "image.jpg",
                "file_size": 128,
            },
        )

        record = ChannelDiscussionMapper().map_comment(
            comment,
            channel_post_record=SimpleNamespace(channel_id=111, message_id=5001),
            discussion_chat_id=222,
            discussion_root_message_id=None,
        )

        self.assertEqual(record.media[0]["media_type"], "photo")
        self.assertEqual(record.media[0]["download_status"], "metadata_only")


if __name__ == "__main__":
    unittest.main()
