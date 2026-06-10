import unittest
from types import SimpleNamespace

from tg_msg_manager.services.channel_export.discussions.artifact_builder import (
    ChannelDiscussionArtifactBuilder,
)
from tg_msg_manager.services.channel_export.discussions.models import (
    DISCUSSION_SOURCE_STATUS_NOT_AVAILABLE,
    DISCUSSION_SOURCE_STATUS_NOT_LINKED,
    DISCUSSION_SOURCE_STATUS_RESOLVED,
    DISCUSSION_THREAD_STATUS_EXPORTED,
    DISCUSSION_THREAD_STATUS_FAILED,
    DISCUSSION_THREAD_STATUS_NO_COMMENTS,
    DISCUSSION_THREAD_STATUS_NOT_AVAILABLE,
    DISCUSSION_THREAD_STATUS_NOT_LINKED,
    DISCUSSION_THREAD_STATUS_PARTIAL,
    ChannelDiscussionSource,
)


def make_channel_identity():
    return SimpleNamespace(channel_id=111, username="example")


def make_post(message_id=5001, *, replies_count=None, raw_payload=None):
    return SimpleNamespace(
        message_id=message_id,
        replies_count=replies_count,
        raw_payload=raw_payload or {},
    )


def make_source(
    *,
    status=DISCUSSION_SOURCE_STATUS_RESOLVED,
    discussion_chat_id=222,
    error=None,
):
    return ChannelDiscussionSource(
        status=status,
        discussion_chat_id=discussion_chat_id,
        discussion_entity=object()
        if status == DISCUSSION_SOURCE_STATUS_RESOLVED
        else None,
        error=error,
    )


class TestChannelDiscussionArtifactBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = ChannelDiscussionArtifactBuilder()
        self.channel_identity = make_channel_identity()

    def test_builds_not_linked_thread_record(self):
        thread = self.builder.build_not_linked_thread(
            channel_identity=self.channel_identity,
            post=make_post(),
            discussion_source=make_source(
                status=DISCUSSION_SOURCE_STATUS_NOT_LINKED,
                discussion_chat_id=None,
            ),
        )

        self.assertEqual(thread.status, DISCUSSION_THREAD_STATUS_NOT_LINKED)
        self.assertIsNone(thread.discussion_chat_id)
        self.assertEqual(thread.comments_count, 0)
        self.assertEqual(thread.exported_comments_count, 0)

    def test_builds_not_available_thread_record_with_source_error(self):
        thread = self.builder.build_not_available_thread(
            channel_identity=self.channel_identity,
            post=make_post(),
            discussion_source=make_source(
                status=DISCUSSION_SOURCE_STATUS_NOT_AVAILABLE,
                discussion_chat_id=None,
                error="discussion unavailable",
            ),
        )

        self.assertEqual(thread.status, DISCUSSION_THREAD_STATUS_NOT_AVAILABLE)
        self.assertEqual(thread.error, "discussion unavailable")

    def test_builds_failed_thread_record_with_fetch_error(self):
        thread = self.builder.build_failed_thread(
            channel_identity=self.channel_identity,
            post=make_post(),
            discussion_source=make_source(),
            error="fetch failed",
        )

        self.assertEqual(thread.status, DISCUSSION_THREAD_STATUS_FAILED)
        self.assertEqual(thread.error, "fetch failed")

    def test_discussion_comments_presence_uses_replies_count_first(self):
        self.assertFalse(
            self.builder.post_has_discussion_comments(make_post(replies_count=0))
        )
        self.assertTrue(
            self.builder.post_has_discussion_comments(make_post(replies_count=1))
        )

    def test_discussion_comments_presence_uses_raw_payload_fallback(self):
        self.assertFalse(
            self.builder.post_has_discussion_comments(
                make_post(raw_payload={"replies": None})
            )
        )
        self.assertTrue(
            self.builder.post_has_discussion_comments(
                make_post(
                    raw_payload={
                        "replies": {
                            "comments": True,
                            "replies": "2",
                        }
                    }
                )
            )
        )

    def test_metadata_record_uses_raw_replies_payload(self):
        record = self.builder.build_metadata_record(
            channel_identity=self.channel_identity,
            post=make_post(
                raw_payload={
                    "replies": {
                        "comments": True,
                        "channel_id": "222",
                        "replies": "90",
                    }
                }
            ),
        )

        self.assertEqual(record.channel_id, 111)
        self.assertEqual(record.channel_message_id, 5001)
        self.assertTrue(record.has_comments)
        self.assertEqual(record.discussion_chat_id, 222)
        self.assertEqual(record.replies_count, 90)
        self.assertFalse(record.comments_exported)
        self.assertEqual(record.source, "raw_payload.replies")

    def test_discussion_root_id_prefers_post_raw_payload(self):
        root_id = self.builder.discussion_root_message_id(
            make_post(raw_payload={"discussion_root_id": "98765"}),
            [SimpleNamespace(reply_to_id=123)],
        )

        self.assertEqual(root_id, 98765)

    def test_discussion_root_id_falls_back_to_comment_reply_object(self):
        root_id = self.builder.discussion_root_message_id(
            make_post(),
            [SimpleNamespace(reply_to=SimpleNamespace(reply_to_msg_id="98765"))],
        )

        self.assertEqual(root_id, 98765)

    def test_fetched_thread_status_exported_when_all_comments_written(self):
        thread = self.builder.build_fetched_thread(
            channel_identity=self.channel_identity,
            post=make_post(replies_count=2),
            discussion_source=make_source(),
            discussion_root_message_id=98765,
            exported_comments_count=2,
            has_more=False,
        )

        self.assertEqual(thread.status, DISCUSSION_THREAD_STATUS_EXPORTED)
        self.assertEqual(thread.comments_count, 2)
        self.assertEqual(thread.exported_comments_count, 2)
        self.assertEqual(thread.discussion_root_message_id, 98765)

    def test_fetched_thread_status_partial_when_more_comments_are_available(self):
        thread = self.builder.build_fetched_thread(
            channel_identity=self.channel_identity,
            post=make_post(),
            discussion_source=make_source(),
            discussion_root_message_id=None,
            exported_comments_count=2,
            has_more=True,
        )

        self.assertEqual(thread.status, DISCUSSION_THREAD_STATUS_PARTIAL)
        self.assertEqual(thread.comments_count, 3)

    def test_fetched_thread_status_partial_when_replies_count_exceeds_exported(self):
        thread = self.builder.build_fetched_thread(
            channel_identity=self.channel_identity,
            post=make_post(replies_count=3),
            discussion_source=make_source(),
            discussion_root_message_id=None,
            exported_comments_count=2,
            has_more=False,
        )

        self.assertEqual(thread.status, DISCUSSION_THREAD_STATUS_PARTIAL)
        self.assertEqual(thread.comments_count, 3)

    def test_fetched_thread_status_no_comments_preserves_known_count(self):
        thread = self.builder.build_fetched_thread(
            channel_identity=self.channel_identity,
            post=make_post(replies_count=3),
            discussion_source=make_source(),
            discussion_root_message_id=None,
            exported_comments_count=0,
            has_more=False,
        )

        self.assertEqual(thread.status, DISCUSSION_THREAD_STATUS_NO_COMMENTS)
        self.assertEqual(thread.comments_count, 3)
        self.assertEqual(thread.exported_comments_count, 0)


if __name__ == "__main__":
    unittest.main()
