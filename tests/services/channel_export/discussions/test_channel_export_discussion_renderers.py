import json
import unittest
from datetime import datetime, timezone

from tg_msg_manager.services.channel_export.discussions.jsonl_renderer import (
    ChannelDiscussionJsonlRenderer,
)
from tg_msg_manager.services.channel_export.discussions.models import (
    ChannelDiscussionCommentRecord,
    ChannelDiscussionThreadRecord,
)
from tg_msg_manager.services.channel_export.discussions.txt_renderer import (
    ChannelDiscussionTxtRenderer,
)


def make_comment_record() -> ChannelDiscussionCommentRecord:
    return ChannelDiscussionCommentRecord(
        message_id=98770,
        discussion_chat_id=222,
        channel_id=111,
        channel_message_id=5001,
        discussion_root_message_id=98765,
        author_id=123,
        author_name="User",
        username="user",
        timestamp=datetime(2026, 5, 8, 12, 0, tzinfo=timezone.utc),
        text="comment text",
        reply_to_id=98765,
        media=(),
        reactions={"like": 1},
        raw_payload={"created_at": datetime(2026, 5, 8, 12, 0, tzinfo=timezone.utc)},
    )


class TestChannelDiscussionRenderers(unittest.TestCase):
    def test_jsonl_comment_line_is_valid_json_with_iso_datetime(self):
        line = ChannelDiscussionJsonlRenderer().render_comment_line(
            make_comment_record()
        )

        payload = json.loads(line)
        self.assertEqual(payload["message_id"], 98770)
        self.assertEqual(payload["timestamp"], "2026-05-08T12:00:00+00:00")
        self.assertEqual(
            payload["raw_payload"]["created_at"], "2026-05-08T12:00:00+00:00"
        )

    def test_jsonl_thread_line_is_valid_json(self):
        record = ChannelDiscussionThreadRecord(
            channel_id=111,
            channel_username="example",
            channel_message_id=5001,
            discussion_chat_id=222,
            discussion_root_message_id=98765,
            comments_count=2,
            exported_comments_count=2,
            status="exported",
            error=None,
        )

        payload = json.loads(
            ChannelDiscussionJsonlRenderer().render_thread_line(record)
        )

        self.assertEqual(payload["channel_message_id"], 5001)
        self.assertEqual(payload["status"], "exported")

    def test_txt_output_includes_timestamp_author_and_text(self):
        text = ChannelDiscussionTxtRenderer().render_comment_block(
            make_comment_record()
        )

        self.assertIn("2026-05-08 12:00:00 UTC", text)
        self.assertIn("User (ID: 123, username: user)", text)
        self.assertIn("comment text", text)


if __name__ == "__main__":
    unittest.main()
