import unittest
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from tg_msg_manager.services.channel_export.manifest_coordinator import (
    build_channel_export_manifest,
)
from tg_msg_manager.services.channel_export.models import (
    ChannelExportOptions,
    ChannelExportState,
    ChannelIdentity,
)


@dataclass(frozen=True)
class FakeDiscussionResult:
    discussion_chat_id: int
    thread_count: int
    comment_count: int
    failed_thread_count: int


def make_options(**overrides):
    values = {
        "channel": "@daily",
        "limit": None,
        "media_mode": "metadata",
        "output_dir": Path("/exports"),
    }
    values.update(overrides)
    return ChannelExportOptions(**values)


def make_state(**overrides):
    values = {
        "schema_version": "1.0",
        "channel_id": 123,
        "channel_username": "daily",
        "channel_title": "Daily",
        "last_exported_message_id": 10,
        "last_exported_at": datetime(2026, 5, 8, 12, 0, tzinfo=timezone.utc),
        "message_count_total": 10,
        "media_count_total": 4,
        "downloaded_media_count_total": 2,
        "already_existing_media_count_total": 1,
        "skipped_media_count_total": 1,
        "skipped_by_size_count_total": 1,
        "skipped_by_type_count_total": 0,
        "failed_media_count_total": 0,
        "last_run_status": "completed",
        "updated_at": datetime(2026, 5, 8, 12, 1, tzinfo=timezone.utc),
        "date_from": datetime(2026, 5, 1, 9, 0, tzinfo=timezone.utc),
        "date_to": datetime(2026, 5, 2, 10, 0, tzinfo=timezone.utc),
        "last_manifest_path": "manifest.json",
    }
    values.update(overrides)
    return ChannelExportState(**values)


class TestChannelExportManifestCoordinator(unittest.TestCase):
    def test_build_manifest_without_discussion_preserves_summary_fields(self):
        manifest = build_channel_export_manifest(
            channel=ChannelIdentity(123, "Daily", "daily"),
            state=make_state(),
            options=make_options(),
            media_mode="metadata",
            discussion_result=None,
        )

        self.assertEqual(manifest["dataset_type"], "direct_channel_export")
        self.assertEqual(manifest["source"]["id"], 123)
        self.assertEqual(manifest["export"]["message_count"], 10)
        self.assertEqual(manifest["export"]["media_count"], 4)
        self.assertEqual(manifest["export"]["media_mode"], "metadata")
        self.assertEqual(manifest["discussion"], {"mode": "none"})
        self.assertNotIn(
            "discussion_comments.jsonl",
            manifest["export"]["included_files"],
        )

    def test_build_manifest_with_discussion_result_preserves_discussion_block(self):
        manifest = build_channel_export_manifest(
            channel=ChannelIdentity(123, "Daily", "daily"),
            state=make_state(),
            options=make_options(
                discussion_mode="full",
                max_comments_per_post=50,
            ),
            media_mode="metadata",
            discussion_result=FakeDiscussionResult(
                discussion_chat_id=222,
                thread_count=3,
                comment_count=9,
                failed_thread_count=1,
            ),
        )

        self.assertEqual(manifest["discussion"]["mode"], "full")
        self.assertEqual(manifest["discussion"]["discussion_chat_id"], 222)
        self.assertEqual(manifest["discussion"]["thread_count"], 3)
        self.assertEqual(manifest["discussion"]["comment_count"], 9)
        self.assertEqual(manifest["discussion"]["failed_thread_count"], 1)
        self.assertEqual(manifest["discussion"]["max_comments_per_post"], 50)
        self.assertIn(
            "discussion_threads.jsonl",
            manifest["discussion"]["included_files"],
        )
        self.assertIn(
            "discussion_export_state.json",
            manifest["export"]["included_files"],
        )

    def test_metadata_mode_keeps_media_options_in_manifest(self):
        manifest = build_channel_export_manifest(
            channel=ChannelIdentity(123, "Daily", "daily"),
            state=make_state(),
            options=make_options(media_types=("photo", "video")),
            media_mode="metadata",
        )

        self.assertEqual(manifest["export"]["media_mode"], "metadata")
        self.assertEqual(manifest["export"]["media_types"], ["photo", "video"])
        self.assertIsNone(manifest["export"]["max_media_size"])

    def test_full_media_mode_includes_media_directory_and_limits(self):
        manifest = build_channel_export_manifest(
            channel=ChannelIdentity(123, "Daily", "daily"),
            state=make_state(),
            options=make_options(
                media_mode="full",
                max_media_size=1024,
                media_types=("video",),
            ),
            media_mode="full",
        )

        self.assertEqual(manifest["export"]["media_mode"], "full")
        self.assertEqual(manifest["export"]["max_media_size"], 1024)
        self.assertEqual(manifest["export"]["media_types"], ["video"])
        self.assertIn("media/", manifest["export"]["included_files"])


if __name__ == "__main__":
    unittest.main()
