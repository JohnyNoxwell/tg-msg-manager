import unittest
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from tg_msg_manager.services.channel_export.models import (
    ChannelExportOptions,
    ChannelExportPlan,
    ChannelExportRunStats,
    ChannelExportState,
    ChannelIdentity,
)
from tg_msg_manager.services.channel_export.result_builder import (
    build_channel_export_result,
)


@dataclass(frozen=True)
class FakeDiscussionResult:
    discussion_chat_id: int
    thread_count: int
    comment_count: int
    failed_thread_count: int
    comments_jsonl_path: Path
    comments_txt_path: Path
    threads_jsonl_path: Path
    state_path: Path


def make_plan(base: Path) -> ChannelExportPlan:
    return ChannelExportPlan(
        output_dir=base,
        manifest_path=base / "manifest.json",
        messages_jsonl_path=base / "messages.jsonl",
        messages_txt_path=base / "messages.txt",
        media_manifest_path=base / "media_manifest.jsonl",
        state_path=base / "channel_export_state.json",
        media_dir=base / "media",
        discussion_comments_jsonl_path=base / "discussion_comments.jsonl",
        discussion_comments_txt_path=base / "discussion_comments.txt",
        discussion_threads_jsonl_path=base / "discussion_threads.jsonl",
        discussion_metadata_jsonl_path=base / "discussion_metadata.jsonl",
        discussion_state_path=base / "discussion_export_state.json",
    )


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
    }
    values.update(overrides)
    return ChannelExportState(**values)


def make_run_stats(**overrides):
    values = {
        "mode": "incremental",
        "posts_exported": 2,
        "media_records_added": 3,
        "downloaded_media_count": 1,
        "already_existing_media_count": 1,
        "skipped_media_count": 1,
        "skipped_by_size_count": 1,
        "skipped_by_type_count": 0,
        "failed_media_count": 0,
        "date_from": None,
        "date_to": None,
        "last_exported_message_id": 10,
    }
    values.update(overrides)
    return ChannelExportRunStats(**values)


class TestChannelExportResultBuilder(unittest.TestCase):
    def test_build_result_without_discussion_preserves_channel_fields(self):
        base = Path("/exports/@daily__123")
        result = build_channel_export_result(
            channel=ChannelIdentity(123, "Daily", "daily"),
            plan=make_plan(base),
            options=ChannelExportOptions(
                channel="@daily",
                limit=None,
                media_mode="metadata",
                output_dir=Path("/exports"),
            ),
            run_mode="incremental",
            state=make_state(),
            run_stats=make_run_stats(),
            discussion_result=None,
        )

        self.assertEqual(result.channel.channel_id, 123)
        self.assertEqual(result.run_mode, "incremental")
        self.assertEqual(result.media_mode, "metadata")
        self.assertEqual(result.message_count, 10)
        self.assertEqual(result.media_count, 4)
        self.assertEqual(result.posts_exported_this_run, 2)
        self.assertEqual(result.media_records_added_this_run, 3)
        self.assertEqual(result.downloaded_media_count, 2)
        self.assertEqual(result.already_existing_media_count, 1)
        self.assertEqual(result.skipped_by_size_count_this_run, 1)
        self.assertEqual(result.manifest_path, base / "manifest.json")
        self.assertEqual(result.discussion_mode, "none")
        self.assertIsNone(result.discussion_chat_id)
        self.assertEqual(result.discussion_comment_count_this_run, 0)

    def test_build_result_with_discussion_preserves_discussion_fields(self):
        base = Path("/exports/@daily__123")
        discussion_result = FakeDiscussionResult(
            discussion_chat_id=222,
            thread_count=3,
            comment_count=9,
            failed_thread_count=1,
            comments_jsonl_path=base / "discussion_comments.jsonl",
            comments_txt_path=base / "discussion_comments.txt",
            threads_jsonl_path=base / "discussion_threads.jsonl",
            state_path=base / "discussion_export_state.json",
        )

        result = build_channel_export_result(
            channel=ChannelIdentity(123, "Daily", "daily"),
            plan=make_plan(base),
            options=ChannelExportOptions(
                channel="@daily",
                limit=None,
                media_mode="full",
                output_dir=Path("/exports"),
                max_media_size=1024,
                media_types=("photo",),
                discussion_mode="full",
            ),
            run_mode="force_full",
            state=make_state(),
            run_stats=make_run_stats(mode="force_full"),
            discussion_result=discussion_result,
        )

        self.assertEqual(result.media_mode, "full")
        self.assertEqual(result.max_media_size, 1024)
        self.assertEqual(result.media_types, ("photo",))
        self.assertEqual(result.discussion_mode, "full")
        self.assertEqual(result.discussion_chat_id, 222)
        self.assertEqual(result.discussion_thread_count_this_run, 3)
        self.assertEqual(result.discussion_comment_count_this_run, 9)
        self.assertEqual(result.failed_discussion_thread_count_this_run, 1)
        self.assertEqual(
            result.discussion_comments_jsonl_path,
            base / "discussion_comments.jsonl",
        )
        self.assertEqual(
            result.discussion_state_path,
            base / "discussion_export_state.json",
        )


if __name__ == "__main__":
    unittest.main()
