import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from tg_msg_manager.services.channel_export.manifest_writer import (
    ChannelManifestWriter,
    build_manifest,
)
from tg_msg_manager.services.channel_export.models import ChannelIdentity


class TestChannelExportManifest(unittest.TestCase):
    def test_build_manifest_contains_required_fields(self):
        manifest = build_manifest(
            channel=ChannelIdentity(
                channel_id=777,
                title="Updates",
                username="updates",
                access_hash=None,
            ),
            message_count=10,
            media_count=4,
            downloaded_media_count=0,
            already_existing_media_count=0,
            skipped_media_count=4,
            skipped_by_size_count=2,
            skipped_by_type_count=2,
            failed_media_count=1,
            date_from=datetime(2026, 5, 1, 9, 0, tzinfo=timezone.utc),
            date_to=datetime(2026, 5, 2, 10, 0, tzinfo=timezone.utc),
            media_mode="metadata",
            max_media_size=None,
            media_types=None,
            included_files=(
                "manifest.json",
                "messages.jsonl",
                "messages.txt",
                "media_manifest.jsonl",
            ),
        )

        self.assertEqual(manifest["dataset_type"], "direct_channel_export")
        self.assertEqual(manifest["schema_version"], "1.0")
        self.assertEqual(manifest["source"]["type"], "channel")
        self.assertEqual(manifest["source"]["id"], 777)
        self.assertEqual(manifest["source"]["username"], "updates")
        self.assertEqual(manifest["export"]["message_count"], 10)
        self.assertEqual(manifest["export"]["media_count"], 4)
        self.assertEqual(manifest["export"]["downloaded_media_count"], 0)
        self.assertEqual(manifest["export"]["already_existing_media_count"], 0)
        self.assertEqual(manifest["export"]["skipped_media_count"], 4)
        self.assertEqual(manifest["export"]["skipped_by_size_count"], 2)
        self.assertEqual(manifest["export"]["skipped_by_type_count"], 2)
        self.assertEqual(manifest["export"]["failed_media_count"], 1)
        self.assertEqual(
            manifest["export"]["date_from"],
            "2026-05-01T09:00:00+00:00",
        )
        self.assertEqual(
            manifest["export"]["date_to"],
            "2026-05-02T10:00:00+00:00",
        )
        self.assertEqual(manifest["export"]["media_mode"], "metadata")
        self.assertEqual(manifest["export"]["included_files"][0], "manifest.json")
        self.assertIn("jsonl", manifest["export"]["formats"])
        self.assertIn("txt", manifest["export"]["formats"])
        self.assertEqual(manifest["status"], "completed")
        self.assertIsInstance(manifest["exported_at"], str)

    def test_manifest_writer_writes_valid_json_file(self):
        manifest = build_manifest(
            channel=ChannelIdentity(
                channel_id=1,
                title=None,
                username=None,
                access_hash=None,
            ),
            message_count=1,
            media_count=0,
            downloaded_media_count=0,
            already_existing_media_count=0,
            skipped_media_count=0,
            skipped_by_size_count=0,
            skipped_by_type_count=0,
            failed_media_count=0,
            date_from=None,
            date_to=None,
            media_mode="none",
            max_media_size=None,
            media_types=None,
            included_files=("manifest.json",),
        )

        with tempfile.TemporaryDirectory(prefix="tg_channel_manifest_") as tmpdir:
            path = Path(tmpdir) / "manifest.json"
            ChannelManifestWriter().write(path, manifest)

            loaded = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(loaded["dataset_type"], "direct_channel_export")
            self.assertEqual(loaded["source"]["id"], 1)
            self.assertEqual(loaded["export"]["media_mode"], "none")


if __name__ == "__main__":
    unittest.main()
