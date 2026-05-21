import unittest
from datetime import datetime, timezone
from pathlib import Path

from tg_msg_manager.services.channel_export.discussions.models import (
    ChannelDiscussionCommentRecord,
    ChannelDiscussionExportResult,
    ChannelDiscussionExportState,
    ChannelDiscussionOptions,
    ChannelDiscussionThreadRecord,
)


class TestChannelDiscussionModels(unittest.TestCase):
    def test_discussion_options_can_be_constructed(self):
        options = ChannelDiscussionOptions(mode=" FULL ", max_comments_per_post=50)

        self.assertEqual(options.mode, "full")
        self.assertEqual(options.max_comments_per_post, 50)

    def test_thread_record_can_be_constructed(self):
        record = ChannelDiscussionThreadRecord(
            channel_id=111,
            channel_username="example",
            channel_message_id=5001,
            discussion_chat_id=222,
            discussion_root_message_id=98765,
            comments_count=42,
            exported_comments_count=40,
            status="partial",
            error=None,
        )

        self.assertEqual(record.channel_message_id, 5001)
        self.assertEqual(record.status, "partial")

    def test_comment_record_can_be_constructed(self):
        timestamp = datetime(2026, 5, 8, 12, 0, tzinfo=timezone.utc)

        record = ChannelDiscussionCommentRecord(
            message_id=98770,
            discussion_chat_id=222,
            channel_id=111,
            channel_message_id=5001,
            discussion_root_message_id=98765,
            author_id=123,
            author_name="User",
            username="user",
            timestamp=timestamp,
            text="comment text",
            reply_to_id=98765,
            media=(),
            reactions={"like": 1},
            raw_payload={"id": 98770},
        )

        self.assertEqual(record.message_id, 98770)
        self.assertEqual(record.reply_to_id, 98765)
        self.assertEqual(record.reactions, {"like": 1})

    def test_state_record_can_be_constructed(self):
        now = datetime(2026, 5, 8, 12, 0, tzinfo=timezone.utc)

        state = ChannelDiscussionExportState(
            schema_version="1.0",
            channel_id=111,
            discussion_chat_id=222,
            last_run_at=now,
            thread_count_total=10,
            comment_count_total=237,
            failed_thread_count_total=1,
            last_run_status="completed",
            updated_at=now,
        )

        self.assertEqual(state.channel_id, 111)
        self.assertEqual(state.comment_count_total, 237)

    def test_result_record_can_be_constructed(self):
        result = ChannelDiscussionExportResult(
            mode="full",
            discussion_chat_id=222,
            thread_count=10,
            comment_count=237,
            failed_thread_count=1,
            comments_jsonl_path=Path("/tmp/discussion_comments.jsonl"),
            comments_txt_path=Path("/tmp/discussion_comments.txt"),
            threads_jsonl_path=Path("/tmp/discussion_threads.jsonl"),
            state_path=Path("/tmp/discussion_export_state.json"),
        )

        self.assertEqual(result.mode, "full")
        self.assertEqual(result.thread_count, 10)


if __name__ == "__main__":
    unittest.main()
