import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from tg_msg_manager.services.channel_export.discussions.errors import (
    ChannelDiscussionStateError,
)
from tg_msg_manager.services.channel_export.discussions.models import (
    ChannelDiscussionRunStats,
)
from tg_msg_manager.services.channel_export.discussions.state_manager import (
    ChannelDiscussionStateManager,
)


class TestChannelDiscussionStateManager(unittest.TestCase):
    def test_writes_and_loads_state_json(self):
        manager = ChannelDiscussionStateManager()
        stats = ChannelDiscussionRunStats(
            mode="full",
            thread_count=2,
            comment_count=5,
            failed_thread_count=1,
        )
        state = manager.build_completed_state(
            channel=SimpleNamespace(channel_id=111),
            discussion_chat_id=222,
            stats=stats,
        )

        with tempfile.TemporaryDirectory(prefix="tg_discussion_state_") as tmpdir:
            path = Path(tmpdir) / "discussion_export_state.json"
            manager.save(path, state)
            loaded = manager.load(path)

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.channel_id, 111)
        self.assertEqual(loaded.comment_count_total, 5)

    def test_incremental_totals_are_merged(self):
        manager = ChannelDiscussionStateManager()
        previous = manager.build_completed_state(
            channel=SimpleNamespace(channel_id=111),
            discussion_chat_id=222,
            stats=ChannelDiscussionRunStats(
                mode="full",
                thread_count=2,
                comment_count=5,
                failed_thread_count=1,
            ),
        )

        merged = manager.build_completed_state(
            channel=SimpleNamespace(channel_id=111),
            discussion_chat_id=222,
            stats=ChannelDiscussionRunStats(
                mode="incremental",
                thread_count=1,
                comment_count=3,
                failed_thread_count=0,
            ),
            previous_state=previous,
        )

        self.assertEqual(merged.thread_count_total, 3)
        self.assertEqual(merged.comment_count_total, 8)
        self.assertEqual(merged.failed_thread_count_total, 1)

    def test_force_or_full_totals_are_rebuilt(self):
        manager = ChannelDiscussionStateManager()
        previous = manager.build_completed_state(
            channel=SimpleNamespace(channel_id=111),
            discussion_chat_id=222,
            stats=ChannelDiscussionRunStats(
                mode="full",
                thread_count=10,
                comment_count=50,
                failed_thread_count=5,
            ),
        )

        rebuilt = manager.build_completed_state(
            channel=SimpleNamespace(channel_id=111),
            discussion_chat_id=222,
            stats=ChannelDiscussionRunStats(
                mode="force_full",
                thread_count=1,
                comment_count=2,
                failed_thread_count=0,
            ),
            previous_state=previous,
        )

        self.assertEqual(rebuilt.thread_count_total, 1)
        self.assertEqual(rebuilt.comment_count_total, 2)
        self.assertEqual(rebuilt.failed_thread_count_total, 0)

    def test_corrupted_state_raises_domain_error(self):
        with tempfile.TemporaryDirectory(prefix="tg_discussion_state_bad_") as tmpdir:
            path = Path(tmpdir) / "discussion_export_state.json"
            path.write_text("{not json", encoding="utf-8")

            with self.assertRaises(ChannelDiscussionStateError):
                ChannelDiscussionStateManager().load(path)

    def test_loads_iso_datetime_fields(self):
        payload = {
            "schema_version": "1.0",
            "channel_id": 111,
            "discussion_chat_id": 222,
            "last_run_at": "2026-05-08T12:00:00+00:00",
            "thread_count_total": 1,
            "comment_count_total": 2,
            "failed_thread_count_total": 0,
            "last_run_status": "completed",
            "updated_at": "2026-05-08T12:01:00+00:00",
        }

        with tempfile.TemporaryDirectory(prefix="tg_discussion_state_iso_") as tmpdir:
            path = Path(tmpdir) / "discussion_export_state.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            loaded = ChannelDiscussionStateManager().load(path)

        self.assertEqual(
            loaded.last_run_at,
            datetime(2026, 5, 8, 12, 0, tzinfo=timezone.utc),
        )


if __name__ == "__main__":
    unittest.main()
