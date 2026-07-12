import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

from tg_msg_manager.services.channel_export.batch_discovery import (
    ChannelDatasetDiscovery,
)
from tg_msg_manager.services.channel_export.batch_models import (
    BATCH_STATUS_FAILED,
    BATCH_STATUS_NO_NEW_POSTS,
    BATCH_STATUS_UPDATED,
)
from tg_msg_manager.services.channel_export.batch_options import (
    ChannelBatchOptionsBuilder,
)
from tg_msg_manager.services.channel_export.batch_service import (
    ChannelBatchUpdateService,
)


def _write_dataset(
    root: Path,
    name: str,
    *,
    channel_id: int,
    username: str | None,
    media_mode: str = "metadata",
    discussion_mode: str = "none",
) -> Path:
    dataset_dir = root / name
    dataset_dir.mkdir()
    state = {
        "schema_version": "1.0",
        "channel_id": channel_id,
        "channel_username": username,
        "channel_title": name,
        "last_exported_message_id": 10,
        "last_exported_at": "2026-01-01T00:00:00+00:00",
        "message_count_total": 10,
        "media_count_total": 0,
        "downloaded_media_count_total": 0,
        "already_existing_media_count_total": 0,
        "skipped_media_count_total": 0,
        "skipped_by_size_count_total": 0,
        "skipped_by_type_count_total": 0,
        "failed_media_count_total": 0,
        "last_run_status": "completed",
        "updated_at": "2026-01-01T00:00:00+00:00",
        "date_from": None,
        "date_to": None,
        "last_manifest_path": "manifest.json",
    }
    discussion = {"mode": discussion_mode}
    if discussion_mode == "full":
        discussion["max_comments_per_post"] = 25
    manifest = {
        "dataset_type": "direct_channel_export",
        "schema_version": "1.0",
        "source": {
            "type": "channel",
            "id": channel_id,
            "username": username,
            "title": name,
        },
        "export": {
            "media_mode": media_mode,
            "max_media_size": 1024 if media_mode == "full" else None,
            "media_types": ["photo"] if media_mode == "full" else None,
            "included_files": ["messages.jsonl", "media_manifest.jsonl"],
        },
        "discussion": discussion,
        "status": "completed",
    }
    (dataset_dir / "channel_export_state.json").write_text(
        json.dumps(state), encoding="utf-8"
    )
    (dataset_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return dataset_dir


class TestChannelDatasetDiscovery(unittest.TestCase):
    def test_empty_or_missing_root_has_no_candidates(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self.assertEqual(ChannelDatasetDiscovery().discover(root), ())
            self.assertEqual(ChannelDatasetDiscovery().discover(root / "missing"), ())

    def test_candidates_are_sorted_and_unrelated_directories_are_ignored(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "z").mkdir()
            (root / "z" / "channel_export_state.json").touch()
            (root / "a").mkdir()
            (root / "a" / "manifest.json").touch()
            (root / "unrelated").mkdir()

            result = ChannelDatasetDiscovery().discover(root)

            self.assertEqual([path.name for path in result], ["a", "z"])


class TestChannelBatchOptionsBuilder(unittest.TestCase):
    def test_reconstructs_options_and_uses_username(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            dataset = _write_dataset(
                root,
                "channel",
                channel_id=11,
                username="example",
                media_mode="full",
                discussion_mode="full",
            )

            options = ChannelBatchOptionsBuilder().build(dataset, root=root)

            self.assertEqual(options.channel, "@example")
            self.assertEqual(options.output_dir, root)
            self.assertEqual(options.media_mode, "full")
            self.assertEqual(options.max_media_size, 1024)
            self.assertEqual(options.media_types, ("photo",))
            self.assertEqual(options.discussion_mode, "full")
            self.assertEqual(options.max_comments_per_post, 25)
            self.assertTrue(options.include_jsonl)
            self.assertFalse(options.include_txt)
            self.assertIsNone(options.limit)
            self.assertFalse(options.force)

    def test_uses_numeric_id_and_default_for_non_full_discussion(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            dataset = _write_dataset(root, "channel", channel_id=22, username=None)

            options = ChannelBatchOptionsBuilder().build(dataset, root=root)

            self.assertEqual(options.channel, "22")
            self.assertEqual(options.max_comments_per_post, 100)

    def test_rejects_missing_manifest(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            dataset = root / "broken"
            dataset.mkdir()
            (dataset / "channel_export_state.json").touch()

            with self.assertRaisesRegex(ValueError, "requires"):
                ChannelBatchOptionsBuilder().build(dataset, root=root)


class TestChannelBatchUpdateService(unittest.IsolatedAsyncioTestCase):
    async def test_updates_sequentially_and_isolates_failures(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_dataset(root, "a", channel_id=1, username="a")
            _write_dataset(root, "b", channel_id=2, username="b")
            _write_dataset(root, "c", channel_id=3, username="c")
            exporter = SimpleNamespace(
                export_channel=AsyncMock(
                    side_effect=[
                        SimpleNamespace(posts_exported_this_run=2),
                        RuntimeError("unavailable"),
                        SimpleNamespace(posts_exported_this_run=0),
                    ]
                )
            )

            result = await ChannelBatchUpdateService(
                channel_exporter=exporter
            ).update_all(root)

            self.assertEqual(
                [item.status for item in result.items],
                [BATCH_STATUS_UPDATED, BATCH_STATUS_FAILED, BATCH_STATUS_NO_NEW_POSTS],
            )
            self.assertEqual(
                [
                    call.args[0].channel
                    for call in exporter.export_channel.await_args_list
                ],
                ["@a", "@b", "@c"],
            )
            self.assertEqual(result.updated_count, 1)
            self.assertEqual(result.no_new_posts_count, 1)
            self.assertEqual(result.failed_count, 1)
            self.assertEqual(result.items[1].error, "unavailable")

    async def test_malformed_candidate_does_not_block_valid_dataset(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            broken = root / "a-broken"
            broken.mkdir()
            (broken / "manifest.json").touch()
            _write_dataset(root, "b-valid", channel_id=2, username="valid")
            exporter = SimpleNamespace(
                export_channel=AsyncMock(
                    return_value=SimpleNamespace(posts_exported_this_run=1)
                )
            )

            result = await ChannelBatchUpdateService(
                channel_exporter=exporter
            ).update_all(root)

            self.assertEqual(result.failed_count, 1)
            self.assertEqual(result.updated_count, 1)
            exporter.export_channel.assert_awaited_once()
