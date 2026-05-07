import tempfile
import unittest
from pathlib import Path

from tg_msg_manager.services.channel_export.plan_builder import (
    MEDIA_SUBDIRECTORIES,
    ChannelExportPlanBuilder,
    build_channel_directory_name,
    sanitize_path_part,
)
from tg_msg_manager.services.channel_export.models import ChannelIdentity


class TestChannelExportPlanBuilder(unittest.TestCase):
    def test_sanitize_path_part_removes_slashes_and_trims(self):
        self.assertEqual(
            sanitize_path_part("  News / Channel\\Name  "),
            "News__ChannelName",
        )

    def test_build_directory_name_uses_username(self):
        channel = ChannelIdentity(channel_id=123456, title="Ignored", username="news")

        self.assertEqual(build_channel_directory_name(channel), "@news__123456")

    def test_build_directory_name_uses_title_when_username_missing(self):
        channel = ChannelIdentity(
            channel_id=321,
            title="Daily News / UA",
            username=None,
        )

        self.assertEqual(
            build_channel_directory_name(channel),
            "Daily_News__UA__channel_321",
        )

    def test_build_directory_name_falls_back_when_identity_is_empty(self):
        channel = ChannelIdentity(channel_id=77, title=None, username=None)

        self.assertEqual(build_channel_directory_name(channel), "channel_77")

    def test_sanitize_path_part_truncates_long_titles(self):
        value = "A" * 200

        sanitized = sanitize_path_part(value)

        self.assertEqual(len(sanitized), 120)
        self.assertEqual(sanitized, "A" * 120)

    def test_plan_builder_creates_deterministic_paths_and_media_dirs(self):
        channel = ChannelIdentity(channel_id=987654321, title="Title", username="chan")

        with tempfile.TemporaryDirectory(prefix="tg_channel_plan_") as tmpdir:
            plan = ChannelExportPlanBuilder().build(Path(tmpdir), channel)

            self.assertEqual(plan.output_dir.name, "@chan__987654321")
            self.assertEqual(plan.manifest_path, plan.output_dir / "manifest.json")
            self.assertEqual(
                plan.messages_jsonl_path,
                plan.output_dir / "messages.jsonl",
            )
            self.assertEqual(plan.messages_txt_path, plan.output_dir / "messages.txt")
            self.assertEqual(
                plan.media_manifest_path,
                plan.output_dir / "media_manifest.jsonl",
            )
            self.assertTrue(plan.media_dir.is_dir())
            for subdirectory in MEDIA_SUBDIRECTORIES:
                self.assertTrue((plan.media_dir / subdirectory).is_dir())


if __name__ == "__main__":
    unittest.main()
