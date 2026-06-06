import sys
import unittest
from argparse import Namespace
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from unittest.mock import AsyncMock, MagicMock, patch

from tg_msg_manager.cli import run_cli
from tg_msg_manager.cli.commands.target_names import _handle_target_command
from tg_msg_manager.cli_parser import build_cli_parser
from tg_msg_manager.core.config import Settings
from tg_msg_manager.core.runtime import AppPaths, AppRuntime
from tg_msg_manager.infrastructure.storage.records import (
    TargetNameResolutionRecord,
    TargetNameSnapshotRecord,
    TargetNameTargetRecord,
)


class TestTargetNamesCLI(unittest.IsolatedAsyncioTestCase):
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

    def test_parser_accepts_target_names_defaults(self):
        parser = build_cli_parser()

        args = parser.parse_args(["target", "names", "1001"])

        self.assertEqual(args.command, "target")
        self.assertEqual(args.target_command, "names")
        self.assertEqual(args.target, "1001")
        self.assertEqual(args.field, "all")
        self.assertEqual(args.format, "text")

    def test_parser_rejects_invalid_field_and_format(self):
        parser = build_cli_parser()

        with self.assertRaises(SystemExit):
            parser.parse_args(["target", "names", "1001", "--field", "invalid"])
        with self.assertRaises(SystemExit):
            parser.parse_args(["target", "names", "1001", "--format", "yaml"])

    @patch("tg_msg_manager.cli.SQLiteStorage")
    @patch("tg_msg_manager.cli._handle_target_command", new_callable=AsyncMock)
    @patch("tg_msg_manager.cli.CLIContext")
    async def test_run_cli_target_names_uses_local_only_context(
        self, mock_ctx_cls, mock_target_handler, mock_storage_cls
    ):
        mock_storage = MagicMock()
        mock_storage.close = AsyncMock()
        mock_storage_cls.return_value = mock_storage

        with patch.object(sys, "argv", ["prog", "target", "names", "1001"]):
            await run_cli(runtime=self.runtime)

        mock_ctx_cls.assert_not_called()
        mock_storage_cls.assert_called_once_with(self.runtime.paths.db_path)
        mock_storage.close.assert_awaited_once()
        mock_target_handler.assert_awaited_once()

    @patch("tg_msg_manager.cli.SQLiteStorage")
    @patch("tg_msg_manager.cli._handle_target_command", new_callable=AsyncMock)
    @patch("tg_msg_manager.cli.build_app_runtime")
    async def test_run_cli_target_names_builds_runtime_without_api_credentials(
        self, mock_build_runtime, mock_target_handler, mock_storage_cls
    ):
        mock_build_runtime.return_value = self.runtime
        mock_storage = MagicMock()
        mock_storage.close = AsyncMock()
        mock_storage_cls.return_value = mock_storage

        with patch.object(sys, "argv", ["prog", "target", "names", "1001"]):
            await run_cli()

        mock_build_runtime.assert_called_once_with(require_api_credentials=False)
        mock_target_handler.assert_awaited_once()

    async def test_handler_renders_json_success(self):
        target = TargetNameTargetRecord(
            target_id=1001, target_type="user", current_username="new_handle"
        )
        storage = MagicMock()
        storage.resolve_target_name_target.return_value = TargetNameResolutionRecord(
            status="found", target="1001", matches=(target,)
        )
        storage.get_target_name_snapshots.return_value = [
            TargetNameSnapshotRecord(
                target_id=1001,
                target_type="user",
                observed_at=1700000000,
                username="old_handle",
            )
        ]
        ctx = MagicMock(storage=storage)
        output = StringIO()

        with redirect_stdout(output):
            await _handle_target_command(
                ctx,
                Namespace(
                    target_command="names",
                    target="1001",
                    field="username",
                    format="json",
                ),
            )

        self.assertIn('"target": "1001"', output.getvalue())
        self.assertIn('"new_value": "@old_handle"', output.getvalue())

    async def test_handler_renders_unknown_and_ambiguous_errors(self):
        storage = MagicMock()
        storage.resolve_target_name_target.return_value = TargetNameResolutionRecord(
            status="not_found", target="missing"
        )
        ctx = MagicMock(storage=storage)
        err = StringIO()

        with redirect_stderr(err), self.assertRaises(SystemExit) as missing:
            await _handle_target_command(
                ctx,
                Namespace(
                    target_command="names",
                    target="missing",
                    field="all",
                    format="text",
                ),
            )

        self.assertEqual(missing.exception.code, 1)
        self.assertIn("target not found", err.getvalue())

        storage.resolve_target_name_target.return_value = TargetNameResolutionRecord(
            status="ambiguous",
            target="shared",
            matches=(
                TargetNameTargetRecord(target_id=1001, target_type="user"),
                TargetNameTargetRecord(target_id=1002, target_type="user"),
            ),
        )
        err = StringIO()
        with redirect_stderr(err), self.assertRaises(SystemExit) as ambiguous:
            await _handle_target_command(
                ctx,
                Namespace(
                    target_command="names",
                    target="shared",
                    field="all",
                    format="json",
                ),
            )

        self.assertEqual(ambiguous.exception.code, 1)
        self.assertIn('"code": "ambiguous_target"', err.getvalue())


if __name__ == "__main__":
    unittest.main()
