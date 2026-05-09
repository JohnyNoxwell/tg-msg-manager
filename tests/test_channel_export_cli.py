import sys
import unittest
from argparse import Namespace
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from tg_msg_manager.cli import _command_needs_client, run_cli
from tg_msg_manager.cli_commands import _handle_export_channel_command
from tg_msg_manager.cli_menu import _handle_menu_export_channel
from tg_msg_manager.cli_parser import build_cli_parser
from tg_msg_manager.core.config import Settings
from tg_msg_manager.core.runtime import AppPaths, AppRuntime
from tg_msg_manager.services.channel_export import ChannelResolveError


class TestChannelExportCLIParser(unittest.TestCase):
    def test_help_includes_export_channel(self):
        parser = build_cli_parser()

        self.assertIn("export-channel", parser.format_help())

    def test_export_channel_help_exits_cleanly(self):
        parser = build_cli_parser()
        output = StringIO()

        with redirect_stdout(output), self.assertRaises(SystemExit) as raised:
            parser.parse_args(["export-channel", "--help"])

        self.assertEqual(raised.exception.code, 0)
        self.assertIn("--channel", output.getvalue())
        self.assertIn("--discussion", output.getvalue())

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
        self.assertEqual(parsed.discussion, "none")
        self.assertEqual(parsed.max_comments_per_post, 100)
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

    def test_discussion_mode_choices_are_parsed(self):
        parser = build_cli_parser()

        parsed_none = parser.parse_args(
            ["export-channel", "--channel", "@example", "--discussion", "none"]
        )
        parsed_metadata = parser.parse_args(
            ["export-channel", "--channel", "@example", "--discussion", "metadata"]
        )
        parsed_full = parser.parse_args(
            ["export-channel", "--channel", "@example", "--discussion", "full"]
        )

        self.assertEqual(parsed_none.discussion, "none")
        self.assertEqual(parsed_metadata.discussion, "metadata")
        self.assertEqual(parsed_full.discussion, "full")

    def test_invalid_discussion_mode_is_rejected(self):
        parser = build_cli_parser()

        with self.assertRaises(SystemExit):
            parser.parse_args(
                ["export-channel", "--channel", "@example", "--discussion", "tree"]
            )

    def test_max_comments_per_post_is_parsed(self):
        parser = build_cli_parser()
        parsed = parser.parse_args(
            [
                "export-channel",
                "--channel",
                "@example",
                "--max-comments-per-post",
                "50",
            ]
        )

        self.assertEqual(parsed.max_comments_per_post, 50)

    def test_invalid_max_comments_per_post_is_rejected(self):
        parser = build_cli_parser()

        for value in ("0", "-1"):
            with self.subTest(value=value), self.assertRaises(SystemExit):
                parser.parse_args(
                    [
                        "export-channel",
                        "--channel",
                        "@example",
                        "--max-comments-per-post",
                        value,
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
                discussion_mode="full",
                discussion_thread_count_this_run=2,
                discussion_comment_count_this_run=5,
                failed_discussion_thread_count_this_run=1,
                discussion_comments_jsonl_path=Path(
                    "/tmp/out/discussion_comments.jsonl"
                ),
                discussion_threads_jsonl_path=Path("/tmp/out/discussion_threads.jsonl"),
                discussion_state_path=Path("/tmp/out/discussion_export_state.json"),
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
            discussion="full",
            max_comments_per_post=50,
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
        self.assertEqual(options.discussion_mode, "full")
        self.assertEqual(options.max_comments_per_post, 50)
        mock_print.assert_any_call("Channel export completed")
        mock_print.assert_any_call("Mode: incremental")
        mock_print.assert_any_call("Discussion mode: full")
        mock_print.assert_any_call("Discussion threads this run: 2")
        mock_print.assert_any_call("Discussion comments this run: 5")
        mock_print.assert_any_call("Failed discussion threads this run: 1")
        mock_print.assert_any_call(
            "Discussion comments: /tmp/out/discussion_comments.jsonl"
        )

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
            discussion="none",
            max_comments_per_post=100,
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
            discussion="none",
            max_comments_per_post=100,
            output_dir=None,
            force=False,
        )

        with self.assertRaises(SystemExit) as raised:
            await _handle_export_channel_command(ctx, args)

        self.assertEqual(
            str(raised.exception),
            "Channel export failed: Object of type datetime is not JSON serializable",
        )

    async def _run_menu_export_channel(self, inputs):
        ctx = MagicMock()

        with (
            patch(
                "tg_msg_manager.cli_menu.TerminalInput.prompt_with_esc",
                side_effect=inputs,
            ),
            patch("tg_msg_manager.cli_menu.pause_for_enter"),
            patch(
                "tg_msg_manager.cli_menu._handle_export_channel_command",
                new_callable=AsyncMock,
            ) as mock_handler,
        ):
            await _handle_menu_export_channel(ctx)

        return mock_handler

    async def test_menu_export_channel_default_options_preserve_previous_values(self):
        mock_handler = await self._run_menu_export_channel(
            ["1523454586", "100", "full", "", "", "", "", "", ""]
        )

        args = mock_handler.await_args.args[1]
        self.assertEqual(args.channel, "1523454586")
        self.assertEqual(args.limit, 100)
        self.assertEqual(args.media, "full")
        self.assertIsNone(args.max_media_size)
        self.assertIsNone(args.media_types)
        self.assertEqual(args.discussion, "none")
        self.assertEqual(args.max_comments_per_post, 100)
        self.assertIsNone(args.output_dir)
        self.assertFalse(args.force)

    async def test_menu_export_channel_passes_discussion_full(self):
        mock_handler = await self._run_menu_export_channel(
            ["@example", "", "metadata", "full", "", "", "", "", ""]
        )

        args = mock_handler.await_args.args[1]
        self.assertEqual(args.discussion, "full")

    async def test_menu_export_channel_passes_discussion_metadata(self):
        mock_handler = await self._run_menu_export_channel(
            ["@example", "", "metadata", "metadata", "", "", "", "", ""]
        )

        args = mock_handler.await_args.args[1]
        self.assertEqual(args.discussion, "metadata")

    async def test_menu_export_channel_prints_full_mode_warning(self):
        with patch("builtins.print") as mock_print:
            await self._run_menu_export_channel(
                ["@example", "", "metadata", "full", "", "", "", "", ""]
            )

        printed = "\n".join(
            str(call.args[0]) for call in mock_print.call_args_list if call.args
        )
        self.assertIn("Full discussion export is a heavy mode", printed)

    async def test_menu_export_channel_passes_custom_max_comments_per_post(self):
        mock_handler = await self._run_menu_export_channel(
            ["@example", "", "metadata", "", "25", "", "", "", ""]
        )

        args = mock_handler.await_args.args[1]
        self.assertEqual(args.max_comments_per_post, 25)

    async def test_menu_export_channel_passes_force_y_as_true(self):
        mock_handler = await self._run_menu_export_channel(
            ["@example", "", "metadata", "", "", "y", "", "", ""]
        )

        args = mock_handler.await_args.args[1]
        self.assertTrue(args.force)

    async def test_menu_export_channel_passes_output_dir(self):
        mock_handler = await self._run_menu_export_channel(
            ["@example", "", "metadata", "", "", "", "/tmp/out", "", ""]
        )

        args = mock_handler.await_args.args[1]
        self.assertEqual(args.output_dir, "/tmp/out")

    async def test_menu_export_channel_passes_max_media_size(self):
        mock_handler = await self._run_menu_export_channel(
            ["@example", "", "metadata", "", "", "", "", "50MB", ""]
        )

        args = mock_handler.await_args.args[1]
        self.assertEqual(args.max_media_size, 50 * 1024 * 1024)

    async def test_menu_export_channel_passes_media_types(self):
        mock_handler = await self._run_menu_export_channel(
            ["@example", "", "metadata", "", "", "", "", "", "photo,video"]
        )

        args = mock_handler.await_args.args[1]
        self.assertEqual(args.media_types, ("photo", "video"))

    async def test_menu_export_channel_rejects_invalid_discussion(self):
        ctx = MagicMock()

        with (
            patch(
                "tg_msg_manager.cli_menu.TerminalInput.prompt_with_esc",
                side_effect=["@example", "", "metadata", "tree"],
            ),
            patch("tg_msg_manager.cli_menu.pause_for_enter") as mock_pause,
            patch(
                "tg_msg_manager.cli_menu._handle_export_channel_command",
                new_callable=AsyncMock,
            ) as mock_handler,
        ):
            await _handle_menu_export_channel(ctx)

        mock_handler.assert_not_awaited()
        mock_pause.assert_called_once()

    async def test_menu_export_channel_rejects_invalid_max_comments_per_post(self):
        ctx = MagicMock()

        with (
            patch(
                "tg_msg_manager.cli_menu.TerminalInput.prompt_with_esc",
                side_effect=["@example", "", "metadata", "", "0"],
            ),
            patch("tg_msg_manager.cli_menu.pause_for_enter") as mock_pause,
            patch(
                "tg_msg_manager.cli_menu._handle_export_channel_command",
                new_callable=AsyncMock,
            ) as mock_handler,
        ):
            await _handle_menu_export_channel(ctx)

        mock_handler.assert_not_awaited()
        mock_pause.assert_called_once()

    async def test_menu_export_channel_rejects_invalid_force(self):
        ctx = MagicMock()

        with (
            patch(
                "tg_msg_manager.cli_menu.TerminalInput.prompt_with_esc",
                side_effect=["@example", "", "metadata", "", "", "maybe"],
            ),
            patch("tg_msg_manager.cli_menu.pause_for_enter") as mock_pause,
            patch(
                "tg_msg_manager.cli_menu._handle_export_channel_command",
                new_callable=AsyncMock,
            ) as mock_handler,
        ):
            await _handle_menu_export_channel(ctx)

        mock_handler.assert_not_awaited()
        mock_pause.assert_called_once()

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
