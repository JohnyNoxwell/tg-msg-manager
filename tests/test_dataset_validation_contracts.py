import json
import shutil
import sys
import tempfile
import unittest
from argparse import Namespace
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from typing import Optional
from unittest.mock import AsyncMock, MagicMock, patch

from tg_msg_manager.cli import _command_needs_client, run_cli
from tg_msg_manager.cli_commands import _handle_validate_dataset_command
from tg_msg_manager.cli_parser import build_cli_parser
from tg_msg_manager.core.config import Settings
from tg_msg_manager.core.runtime import AppPaths, AppRuntime
from tg_msg_manager.services.dataset_validation import (
    DatasetInspectionOptions,
    DatasetValidationOptions,
    inspect_dataset,
    render_inspection_report_json,
    render_inspection_report_markdown,
    render_validation_report_json,
    render_validation_report_markdown,
    validate_dataset,
)

FIXTURES = Path(__file__).parent / "fixtures" / "dataset_validation"


def fixture_path(name: str) -> Path:
    return FIXTURES / name


def issue_codes(report) -> set[str]:
    return {issue.code for issue in report.issues}


class TestDatasetValidationContracts(unittest.TestCase):
    def test_valid_minimal_fixture_validates_ok(self):
        report = validate_dataset(
            DatasetValidationOptions(fixture_path("valid_minimal_channel_dataset"))
        )

        self.assertEqual(report.status, "ok")
        self.assertEqual(report.summary["messages"]["count"], 1)
        self.assertEqual(report.summary["media"]["record_count"], 0)

    def test_duplicate_messages_fixture_reports_error(self):
        report = validate_dataset(
            DatasetValidationOptions(fixture_path("invalid_duplicate_messages"))
        )

        self.assertEqual(report.status, "errors")
        self.assertIn("duplicate_message_id", issue_codes(report))

    def test_invalid_jsonl_fixture_reports_line_number(self):
        report = validate_dataset(
            DatasetValidationOptions(fixture_path("invalid_bad_jsonl"))
        )

        self.assertEqual(report.status, "errors")
        invalid = [issue for issue in report.issues if issue.code == "invalid_jsonl"]
        self.assertEqual(invalid[0].line, 2)

    def test_missing_downloaded_media_fixture_reports_error(self):
        report = validate_dataset(
            DatasetValidationOptions(fixture_path("invalid_missing_media_file"))
        )

        self.assertEqual(report.status, "errors")
        self.assertIn("media_file_missing", issue_codes(report))

    def test_valid_discussion_fixture_validates_ok(self):
        report = validate_dataset(
            DatasetValidationOptions(fixture_path("valid_discussion_dataset"))
        )

        self.assertEqual(report.status, "ok")
        self.assertEqual(report.summary["discussions"]["comment_count"], 1)
        self.assertEqual(report.summary["discussions"]["thread_count"], 1)

    def test_partial_discussion_fixture_reports_warning(self):
        report = validate_dataset(
            DatasetValidationOptions(fixture_path("partial_discussion_dataset"))
        )

        self.assertEqual(report.status, "warnings")
        self.assertIn("discussion_payload_without_state", issue_codes(report))

    def test_renderers_emit_deterministic_json_and_required_markdown_sections(self):
        validation = validate_dataset(
            DatasetValidationOptions(fixture_path("valid_minimal_channel_dataset"))
        )
        inspection = inspect_dataset(
            DatasetInspectionOptions(fixture_path("valid_minimal_channel_dataset"))
        )

        validation_json = json.loads(render_validation_report_json(validation))
        inspection_json = json.loads(render_inspection_report_json(inspection))
        validation_md = render_validation_report_markdown(validation)
        inspection_md = render_inspection_report_markdown(inspection)

        self.assertEqual(validation_json["status"], "ok")
        self.assertEqual(inspection_json["messages"]["count"], 1)
        for section in (
            "## Status",
            "## Dataset Path",
            "## Files Checked",
            "## Errors",
            "## Warnings",
            "## Summary",
        ):
            self.assertIn(section, validation_md)
        for section in (
            "## Dataset Path",
            "## Files",
            "## Messages",
            "## Media",
            "## Discussions",
            "## State",
            "## Notes",
        ):
            self.assertIn(section, inspection_md)


class TestDatasetValidationMediaRelationships(unittest.TestCase):
    def _copy_minimal_fixture(self, tmpdir: str) -> Path:
        target = Path(tmpdir) / "dataset"
        shutil.copytree(fixture_path("valid_minimal_channel_dataset"), target)
        return target

    def test_downloaded_media_with_existing_file_is_ok(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset = self._copy_minimal_fixture(tmpdir)
            media_path = dataset / "media" / "photos" / "existing.jpg"
            media_path.parent.mkdir(parents=True)
            media_path.write_text("bytes", encoding="utf-8")
            self._write_media_manifest(
                dataset, "downloaded", "media/photos/existing.jpg"
            )
            self._patch_manifest_media_counts(dataset, media_count=1, downloaded=1)

            report = validate_dataset(DatasetValidationOptions(dataset))

        self.assertEqual(report.status, "ok")

    def test_failed_media_is_warning_not_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset = self._copy_minimal_fixture(tmpdir)
            self._write_media_manifest(dataset, "failed", None)
            self._patch_manifest_media_counts(dataset, media_count=1, failed=1)

            report = validate_dataset(DatasetValidationOptions(dataset))

        self.assertEqual(report.status, "warnings")
        self.assertIn("failed_media_records_present", issue_codes(report))

    def test_skipped_media_does_not_require_file(self):
        for status in ("skipped_by_size", "skipped_by_type"):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as tmpdir:
                dataset = self._copy_minimal_fixture(tmpdir)
                self._write_media_manifest(dataset, status, None)
                self._patch_manifest_media_counts(dataset, media_count=1)

                report = validate_dataset(DatasetValidationOptions(dataset))

            self.assertNotIn("media_file_missing", issue_codes(report))

    def test_unknown_media_status_warns(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset = self._copy_minimal_fixture(tmpdir)
            self._write_media_manifest(dataset, "new_status", None)
            self._patch_manifest_media_counts(dataset, media_count=1)

            report = validate_dataset(DatasetValidationOptions(dataset))

        self.assertEqual(report.status, "warnings")
        self.assertIn("unknown_media_status", issue_codes(report))

    def test_media_path_traversal_is_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset = self._copy_minimal_fixture(tmpdir)
            self._write_media_manifest(dataset, "downloaded", "../outside.jpg")
            self._patch_manifest_media_counts(dataset, media_count=1, downloaded=1)

            report = validate_dataset(DatasetValidationOptions(dataset))

        self.assertEqual(report.status, "errors")
        self.assertIn("media_path_escape", issue_codes(report))

    def _write_media_manifest(
        self,
        dataset: Path,
        status: str,
        final_path: Optional[str],
    ) -> None:
        record = {
            "media_id": "1_01",
            "message_id": 1,
            "media_index": 1,
            "media_type": "photo",
            "mime_type": "image/jpeg",
            "file_name": "photo.jpg",
            "file_size": 4,
            "width": 10,
            "height": 10,
            "duration": None,
            "local_path": final_path,
            "sha256": None,
            "download_status": status,
            "error": "boom" if status == "failed" else None,
            "original_filename": "photo.jpg",
            "detected_extension": ".jpg",
            "filename_strategy": "original_filename",
            "final_filename": "photo.jpg",
            "final_path": final_path,
        }
        (dataset / "media_manifest.jsonl").write_text(
            json.dumps(record, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def _patch_manifest_media_counts(
        self,
        dataset: Path,
        *,
        media_count: int,
        downloaded: int = 0,
        failed: int = 0,
    ) -> None:
        path = dataset / "manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["export"]["media_count"] = media_count
        manifest["export"]["downloaded_media_count"] = downloaded
        manifest["export"]["failed_media_count"] = failed
        manifest["export"]["included_files"].append("media/")
        path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
        )
        state_path = dataset / "channel_export_state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["media_count_total"] = media_count
        state["downloaded_media_count_total"] = downloaded
        state["failed_media_count_total"] = failed
        state_path.write_text(
            json.dumps(state, indent=2, sort_keys=True), encoding="utf-8"
        )


class TestDatasetValidationDiscussionRelationships(unittest.TestCase):
    def test_no_discussion_files_is_valid_absent_discussion(self):
        report = validate_dataset(
            DatasetValidationOptions(fixture_path("valid_minimal_channel_dataset"))
        )

        self.assertFalse(report.summary["discussions"]["present"])
        self.assertEqual(report.status, "ok")

    def test_invalid_discussion_comments_jsonl_is_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset = Path(tmpdir) / "dataset"
            shutil.copytree(fixture_path("valid_discussion_dataset"), dataset)
            (dataset / "discussion_comments.jsonl").write_text(
                "{bad\n", encoding="utf-8"
            )

            report = validate_dataset(DatasetValidationOptions(dataset))

        self.assertEqual(report.status, "errors")
        self.assertIn("invalid_discussion_comments_jsonl", issue_codes(report))

    def test_invalid_discussion_threads_jsonl_is_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset = Path(tmpdir) / "dataset"
            shutil.copytree(fixture_path("valid_discussion_dataset"), dataset)
            (dataset / "discussion_threads.jsonl").write_text(
                "{bad\n", encoding="utf-8"
            )

            report = validate_dataset(DatasetValidationOptions(dataset))

        self.assertEqual(report.status, "errors")
        self.assertIn("invalid_discussion_threads_jsonl", issue_codes(report))

    def test_unlinked_discussion_comment_warns(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset = Path(tmpdir) / "dataset"
            shutil.copytree(fixture_path("valid_discussion_dataset"), dataset)
            comment = json.loads((dataset / "discussion_comments.jsonl").read_text())
            comment["channel_message_id"] = 999
            (dataset / "discussion_comments.jsonl").write_text(
                json.dumps(comment, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            report = validate_dataset(DatasetValidationOptions(dataset))

        self.assertEqual(report.status, "warnings")
        self.assertIn("discussion_comment_unlinked", issue_codes(report))

    def test_duplicate_discussion_comment_id_is_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset = Path(tmpdir) / "dataset"
            shutil.copytree(fixture_path("valid_discussion_dataset"), dataset)
            comment = (dataset / "discussion_comments.jsonl").read_text(
                encoding="utf-8"
            )
            (dataset / "discussion_comments.jsonl").write_text(
                comment + comment, encoding="utf-8"
            )

            report = validate_dataset(DatasetValidationOptions(dataset))

        self.assertEqual(report.status, "errors")
        self.assertIn("duplicate_discussion_comment_id", issue_codes(report))


class TestDatasetValidationCLI(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.runtime = AppRuntime(
            settings=Settings(api_id=1, api_hash="hash", db_path="messages.db"),
            paths=AppPaths(
                project_root="/tmp/tg-msg-manager",
                config_path="/tmp/tg-msg-manager/config.json",
                db_path="/tmp/tg-msg-manager/messages.db",
                lock_path="/tmp/tg-msg-manager/.tg_msg_manager.lock",
                logs_dir="/tmp/tg-msg-manager/LOGS",
                db_exports_dir="/tmp/tg-msg-manager/DB_EXPORTS",
                private_dialogs_dir="/tmp/tg-msg-manager/PRIVAT_DIALOGS",
                public_groups_dir="/tmp/tg-msg-manager/PUBLIC_GROUPS",
                channel_exports_dir="/tmp/tg-msg-manager/exports/channels",
            ),
            python_executable="/usr/bin/python3",
        )

    def test_parser_help_and_required_path(self):
        parser = build_cli_parser()
        self.assertIn("validate-dataset", parser.format_help())
        self.assertIn("inspect-dataset", parser.format_help())
        with self.assertRaises(SystemExit):
            parser.parse_args(["validate-dataset"])
        with self.assertRaises(SystemExit):
            parser.parse_args(["inspect-dataset"])

    async def test_run_cli_validate_dataset_does_not_initialize_context(self):
        mock_ctx = MagicMock()
        mock_ctx.initialize = AsyncMock()
        mock_ctx.shutdown = AsyncMock()

        with (
            patch("tg_msg_manager.cli.CLIContext", return_value=mock_ctx) as mock_cls,
            patch.object(
                sys,
                "argv",
                [
                    "prog",
                    "validate-dataset",
                    "--path",
                    str(fixture_path("valid_minimal_channel_dataset")),
                ],
            ),
            patch(
                "tg_msg_manager.cli._handle_validate_dataset_command",
                new_callable=AsyncMock,
            ) as mock_handler,
        ):
            await run_cli(runtime=self.runtime)

        mock_cls.assert_not_called()
        self.assertFalse(_command_needs_client("validate-dataset"))
        mock_handler.assert_awaited_once()

    async def test_validate_dataset_handler_exits_one_for_errors(self):
        args = Namespace(
            path=str(fixture_path("invalid_duplicate_messages")),
            json=False,
        )
        with redirect_stdout(StringIO()), self.assertRaises(SystemExit) as raised:
            await _handle_validate_dataset_command(MagicMock(), args)

        self.assertEqual(raised.exception.code, 1)
