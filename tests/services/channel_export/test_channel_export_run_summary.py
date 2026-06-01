import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tg_msg_manager.services.channel_export.run_changelog import (
    ChannelRunChangelogWriter,
)
from tg_msg_manager.services.channel_export.run_summary import ChannelRunSummaryBuilder


ARTIFACT_PATHS = {
    "manifest": "manifest.json",
    "messages_jsonl": "messages.jsonl",
    "messages_txt": "messages.txt",
    "media_manifest": "media_manifest.jsonl",
    "state": "channel_export_state.json",
    "run_changelog": "run_changelog.jsonl",
}


class FixedUuid:
    hex = "fixed-run-id"


class FrozenDateTime:
    @staticmethod
    def now(tz):
        return datetime(2026, 5, 30, 12, 0, tzinfo=tz)


def make_post(message_id: int, timestamp: datetime):
    return SimpleNamespace(message_id=message_id, timestamp=timestamp)


class TestChannelRunSummary(unittest.TestCase):
    def test_summary_records_changelog_facts(self):
        first = datetime(2026, 5, 7, 10, 0, tzinfo=timezone.utc)
        second = datetime(2026, 5, 7, 11, 0, tzinfo=timezone.utc)
        builder = ChannelRunSummaryBuilder()

        builder.record(make_post(1, first))
        builder.record(make_post(2, second))
        summary = builder.build()

        self.assertEqual(summary.message_ids, (1, 2))
        self.assertEqual(summary.first_message_id, 1)
        self.assertEqual(summary.last_message_id, 2)
        self.assertEqual(summary.first_message_timestamp, first)
        self.assertEqual(summary.last_message_timestamp, second)
        self.assertEqual(summary.message_count, 2)

    def test_changelog_summary_output_matches_posts_output(self):
        first = datetime(2026, 5, 7, 10, 0, tzinfo=timezone.utc)
        second = datetime(2026, 5, 7, 11, 0, tzinfo=timezone.utc)
        posts = (make_post(1, first), make_post(2, second))
        builder = ChannelRunSummaryBuilder()
        for post in posts:
            builder.record(post)

        channel = SimpleNamespace(
            channel_id=123,
            username="daily",
            title="Daily",
        )
        previous_state = None
        new_state = SimpleNamespace(last_exported_message_id=2)
        run_stats = SimpleNamespace(posts_exported=2)

        with tempfile.TemporaryDirectory(prefix="tg_channel_summary_") as tmpdir:
            posts_dir = Path(tmpdir) / "posts"
            summary_dir = Path(tmpdir) / "summary"
            posts_dir.mkdir()
            summary_dir.mkdir()
            writer = ChannelRunChangelogWriter()

            with (
                patch(
                    "tg_msg_manager.services.channel_export.run_changelog.uuid.uuid4",
                    return_value=FixedUuid(),
                ),
                patch(
                    "tg_msg_manager.services.channel_export.run_changelog.datetime",
                    FrozenDateTime,
                ),
            ):
                writer.append_entry(
                    output_dir=posts_dir,
                    channel=channel,
                    run_mode="full",
                    previous_state=previous_state,
                    new_state=new_state,
                    run_stats=run_stats,
                    posts=posts,
                    artifact_paths=ARTIFACT_PATHS,
                )
                writer.append_entry(
                    output_dir=summary_dir,
                    channel=channel,
                    run_mode="full",
                    previous_state=previous_state,
                    new_state=new_state,
                    run_stats=run_stats,
                    posts=(),
                    artifact_paths=ARTIFACT_PATHS,
                    summary=builder.build(),
                )

            posts_text = (posts_dir / "run_changelog.jsonl").read_text(encoding="utf-8")
            summary_text = (summary_dir / "run_changelog.jsonl").read_text(
                encoding="utf-8"
            )
            self.assertEqual(summary_text, posts_text)
            payload = json.loads(summary_text)
            self.assertEqual(payload["new_message_ids"], [1, 2])
            self.assertEqual(payload["first_new_message_id"], 1)
            self.assertEqual(payload["last_new_message_date"], second.isoformat())


if __name__ == "__main__":
    unittest.main()
