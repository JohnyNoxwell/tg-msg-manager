import sys
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from tg_msg_manager.cli import _command_needs_client, run_cli
from tg_msg_manager.cli_commands import _handle_export_channel_command
from tg_msg_manager.cli_parser import build_cli_parser
from tg_msg_manager.core.config import Settings
from tg_msg_manager.core.runtime import AppPaths, AppRuntime
from tg_msg_manager.services.channel_export import ChannelResolveError


class TestChannelExportCLIParser(unittest.TestCase):
    def test_help_includes_export_channel(self):
        parser = build_cli_parser()

        self.assertIn("export-channel", parser.format_help())

    def test_channel_is_required(self):
        parser = build_cli_parser()

        with self.assertRaises(SystemExit):
            parser.parse_args(["export-channel"])

    def test_media_choices_enforced(self):
        parser = build_cli_parser()

        with self.assertRaises(SystemExit):
            parser.parse_args(
                ["export-channel", "--channel", "@example", "--media", "invalid"]
            )

    def test_limit_is_parsed(self):
        parser = build_cli_parser()
        parsed = parser.parse_args(
            ["export-channel", "--channel", "@example", "--limit", "5"]
        )

        self.assertEqual(parsed.limit, 5)
        self.assertEqual(parsed.media, "metadata")
        self.assertFalse(parsed.force)

    def test_full_media_flags_are_parsed(self):
        parser = build_cli_parser()
        parsed = parser.parse_args(
            [
                "export-channel",
                "--channel",
                "@example",
                "--media",
                "full",
                "--max-media-size",
                "50MB",
                "--media-types",
                "photo,video",
            ]
        )

        self.assertEqual(parsed.media, "full")
        self.assertEqual(parsed.max_media_size, 50 * 1024 * 1024)
        self.assertEqual(parsed.media_types, ("photo", "video"))

    def test_invalid_media_size_is_rejected(self):
        parser = build_cli_parser()

        with self.assertRaises(SystemExit):
            parser.parse_args(
                [
                    "export-channel",
                    "--channel",
                    "@example",
                    "--max-media-size",
                    "abc",
                ]
            )

    def test_invalid_media_types_are_rejected(self):
        parser = build_cli_parser()

        with self.assertRaises(SystemExit):
            parser.parse_args(
                [
                    "export-channel",
                    "--channel",
                    "@example",
                    "--media-types",
                    "photo,ocr",
                ]
            )


class TestChannelExportCLIHandler(unittest.IsolatedAsyncioTestCase):
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

    async def test_handler_builds_options_and_prints_paths(self):
        ctx = MagicMock()
        ctx.paths.channel_exports_dir = "/tmp/tg-msg-manager/exports/channels"
        ctx.channel_exporter = MagicMock()
        ctx.channel_exporter.export_channel = AsyncMock(
            return_value=MagicMock(
                run_mode="incremental",
                message_count=2,
                media_count=1,
                posts_exported_this_run=1,
                media_records_added_this_run=1,
                downloaded_media_count_this_run=0,
                already_existing_media_count_this_run=0,
                skipped_by_size_count_this_run=0,
                skipped_by_type_count_this_run=0,
                failed_media_count_this_run=0,
                manifest_path=Path("/tmp/out/manifest.json"),
                messages_jsonl_path=Path("/tmp/out/messages.jsonl"),
                messages_txt_path=Path("/tmp/out/messages.txt"),
                media_manifest_path=Path("/tmp/out/media_manifest.jsonl"),
                state_path=Path("/tmp/out/channel_export_state.json"),
            )
        )
        args = Namespace(
            channel="@example",
            limit=5,
            media="metadata",
            max_media_size=None,
            media_types=None,
            output_dir=None,
            force=False,
        )

        with patch("builtins.print") as mock_print:
            await _handle_export_channel_command(ctx, args)

        options = ctx.channel_exporter.export_channel.await_args.args[0]
        self.assertEqual(options.channel, "@example")
        self.assertEqual(options.limit, 5)
        self.assertEqual(options.media_mode, "metadata")
        self.assertEqual(options.output_dir, Path(ctx.paths.channel_exports_dir))
        self.assertIsNone(options.max_media_size)
        self.assertIsNone(options.media_types)
        mock_print.assert_any_call("Channel export completed")
        mock_print.assert_any_call("Mode: incremental")

    async def test_handler_converts_domain_error_to_system_exit(self):
        ctx = MagicMock()
        ctx.paths.channel_exports_dir = "/tmp/tg-msg-manager/exports/channels"
        ctx.channel_exporter = MagicMock()
        ctx.channel_exporter.export_channel = AsyncMock(
            side_effect=ChannelResolveError(
                "Could not resolve channel '-1001274306614'"
            )
        )
        args = Namespace(
            channel="-1001274306614",
            limit=100,
            media="metadata",
            max_media_size=None,
            media_types=None,
            output_dir=None,
            force=False,
        )

        with self.assertRaises(SystemExit) as raised:
            await _handle_export_channel_command(ctx, args)

        self.assertEqual(
            str(raised.exception),
            "Could not resolve channel '-1001274306614'",
        )

    async def test_handler_converts_unexpected_error_to_system_exit(self):
        ctx = MagicMock()
        ctx.paths.channel_exports_dir = "/tmp/tg-msg-manager/exports/channels"
        ctx.channel_exporter = MagicMock()
        ctx.channel_exporter.export_channel = AsyncMock(
            side_effect=TypeError("Object of type datetime is not JSON serializable")
        )
        args = Namespace(
            channel="@alekseevka_kharkiv",
            limit=100,
            media="metadata",
            max_media_size=None,
            media_types=None,
            output_dir=None,
            force=False,
        )

        with self.assertRaises(SystemExit) as raised:
            await _handle_export_channel_command(ctx, args)

        self.assertEqual(
            str(raised.exception),
            "Channel export failed: Object of type datetime is not JSON serializable",
        )

    @patch("tg_msg_manager.cli.CLIContext")
    async def test_run_cli_dispatches_export_channel_and_requires_client(
        self,
        mock_ctx_cls,
    ):
        mock_ctx = MagicMock()
        mock_ctx.initialize = AsyncMock()
        mock_ctx.shutdown = AsyncMock()
        mock_ctx_cls.return_value = mock_ctx

        with (
            patch.object(
                sys,
                "argv",
                ["prog", "export-channel", "--channel", "@example", "--limit", "2"],
            ),
            patch(
                "tg_msg_manager.cli._handle_export_channel_command",
                new_callable=AsyncMock,
            ) as mock_handler,
        ):
            await run_cli(runtime=self.runtime)

        self.assertTrue(mock_ctx_cls.call_args.kwargs["needs_client"])
        mock_handler.assert_awaited_once()
        self.assertTrue(_command_needs_client("export-channel"))


if __name__ == "__main__":
    unittest.main()
