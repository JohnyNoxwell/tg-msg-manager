import json
import unittest
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from tg_msg_manager.services.channel_export.discussions.jsonl_renderer import (
    ChannelDiscussionJsonlRenderer,
)
from tg_msg_manager.services.channel_export.discussions.models import (
    ALLOWED_DISCUSSION_THREAD_STATUSES,
    ChannelDiscussionCommentRecord,
    ChannelDiscussionRunStats,
    ChannelDiscussionThreadRecord,
)
from tg_msg_manager.services.channel_export.discussions.state_manager import (
    ChannelDiscussionStateManager,
)
from tg_msg_manager.services.channel_export.discussions.txt_renderer import (
    ChannelDiscussionTxtRenderer,
)
from tg_msg_manager.services.channel_export.jsonl_renderer import ChannelJsonlRenderer
from tg_msg_manager.services.channel_export.manifest_coordinator import (
    build_channel_export_manifest,
)
from tg_msg_manager.services.channel_export.media_manifest_writer import (
    ChannelMediaManifestWriter,
)
from tg_msg_manager.services.channel_export.models import (
    ChannelExportOptions,
    ChannelExportRunStats,
    ChannelIdentity,
    ChannelMediaRecord,
    ChannelPostRecord,
)
from tg_msg_manager.services.channel_export.state_manager import (
    ChannelExportStateManager,
)
from tg_msg_manager.services.channel_export.txt_renderer import ChannelTxtRenderer

MESSAGE_KEYS = {
    "message_id",
    "channel_id",
    "channel_title",
    "channel_username",
    "timestamp",
    "text",
    "views",
    "forwards",
    "replies_count",
    "reactions",
    "media",
    "raw_payload",
}

MESSAGE_MEDIA_KEYS = {
    "media_id",
    "message_id",
    "media_index",
    "media_type",
    "mime_type",
    "file_name",
    "file_size",
    "width",
    "height",
    "duration",
    "local_path",
    "sha256",
    "download_status",
}

MEDIA_MANIFEST_KEYS = MESSAGE_MEDIA_KEYS | {
    "error",
    "original_filename",
    "detected_extension",
    "filename_strategy",
    "final_filename",
    "final_path",
}

DISCUSSION_COMMENT_KEYS = {
    "message_id",
    "discussion_chat_id",
    "channel_id",
    "channel_message_id",
    "discussion_root_message_id",
    "author_id",
    "author_name",
    "username",
    "timestamp",
    "text",
    "reply_to_id",
    "media",
    "reactions",
    "raw_payload",
}

DISCUSSION_THREAD_KEYS = {
    "channel_id",
    "channel_username",
    "channel_message_id",
    "discussion_chat_id",
    "discussion_root_message_id",
    "comments_count",
    "exported_comments_count",
    "status",
    "error",
}

CHANNEL_STATE_KEYS = {
    "schema_version",
    "channel_id",
    "channel_username",
    "channel_title",
    "last_exported_message_id",
    "last_exported_at",
    "message_count_total",
    "media_count_total",
    "downloaded_media_count_total",
    "already_existing_media_count_total",
    "skipped_media_count_total",
    "skipped_by_size_count_total",
    "skipped_by_type_count_total",
    "failed_media_count_total",
    "last_run_status",
    "updated_at",
    "date_from",
    "date_to",
    "last_manifest_path",
}

DISCUSSION_STATE_KEYS = {
    "schema_version",
    "channel_id",
    "discussion_chat_id",
    "last_run_at",
    "thread_count_total",
    "comment_count_total",
    "failed_thread_count_total",
    "last_run_status",
    "updated_at",
}


@dataclass(frozen=True)
class FakeDiscussionResult:
    discussion_chat_id: int
    thread_count: int
    comment_count: int
    failed_thread_count: int


def assert_exact_keys(testcase: unittest.TestCase, payload: dict, expected: set[str]):
    testcase.assertEqual(set(payload), expected)


def assert_iso_datetime(testcase: unittest.TestCase, value: str):
    testcase.assertIsInstance(datetime.fromisoformat(value), datetime)


def make_media_record(**overrides) -> ChannelMediaRecord:
    values = {
        "media_id": "123_01",
        "message_id": 123,
        "media_index": 1,
        "media_type": "photo",
        "mime_type": "image/jpeg",
        "file_name": "photo.jpg",
        "file_size": 512,
        "width": 640,
        "height": 480,
        "duration": None,
        "local_path": "media/photos/0000000123_01.jpg",
        "sha256": "a" * 64,
        "download_status": "downloaded",
        "error": None,
        "original_filename": "photo.jpg",
        "detected_extension": ".jpg",
        "filename_strategy": "original_filename",
        "final_filename": "0000000123_01.jpg",
        "final_path": "media/photos/0000000123_01.jpg",
    }
    values.update(overrides)
    return ChannelMediaRecord(**values)


def make_post_record(**overrides) -> ChannelPostRecord:
    values = {
        "message_id": 123,
        "channel_id": 777,
        "channel_title": "Daily",
        "channel_username": "daily",
        "timestamp": datetime(2026, 5, 8, 12, 0, tzinfo=timezone.utc),
        "text": "hello",
        "views": 10,
        "forwards": 1,
        "replies_count": 2,
        "reactions": {"like": 3},
        "media": (make_media_record(download_status="metadata_only", sha256=None),),
        "raw_payload": {"source": "fixture"},
    }
    values.update(overrides)
    return ChannelPostRecord(**values)


class TestChannelExportDatasetContracts(unittest.TestCase):
    def test_messages_jsonl_contract_has_exact_keys_and_types(self):
        payload = json.loads(ChannelJsonlRenderer().render_line(make_post_record()))

        assert_exact_keys(self, payload, MESSAGE_KEYS)
        self.assertIsInstance(payload["message_id"], int)
        self.assertIsInstance(payload["channel_id"], int)
        assert_iso_datetime(self, payload["timestamp"])
        self.assertIsInstance(payload["reactions"], dict)
        self.assertIsInstance(payload["raw_payload"], dict)
        self.assertIsInstance(payload["media"], list)
        assert_exact_keys(self, payload["media"][0], MESSAGE_MEDIA_KEYS)

        null_text_payload = json.loads(
            ChannelJsonlRenderer().render_line(make_post_record(text=None))
        )
        self.assertIsNone(null_text_payload["text"])

    def test_media_manifest_jsonl_contract_has_exact_keys_and_final_statuses(self):
        writer = ChannelMediaManifestWriter()
        records = [
            make_media_record(download_status="metadata_only", local_path=None),
            make_media_record(download_status="downloaded"),
            make_media_record(download_status="already_exists"),
            make_media_record(
                download_status="skipped_by_size",
                local_path=None,
                sha256=None,
                error="Media file exceeds max size",
            ),
            make_media_record(
                download_status="skipped_by_type",
                local_path=None,
                sha256=None,
                error="Media type is not allowed",
            ),
            make_media_record(
                download_status="failed",
                local_path=None,
                sha256=None,
                error="network down",
            ),
        ]

        payloads = [json.loads(writer.render_line(record)) for record in records]

        for payload in payloads:
            assert_exact_keys(self, payload, MEDIA_MANIFEST_KEYS)
            self.assertNotEqual(payload["download_status"], "pending")

        statuses = {payload["download_status"] for payload in payloads}
        self.assertEqual(
            statuses,
            {
                "metadata_only",
                "downloaded",
                "already_exists",
                "skipped_by_size",
                "skipped_by_type",
                "failed",
            },
        )
        self.assertTrue(payloads[1]["local_path"])
        self.assertTrue(payloads[1]["sha256"])
        self.assertTrue(payloads[2]["local_path"])
        self.assertTrue(payloads[2]["sha256"])
        self.assertEqual(payloads[3]["error"], "Media file exceeds max size")
        self.assertEqual(payloads[4]["error"], "Media type is not allowed")
        self.assertEqual(payloads[5]["error"], "network down")

    def test_discussion_comments_jsonl_contract_has_exact_keys(self):
        record = ChannelDiscussionCommentRecord(
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
            raw_payload={"id": 98770},
        )

        payload = json.loads(
            ChannelDiscussionJsonlRenderer().render_comment_line(record)
        )

        assert_exact_keys(self, payload, DISCUSSION_COMMENT_KEYS)
        self.assertEqual(payload["reply_to_id"], 98765)
        self.assertEqual(payload["media"], [])
        self.assertIsInstance(payload["reactions"], dict)
        self.assertIsInstance(payload["raw_payload"], dict)
        assert_iso_datetime(self, payload["timestamp"])

    def test_discussion_threads_jsonl_contract_has_exact_keys_and_statuses(self):
        renderer = ChannelDiscussionJsonlRenderer()

        for status in ALLOWED_DISCUSSION_THREAD_STATUSES:
            record = ChannelDiscussionThreadRecord(
                channel_id=111,
                channel_username="example",
                channel_message_id=5001,
                discussion_chat_id=222,
                discussion_root_message_id=98765,
                comments_count=2,
                exported_comments_count=1,
                status=status,
                error="boom" if status == "failed" else None,
            )
            payload = json.loads(renderer.render_thread_line(record))

            assert_exact_keys(self, payload, DISCUSSION_THREAD_KEYS)
            self.assertIn(payload["status"], ALLOWED_DISCUSSION_THREAD_STATUSES)

    def test_manifest_contract_without_and_with_discussion(self):
        channel = ChannelIdentity(channel_id=777, title="Daily", username="daily")
        manager = ChannelExportStateManager()
        stats = ChannelExportRunStats(
            mode="full",
            posts_exported=2,
            media_records_added=1,
            downloaded_media_count=1,
            already_existing_media_count=0,
            skipped_media_count=0,
            skipped_by_size_count=0,
            skipped_by_type_count=0,
            failed_media_count=0,
            date_from=datetime(2026, 5, 8, 11, 0, tzinfo=timezone.utc),
            date_to=datetime(2026, 5, 8, 12, 0, tzinfo=timezone.utc),
            last_exported_message_id=2,
        )
        state = manager.build_completed_state(
            channel=channel,
            stats=stats,
            manifest_path=Path("/exports/manifest.json"),
        )

        manifest = build_channel_export_manifest(
            channel=channel,
            state=state,
            options=ChannelExportOptions(
                channel="@daily",
                limit=None,
                media_mode="metadata",
                output_dir=Path("/exports"),
            ),
            media_mode="metadata",
        )
        self.assertEqual(
            set(manifest),
            {
                "dataset_type",
                "schema_version",
                "exported_at",
                "source",
                "export",
                "discussion",
                "status",
            },
        )
        self.assertEqual(
            set(manifest["source"]),
            {"type", "id", "username", "title"},
        )
        self.assertEqual(manifest["discussion"], {"mode": "none"})
        self.assertIn("messages.jsonl", manifest["export"]["included_files"])
        self.assertEqual(manifest["status"], "completed")

        discussion_manifest = build_channel_export_manifest(
            channel=channel,
            state=state,
            options=ChannelExportOptions(
                channel="@daily",
                limit=None,
                media_mode="full",
                output_dir=Path("/exports"),
                max_media_size=1024,
                media_types=("photo",),
                discussion_mode="full",
            ),
            media_mode="full",
            discussion_result=FakeDiscussionResult(
                discussion_chat_id=222,
                thread_count=2,
                comment_count=3,
                failed_thread_count=1,
            ),
        )
        self.assertEqual(discussion_manifest["discussion"]["mode"], "full")
        self.assertEqual(discussion_manifest["discussion"]["discussion_chat_id"], 222)
        self.assertEqual(
            discussion_manifest["discussion"]["max_comments_per_post"], 100
        )
        self.assertIn("media/", discussion_manifest["export"]["included_files"])
        self.assertEqual(discussion_manifest["export"]["max_media_size"], 1024)
        self.assertEqual(discussion_manifest["export"]["media_types"], ["photo"])

    def test_state_file_contracts_have_exact_keys(self):
        channel = ChannelIdentity(channel_id=777, title="Daily", username="daily")
        channel_state_manager = ChannelExportStateManager()
        channel_state = channel_state_manager.build_completed_state(
            channel=channel,
            stats=ChannelExportRunStats(
                mode="full",
                posts_exported=2,
                media_records_added=1,
                downloaded_media_count=1,
                already_existing_media_count=0,
                skipped_media_count=0,
                skipped_by_size_count=0,
                skipped_by_type_count=0,
                failed_media_count=0,
                date_from=None,
                date_to=None,
                last_exported_message_id=2,
            ),
            manifest_path=Path("/exports/manifest.json"),
        )
        channel_payload = channel_state_manager.to_dict(channel_state)

        assert_exact_keys(self, channel_payload, CHANNEL_STATE_KEYS)
        self.assertEqual(channel_payload["schema_version"], "1.0")
        self.assertEqual(channel_payload["channel_id"], 777)
        self.assertEqual(channel_payload["last_run_status"], "completed")
        assert_iso_datetime(self, channel_payload["last_exported_at"])
        assert_iso_datetime(self, channel_payload["updated_at"])

        discussion_state_manager = ChannelDiscussionStateManager()
        discussion_state = discussion_state_manager.build_completed_state(
            channel=channel,
            discussion_chat_id=222,
            stats=ChannelDiscussionRunStats(
                mode="full",
                thread_count=2,
                comment_count=3,
                failed_thread_count=1,
            ),
        )
        discussion_payload = discussion_state_manager.to_dict(discussion_state)

        assert_exact_keys(self, discussion_payload, DISCUSSION_STATE_KEYS)
        self.assertEqual(discussion_payload["schema_version"], "1.0")
        self.assertEqual(discussion_payload["channel_id"], 777)
        self.assertEqual(discussion_payload["discussion_chat_id"], 222)
        self.assertEqual(discussion_payload["thread_count_total"], 2)
        self.assertEqual(discussion_payload["comment_count_total"], 3)
        self.assertEqual(discussion_payload["failed_thread_count_total"], 1)
        self.assertEqual(discussion_payload["last_run_status"], "completed")
        assert_iso_datetime(self, discussion_payload["last_run_at"])
        assert_iso_datetime(self, discussion_payload["updated_at"])

    def test_txt_projection_smoke_contracts(self):
        post_text = ChannelTxtRenderer().render_block(make_post_record())
        comment_text = ChannelDiscussionTxtRenderer().render_comment_block(
            ChannelDiscussionCommentRecord(
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
            )
        )

        self.assertIn("message_id=123", post_text)
        self.assertIn("Media:", post_text)
        self.assertIn("comment text", comment_text)
        self.assertIn("username: user", comment_text)


if __name__ == "__main__":
    unittest.main()
