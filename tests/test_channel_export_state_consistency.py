import json
import tempfile
import unittest
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from tg_msg_manager.services.channel_export.discussions.errors import (
    ChannelDiscussionStateError,
)
from tg_msg_manager.services.channel_export.discussions.exporter import (
    ChannelDiscussionExporter,
)
from tg_msg_manager.services.channel_export.discussions.models import (
    DISCUSSION_SOURCE_STATUS_RESOLVED,
    ChannelDiscussionExportState,
    ChannelDiscussionOptions,
    ChannelDiscussionSource,
)
from tg_msg_manager.services.channel_export.discussions.state_manager import (
    ChannelDiscussionStateManager,
)
from tg_msg_manager.services.channel_export.errors import ChannelExportStateError
from tg_msg_manager.services.channel_export.models import (
    ChannelExportPlan,
    ChannelExportState,
    ChannelIdentity,
)
from tg_msg_manager.services.channel_export.state_consistency import (
    validate_channel_state_for_incremental,
    validate_discussion_state_for_incremental,
)
from tg_msg_manager.services.channel_export.state_manager import (
    ChannelExportStateManager,
)


class UnusedDiscussionFetcher:
    async def fetch_comments_for_post(self, **kwargs):
        del kwargs
        raise AssertionError("fetch should not run for invalid previous state")


def make_channel_state(**overrides) -> ChannelExportState:
    now = datetime(2026, 5, 8, 12, 0, tzinfo=timezone.utc)
    values = {
        "schema_version": "1.0",
        "channel_id": 111,
        "channel_username": "daily",
        "channel_title": "Daily",
        "last_exported_message_id": 10,
        "last_exported_at": now,
        "message_count_total": 10,
        "media_count_total": 3,
        "downloaded_media_count_total": 1,
        "already_existing_media_count_total": 1,
        "skipped_media_count_total": 1,
        "skipped_by_size_count_total": 1,
        "skipped_by_type_count_total": 0,
        "failed_media_count_total": 0,
        "last_run_status": "completed",
        "updated_at": now,
        "date_from": now,
        "date_to": now,
        "last_manifest_path": "manifest.json",
    }
    values.update(overrides)
    return ChannelExportState(**values)


def make_discussion_state(**overrides) -> ChannelDiscussionExportState:
    now = datetime(2026, 5, 8, 12, 0, tzinfo=timezone.utc)
    values = {
        "schema_version": "1.0",
        "channel_id": 111,
        "discussion_chat_id": 222,
        "last_run_at": now,
        "thread_count_total": 2,
        "comment_count_total": 5,
        "failed_thread_count_total": 1,
        "last_run_status": "completed",
        "updated_at": now,
    }
    values.update(overrides)
    return ChannelDiscussionExportState(**values)


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
        discussion_state_path=base / "discussion_export_state.json",
    )


class TestChannelExportStateConsistency(unittest.IsolatedAsyncioTestCase):
    def test_channel_incremental_state_must_be_monotonic(self):
        previous = make_channel_state()
        current = make_channel_state(
            last_exported_message_id=12,
            message_count_total=12,
            media_count_total=4,
        )

        validate_channel_state_for_incremental(previous, current)

        backwards = replace(current, message_count_total=9)
        with self.assertRaises(ChannelExportStateError):
            validate_channel_state_for_incremental(previous, backwards)

        cursor_backwards = replace(current, last_exported_message_id=9)
        with self.assertRaises(ChannelExportStateError):
            validate_channel_state_for_incremental(previous, cursor_backwards)

    def test_discussion_incremental_state_must_be_monotonic(self):
        previous = make_discussion_state()
        current = make_discussion_state(thread_count_total=3, comment_count_total=8)

        validate_discussion_state_for_incremental(previous, current)

        backwards = replace(current, comment_count_total=4)
        with self.assertRaises(ChannelDiscussionStateError):
            validate_discussion_state_for_incremental(previous, backwards)

    def test_state_managers_reject_negative_counters_on_load(self):
        with tempfile.TemporaryDirectory(prefix="tg_state_consistency_") as tmpdir:
            channel_path = Path(tmpdir) / "channel_export_state.json"
            channel_payload = ChannelExportStateManager().to_dict(make_channel_state())
            channel_payload["message_count_total"] = -1
            channel_path.write_text(json.dumps(channel_payload), encoding="utf-8")

            with self.assertRaises(ChannelExportStateError):
                ChannelExportStateManager().load(channel_path)

            discussion_path = Path(tmpdir) / "discussion_export_state.json"
            discussion_payload = ChannelDiscussionStateManager().to_dict(
                make_discussion_state()
            )
            discussion_payload["comment_count_total"] = -1
            discussion_path.write_text(json.dumps(discussion_payload), encoding="utf-8")

            with self.assertRaises(ChannelDiscussionStateError):
                ChannelDiscussionStateManager().load(discussion_path)

    async def test_discussion_exporter_rejects_previous_state_for_wrong_channel(self):
        with tempfile.TemporaryDirectory(
            prefix="tg_discussion_state_mismatch_"
        ) as tmpdir:
            exporter = ChannelDiscussionExporter(fetcher=UnusedDiscussionFetcher())
            with self.assertRaises(ChannelDiscussionStateError):
                await exporter.export_for_posts(
                    channel_identity=ChannelIdentity(111, "Daily", "daily"),
                    discussion_source=ChannelDiscussionSource(
                        status=DISCUSSION_SOURCE_STATUS_RESOLVED,
                        discussion_chat_id=222,
                        discussion_entity=object(),
                    ),
                    posts=(),
                    plan=make_plan(Path(tmpdir)),
                    discussion_options=ChannelDiscussionOptions(mode="full"),
                    run_mode="incremental",
                    previous_state=make_discussion_state(channel_id=999),
                )

    async def test_discussion_exporter_rejects_previous_state_for_wrong_discussion(
        self,
    ):
        with tempfile.TemporaryDirectory(
            prefix="tg_discussion_chat_mismatch_"
        ) as tmpdir:
            exporter = ChannelDiscussionExporter(fetcher=UnusedDiscussionFetcher())
            with self.assertRaises(ChannelDiscussionStateError):
                await exporter.export_for_posts(
                    channel_identity=ChannelIdentity(111, "Daily", "daily"),
                    discussion_source=ChannelDiscussionSource(
                        status=DISCUSSION_SOURCE_STATUS_RESOLVED,
                        discussion_chat_id=222,
                        discussion_entity=object(),
                    ),
                    posts=(),
                    plan=make_plan(Path(tmpdir)),
                    discussion_options=ChannelDiscussionOptions(mode="full"),
                    run_mode="incremental",
                    previous_state=make_discussion_state(discussion_chat_id=999),
                )

    def test_state_managers_reject_non_completed_status_on_save(self):
        with tempfile.TemporaryDirectory(prefix="tg_state_status_") as tmpdir:
            with self.assertRaises(ChannelExportStateError):
                ChannelExportStateManager().save(
                    Path(tmpdir) / "channel_export_state.json",
                    make_channel_state(last_run_status="failed"),
                )

            with self.assertRaises(ChannelDiscussionStateError):
                ChannelDiscussionStateManager().save(
                    Path(tmpdir) / "discussion_export_state.json",
                    make_discussion_state(last_run_status="failed"),
                )


if __name__ == "__main__":
    unittest.main()
