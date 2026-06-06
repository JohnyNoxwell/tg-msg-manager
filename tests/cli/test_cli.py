import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from argparse import Namespace
from unittest.mock import AsyncMock, MagicMock, patch
from telethon.errors import FloodWaitError, PhoneNumberFloodError

from tg_msg_manager.cli import (
    CLIContext,
    _dispatch_main_menu_choice,
    _format_telegram_login_error,
    get_dirty_target_ids,
    run_cli,
)
from tg_msg_manager.cli_io import print_update_summary, render_main_menu
from tg_msg_manager.core.models.sync_report import TrackedSyncRunReport
from tg_msg_manager.core.config import Settings
from tg_msg_manager.core.runtime import AppPaths, AppRuntime
from tg_msg_manager.core.models.setup import SchedulerSetupResult
from tg_msg_manager.infrastructure.storage.records import PrimaryTarget
from tg_msg_manager.i18n import get_lang
from tg_msg_manager.services.rendering import DEFAULT_TXT_PROFILE


class TestCLIContext(unittest.IsolatedAsyncioTestCase):
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

    @patch("tg_msg_manager.cli.setup_logging")
    @patch("tg_msg_manager.cli.DBExportService")
    @patch("tg_msg_manager.cli.CleanerService")
    @patch("tg_msg_manager.cli.SQLiteStorage")
    async def test_initialize_delete_context_without_client(
        self,
        mock_storage_cls,
        mock_cleaner_cls,
        mock_db_exporter_cls,
        mock_setup_logging,
    ):
        mock_storage = MagicMock()
        mock_storage.start = AsyncMock()
        mock_storage.close = AsyncMock()
        mock_storage_cls.return_value = mock_storage
        mock_db_exporter_cls.return_value = MagicMock()
        mock_cleaner_cls.return_value = MagicMock()

        with (
            patch("tg_msg_manager.cli.ProcessManager.acquire_lock", return_value=True),
            patch("tg_msg_manager.cli.ProcessManager.setup_async_signals"),
            patch("tg_msg_manager.cli.ProcessManager.release_lock"),
        ):
            ctx = CLIContext(self.runtime, needs_client=False)
            await ctx.initialize()

            self.assertIsNone(ctx.client)
            mock_storage.start.assert_awaited_once()
            mock_cleaner_cls.assert_called_once()

            await ctx.shutdown()
            mock_storage.close.assert_awaited_once()

    @patch("tg_msg_manager.cli.setup_logging")
    @patch("tg_msg_manager.cli.PrivateArchiveService")
    @patch("tg_msg_manager.cli.ChannelExportService")
    @patch("tg_msg_manager.cli.DBExportService")
    @patch("tg_msg_manager.cli.CleanerService")
    @patch("tg_msg_manager.cli.ExportService")
    @patch("tg_msg_manager.cli.TelethonClientWrapper")
    @patch("tg_msg_manager.cli.SQLiteStorage")
    async def test_initialize_live_context_wires_service_event_sinks(
        self,
        mock_storage_cls,
        mock_client_cls,
        mock_exporter_cls,
        mock_cleaner_cls,
        mock_db_exporter_cls,
        mock_channel_export_cls,
        mock_private_archive_cls,
        mock_setup_logging,
    ):
        mock_storage = MagicMock()
        mock_storage.start = AsyncMock()
        mock_storage.close = AsyncMock()
        mock_storage_cls.return_value = mock_storage
        mock_db_exporter_cls.return_value = MagicMock()
        mock_exporter_cls.return_value = MagicMock()
        mock_cleaner_cls.return_value = MagicMock()
        mock_channel_export_cls.return_value = MagicMock()
        mock_private_archive_cls.return_value = MagicMock()

        mock_client = MagicMock()
        mock_client.connect = AsyncMock()
        mock_client.disconnect = AsyncMock()
        mock_client_cls.return_value = mock_client

        with (
            patch("tg_msg_manager.cli.ProcessManager.acquire_lock", return_value=True),
            patch("tg_msg_manager.cli.ProcessManager.setup_async_signals"),
            patch("tg_msg_manager.cli.ProcessManager.release_lock"),
        ):
            ctx = CLIContext(self.runtime, needs_client=True)
            await ctx.initialize()

            self.assertTrue(callable(mock_exporter_cls.call_args.kwargs["event_sink"]))
            self.assertTrue(callable(mock_cleaner_cls.call_args.kwargs["event_sink"]))
            self.assertTrue(
                callable(mock_private_archive_cls.call_args.kwargs["event_sink"])
            )
            self.assertTrue(
                callable(mock_channel_export_cls.call_args.kwargs["event_sink"])
            )

            await ctx.shutdown()
            mock_client.disconnect.assert_awaited_once()

    @patch("tg_msg_manager.cli.setup_logging")
    @patch("tg_msg_manager.cli.PrivateArchiveService")
    @patch("tg_msg_manager.cli.ChannelExportService")
    @patch("tg_msg_manager.cli.DBExportService")
    @patch("tg_msg_manager.cli.CleanerService")
    @patch("tg_msg_manager.cli.ExportService")
    @patch("tg_msg_manager.cli.TelethonClientWrapper")
    @patch("tg_msg_manager.cli.SQLiteStorage")
    async def test_initialize_login_flood_wait_exits_with_readable_message(
        self,
        mock_storage_cls,
        mock_client_cls,
        mock_exporter_cls,
        mock_cleaner_cls,
        mock_db_exporter_cls,
        mock_channel_export_cls,
        mock_private_archive_cls,
        mock_setup_logging,
    ):
        mock_storage = MagicMock()
        mock_storage.start = AsyncMock()
        mock_storage.close = AsyncMock()
        mock_storage_cls.return_value = mock_storage
        mock_db_exporter_cls.return_value = MagicMock()

        mock_client = MagicMock()
        mock_client.connect = AsyncMock(
            side_effect=FloodWaitError(request=None, capture=86400)
        )
        mock_client.disconnect = AsyncMock()
        mock_client_cls.return_value = mock_client

        error_output = StringIO()
        with (
            patch("tg_msg_manager.cli.ProcessManager.acquire_lock", return_value=True),
            patch("tg_msg_manager.cli.ProcessManager.setup_async_signals"),
            patch("tg_msg_manager.cli.ProcessManager.release_lock"),
            redirect_stderr(error_output),
            self.assertRaises(SystemExit) as raised,
        ):
            ctx = CLIContext(self.runtime, needs_client=True)
            await ctx.initialize()

        self.assertEqual(raised.exception.code, 1)
        rendered = error_output.getvalue()
        self.assertIn("Не удалось войти в Telegram", rendered)
        self.assertIn("24 ч.", rendered)
        mock_exporter_cls.assert_not_called()
        mock_private_archive_cls.assert_not_called()
        mock_channel_export_cls.assert_not_called()
        mock_cleaner_cls.assert_not_called()

        await ctx.shutdown()
        mock_storage.close.assert_awaited_once()
        mock_client.disconnect.assert_awaited_once()

    def test_login_phone_flood_without_seconds_gets_readable_message(self):
        message = _format_telegram_login_error(PhoneNumberFloodError(request=None))

        self.assertIn("Не удалось войти в Telegram", message)
        self.assertIn("до 24 часов", message)

    def test_login_connection_error_gets_readable_message(self):
        message = _format_telegram_login_error(
            ConnectionError("Connection to Telegram failed 5 time(s)")
        )

        self.assertIn("Не удалось подключиться к Telegram", message)
        self.assertIn("Проверьте интернет-соединение", message)

    def test_print_update_summary_renders_per_user_breakdown(self):
        stats = TrackedSyncRunReport.coerce(
            {
                2: {
                    "name": "Tracked User",
                    "count": 3,
                    "dirty": True,
                    "own_messages": 2,
                    "with_context": 5,
                },
                3: {
                    "name": "Unchanged User",
                    "count": 0,
                    "dirty": False,
                    "own_messages": 10,
                    "with_context": 14,
                },
            }
        )

        output = StringIO()
        with (
            patch.object(sys.stdout, "isatty", return_value=False),
            redirect_stdout(output),
        ):
            print_update_summary(stats, title="Update")

        rendered = output.getvalue()
        self.assertIn("Tracked User", rendered)
        self.assertIn("без контекста · 2", rendered)
        self.assertIn("с контекстом · 5", rendered)
        self.assertNotIn("Unchanged User", rendered)

    def test_get_dirty_target_ids_filters_unchanged_users(self):
        stats = TrackedSyncRunReport.coerce(
            {
                1: {"name": "A", "count": 0, "dirty": False},
                2: {"name": "B", "count": 3, "dirty": True},
                3: {"name": "C", "count": 0},
                4: {"name": "D", "count": 2},
            }
        )

        self.assertEqual(get_dirty_target_ids(stats), [2, 4])

    @patch("tg_msg_manager.cli_support.telemetry.log_summary")
    @patch("tg_msg_manager.cli.commands.export.get_safe_user_and_chat")
    @patch("tg_msg_manager.cli.CLIContext")
    async def test_run_cli_export_logs_telemetry_summary(
        self,
        mock_ctx_cls,
        mock_get_safe_user_and_chat,
        mock_log_summary,
    ):
        mock_ctx = MagicMock()
        mock_ctx.initialize = AsyncMock()
        mock_ctx.shutdown = AsyncMock()
        mock_ctx.exporter = MagicMock()
        mock_ctx.exporter.sync_chat = AsyncMock(return_value=0)
        mock_ctx.db_exporter = MagicMock()
        mock_ctx.db_exporter.export_user_messages = AsyncMock(
            return_value="DB_EXPORTS/test.jsonl"
        )
        mock_ctx.storage = MagicMock()
        mock_ctx.storage.get_user.return_value = {
            "first_name": "Kirill",
            "last_name": "Cilantro",
        }
        mock_ctx_cls.return_value = mock_ctx

        user_ent = MagicMock(
            id=404307871, first_name="Kirill", last_name="Cilantro", username="kirill"
        )
        chat_ent = MagicMock(id=1274306614)
        mock_get_safe_user_and_chat.return_value = (user_ent, chat_ent)

        with patch.object(
            sys,
            "argv",
            [
                "prog",
                "export",
                "--user-id",
                "404307871",
                "--chat-id",
                "1274306614",
                "--depth",
                "2",
                "--json",
            ],
        ):
            await run_cli(runtime=self.runtime)

        mock_log_summary.assert_called_once_with("Export telemetry summary")
        self.assertTrue(
            mock_ctx.db_exporter.export_user_messages.await_args.kwargs["as_json"]
        )

    @patch("tg_msg_manager.cli.CLIContext")
    async def test_run_cli_retry_runs_worker(self, mock_ctx_cls):
        mock_ctx = MagicMock()
        mock_ctx.initialize = AsyncMock()
        mock_ctx.shutdown = AsyncMock()
        mock_ctx.retry_worker = MagicMock()
        mock_ctx.retry_worker.run_due_tasks = AsyncMock()
        mock_ctx_cls.return_value = mock_ctx

        with patch.object(sys, "argv", ["prog", "retry", "--limit", "2"]):
            await run_cli(runtime=self.runtime)

        mock_ctx.retry_worker.run_due_tasks.assert_awaited_once_with(limit=2)

    @patch("tg_msg_manager.cli.commands.export.enqueue_archive_pm_retry_task")
    @patch("tg_msg_manager.cli.commands.export.get_safe_user_and_chat")
    @patch("tg_msg_manager.cli.CLIContext")
    async def test_run_cli_export_pm_enqueues_retry_on_failure(
        self,
        mock_ctx_cls,
        mock_get_safe_user_and_chat,
        mock_enqueue_retry,
    ):
        mock_ctx = MagicMock()
        mock_ctx.initialize = AsyncMock()
        mock_ctx.shutdown = AsyncMock()
        mock_ctx.private_archive = MagicMock()
        mock_ctx.private_archive.archive_pm = AsyncMock(
            side_effect=RuntimeError("boom")
        )
        mock_ctx.storage = MagicMock()
        mock_ctx_cls.return_value = mock_ctx

        user_ent = MagicMock(id=777)
        mock_get_safe_user_and_chat.return_value = (user_ent, None)

        with patch.object(sys, "argv", ["prog", "export-pm", "--user-id", "777"]):
            await run_cli(runtime=self.runtime)

        mock_enqueue_retry.assert_called_once()

    @patch("tg_msg_manager.cli_menu._handle_menu_retry", new_callable=AsyncMock)
    async def test_dispatch_main_menu_choice_routes_retry_hotkey(
        self,
        mock_retry_menu,
    ):
        ctx = MagicMock()

        keep_running = await _dispatch_main_menu_choice(ctx, "R")

        self.assertTrue(keep_running)
        mock_retry_menu.assert_awaited_once_with(ctx)

    @patch("tg_msg_manager.cli_menu._handle_menu_report", new_callable=AsyncMock)
    async def test_dispatch_main_menu_choice_routes_report_hotkey(
        self,
        mock_report_menu,
    ):
        ctx = MagicMock()

        keep_running = await _dispatch_main_menu_choice(ctx, "P")

        self.assertTrue(keep_running)
        mock_report_menu.assert_awaited_once_with(ctx)

    @patch(
        "tg_msg_manager.cli_menu._handle_menu_export_channel", new_callable=AsyncMock
    )
    async def test_dispatch_main_menu_choice_routes_channel_export_menu_item(
        self,
        mock_export_channel_menu,
    ):
        ctx = MagicMock()

        keep_running = await _dispatch_main_menu_choice(ctx, "10")

        self.assertTrue(keep_running)
        mock_export_channel_menu.assert_awaited_once_with(ctx)

    @patch("tg_msg_manager.cli_menu.set_lang")
    async def test_dispatch_main_menu_choice_routes_two_digit_language_toggle(
        self,
        mock_set_lang,
    ):
        ctx = MagicMock()

        with patch("tg_msg_manager.cli_menu.get_lang", return_value="ru"):
            keep_running = await _dispatch_main_menu_choice(ctx, "98")

        self.assertTrue(keep_running)
        mock_set_lang.assert_called_once_with("en")

    async def test_dispatch_main_menu_choice_routes_two_digit_exit(self):
        ctx = MagicMock()

        keep_running = await _dispatch_main_menu_choice(ctx, "00")

        self.assertFalse(keep_running)

    @patch("builtins.print")
    @patch("tg_msg_manager.cli.commands.report.render_report_json", return_value="{}")
    @patch("tg_msg_manager.cli.commands.report.ReportCollector")
    @patch("tg_msg_manager.cli.CLIContext")
    async def test_run_cli_report_uses_read_only_context(
        self,
        mock_ctx_cls,
        mock_report_collector_cls,
        mock_render_report_json,
        mock_print,
    ):
        mock_ctx = MagicMock()
        mock_ctx.initialize = AsyncMock()
        mock_ctx.shutdown = AsyncMock()
        mock_ctx.storage = MagicMock()
        mock_ctx.paths = MagicMock()
        mock_ctx.paths.db_exports_dir = "/tmp/exports"
        mock_ctx_cls.return_value = mock_ctx
        mock_collector = MagicMock()
        mock_collector.collect.return_value = MagicMock()
        mock_report_collector_cls.return_value = mock_collector

        with patch.object(sys, "argv", ["prog", "report", "--json"]):
            await run_cli(runtime=self.runtime)

        self.assertFalse(mock_ctx_cls.call_args.kwargs["needs_client"])
        mock_report_collector_cls.assert_called_once()
        mock_render_report_json.assert_called_once()
        mock_print.assert_called()

    @patch("tg_msg_manager.cli_support.telemetry.log_summary")
    @patch("tg_msg_manager.cli.commands.export.get_safe_user_and_chat")
    @patch("tg_msg_manager.cli.CLIContext")
    async def test_run_cli_export_uses_numeric_user_id_fallback_when_entity_is_unresolved(
        self,
        mock_ctx_cls,
        mock_get_safe_user_and_chat,
        mock_log_summary,
    ):
        mock_ctx = MagicMock()
        mock_ctx.initialize = AsyncMock()
        mock_ctx.shutdown = AsyncMock()
        mock_ctx.exporter = MagicMock()
        mock_ctx.exporter.sync_chat = AsyncMock(return_value=0)
        mock_ctx.exporter.sync_all_dialogs_for_user = AsyncMock(return_value=7)
        mock_ctx.db_exporter = MagicMock()
        mock_ctx.db_exporter.export_user_messages = AsyncMock(return_value="")
        mock_ctx.storage = MagicMock()
        mock_ctx.storage.get_user.return_value = None
        mock_ctx_cls.return_value = mock_ctx

        mock_get_safe_user_and_chat.return_value = (None, None)

        with patch.object(
            sys,
            "argv",
            [
                "prog",
                "export",
                "--user-id",
                "2061894541",
                "--json",
            ],
        ):
            await run_cli(runtime=self.runtime)

        mock_ctx.exporter.sync_all_dialogs_for_user.assert_awaited_once()
        self.assertEqual(
            mock_ctx.exporter.sync_all_dialogs_for_user.await_args.args[0], 2061894541
        )
        mock_log_summary.assert_called_once_with("Export telemetry summary")
        self.assertTrue(
            mock_ctx.db_exporter.export_user_messages.await_args.kwargs["as_json"]
        )

    @patch("tg_msg_manager.cli.CLIContext")
    async def test_run_cli_binds_runtime_language_for_command_handlers(
        self,
        mock_ctx_cls,
    ):
        runtime = AppRuntime(
            settings=Settings(
                api_id=1,
                api_hash="hash",
                db_path="messages.db",
                lang="en",
            ),
            paths=self.runtime.paths,
            python_executable=self.runtime.python_executable,
        )
        mock_ctx = MagicMock()
        mock_ctx.initialize = AsyncMock()
        mock_ctx.shutdown = AsyncMock()
        mock_ctx_cls.return_value = mock_ctx
        observed = {}

        async def fake_setup_handler(ctx, args):
            del ctx, args
            observed["lang"] = get_lang()

        with (
            patch.object(sys, "argv", ["prog", "setup"]),
            patch(
                "tg_msg_manager.cli._handle_setup_command",
                side_effect=fake_setup_handler,
            ),
        ):
            await run_cli(runtime=runtime)

        self.assertEqual(observed["lang"], "en")

    @patch("tg_msg_manager.cli.commands.setup._print_scheduler_setup_result")
    @patch("tg_msg_manager.cli.commands.setup.setup_scheduler", new_callable=AsyncMock)
    @patch("tg_msg_manager.cli.CLIContext")
    async def test_run_cli_schedule_passes_typed_request_to_scheduler(
        self,
        mock_ctx_cls,
        mock_setup_scheduler,
        mock_print_scheduler_setup_result,
    ):
        mock_ctx = MagicMock()
        mock_ctx.initialize = AsyncMock()
        mock_ctx.shutdown = AsyncMock()
        mock_ctx_cls.return_value = mock_ctx
        mock_setup_scheduler.return_value = SchedulerSetupResult(
            success=True,
            plist_path="/tmp/home/Library/LaunchAgents/com.tg-msg-manager.update.plist",
            logs_dir="/tmp/project/LOGS",
            hour=7,
            minute=30,
        )

        with (
            patch.object(sys, "argv", ["prog", "schedule"]),
            patch("builtins.input", return_value="07:30"),
        ):
            await run_cli(runtime=self.runtime)

        request = mock_setup_scheduler.await_args.args[0]
        self.assertEqual(request.hour, 7)
        self.assertEqual(request.minute, 30)
        mock_print_scheduler_setup_result.assert_called_once()

    @patch("tg_msg_manager.cli_support.telemetry.log_summary")
    @patch("tg_msg_manager.cli.commands.export.get_safe_user_and_chat")
    @patch("tg_msg_manager.cli.CLIContext")
    async def test_run_cli_export_without_json_writes_txt_summary(
        self,
        mock_ctx_cls,
        mock_get_safe_user_and_chat,
        mock_log_summary,
    ):
        mock_ctx = MagicMock()
        mock_ctx.initialize = AsyncMock()
        mock_ctx.shutdown = AsyncMock()
        mock_ctx.exporter = MagicMock()
        mock_ctx.exporter.sync_all_dialogs_for_user = AsyncMock(return_value=3)
        mock_ctx.db_exporter = MagicMock()
        mock_ctx.db_exporter.export_user_messages = AsyncMock(
            return_value="DB_EXPORTS/test.txt"
        )
        mock_ctx.storage = MagicMock()
        mock_ctx.storage.get_user.return_value = None
        mock_ctx_cls.return_value = mock_ctx
        mock_get_safe_user_and_chat.return_value = (None, None)

        with patch.object(
            sys,
            "argv",
            [
                "prog",
                "export",
                "--user-id",
                "123456789",
            ],
        ):
            await run_cli(runtime=self.runtime)

        mock_log_summary.assert_called_once_with("Export telemetry summary")
        self.assertFalse(
            mock_ctx.db_exporter.export_user_messages.await_args.kwargs["as_json"]
        )
        self.assertEqual(
            mock_ctx.db_exporter.export_user_messages.await_args.kwargs["txt_profile"],
            DEFAULT_TXT_PROFILE,
        )

    @patch("tg_msg_manager.cli.CLIContext")
    async def test_run_cli_db_export_passes_explicit_legacy_txt_profile(
        self, mock_ctx_cls
    ):
        mock_ctx = MagicMock()
        mock_ctx.initialize = AsyncMock()
        mock_ctx.shutdown = AsyncMock()
        mock_ctx.db_exporter = MagicMock()
        mock_ctx.db_exporter.export_user_messages = AsyncMock(return_value="x.txt")
        mock_ctx_cls.return_value = mock_ctx

        with patch.object(
            sys,
            "argv",
            [
                "prog",
                "db-export",
                "--user-id",
                "123456789",
                "--txt-profile",
                "legacy",
            ],
        ):
            await run_cli(runtime=self.runtime)

        self.assertEqual(
            mock_ctx.db_exporter.export_user_messages.await_args.kwargs["txt_profile"],
            "legacy",
        )

    @patch("tg_msg_manager.cli.CLIContext")
    async def test_run_cli_db_export_defaults_to_txt(self, mock_ctx_cls):
        mock_ctx = MagicMock()
        mock_ctx.initialize = AsyncMock()
        mock_ctx.shutdown = AsyncMock()
        mock_ctx.db_exporter = MagicMock()
        mock_ctx.db_exporter.export_user_messages = AsyncMock(return_value="x.txt")
        mock_ctx_cls.return_value = mock_ctx

        with patch.object(
            sys,
            "argv",
            [
                "prog",
                "db-export",
                "--user-id",
                "123456789",
            ],
        ):
            await run_cli(runtime=self.runtime)

        self.assertFalse(
            mock_ctx.db_exporter.export_user_messages.await_args.kwargs["as_json"]
        )

    @patch("tg_msg_manager.cli.CLIContext")
    async def test_run_cli_db_export_json_flag_writes_json(self, mock_ctx_cls):
        mock_ctx = MagicMock()
        mock_ctx.initialize = AsyncMock()
        mock_ctx.shutdown = AsyncMock()
        mock_ctx.db_exporter = MagicMock()
        mock_ctx.db_exporter.export_user_messages = AsyncMock(return_value="x.jsonl")
        mock_ctx_cls.return_value = mock_ctx

        with patch.object(
            sys,
            "argv",
            [
                "prog",
                "db-export",
                "--user-id",
                "123456789",
                "--json",
            ],
        ):
            await run_cli(runtime=self.runtime)

        self.assertTrue(
            mock_ctx.db_exporter.export_user_messages.await_args.kwargs["as_json"]
        )
        self.assertEqual(
            mock_ctx.db_exporter.export_user_messages.await_args.kwargs["txt_profile"],
            DEFAULT_TXT_PROFILE,
        )

    @patch("tg_msg_manager.cli_menu.pause_for_enter")
    async def test_menu_db_export_empty_txt_profile_uses_context_readable(
        self, mock_pause
    ):
        del mock_pause
        from tg_msg_manager.cli_menu import _handle_menu_db_export

        ctx = MagicMock()
        ctx.storage.get_primary_targets.return_value = [
            PrimaryTarget(user_id=123, chat_id=456, author_name="Target")
        ]
        ctx.db_exporter.export_user_messages = AsyncMock(return_value="x.txt")

        with patch(
            "tg_msg_manager.cli_menu.TerminalInput.prompt_with_esc",
            side_effect=["1", "2", ""],
        ):
            await _handle_menu_db_export(ctx)

        ctx.db_exporter.export_user_messages.assert_awaited_once_with(
            123,
            as_json=False,
            txt_profile=DEFAULT_TXT_PROFILE,
        )

    @patch("tg_msg_manager.cli_menu.pause_for_enter")
    async def test_menu_db_export_passes_explicit_context_readable_profile(
        self, mock_pause
    ):
        del mock_pause
        from tg_msg_manager.cli_menu import _handle_menu_db_export

        ctx = MagicMock()
        ctx.storage.get_primary_targets.return_value = [
            PrimaryTarget(user_id=123, chat_id=456, author_name="Target")
        ]
        ctx.db_exporter.export_user_messages = AsyncMock(return_value="x.txt")

        with patch(
            "tg_msg_manager.cli_menu.TerminalInput.prompt_with_esc",
            side_effect=["1", "2", "context-readable"],
        ):
            await _handle_menu_db_export(ctx)

        ctx.db_exporter.export_user_messages.assert_awaited_once_with(
            123,
            as_json=False,
            txt_profile="context-readable",
        )

    @patch("tg_msg_manager.cli_menu.pause_for_enter")
    async def test_menu_db_export_passes_explicit_legacy_profile(self, mock_pause):
        del mock_pause
        from tg_msg_manager.cli_menu import _handle_menu_db_export

        ctx = MagicMock()
        ctx.storage.get_primary_targets.return_value = [
            PrimaryTarget(user_id=123, chat_id=456, author_name="Target")
        ]
        ctx.db_exporter.export_user_messages = AsyncMock(return_value="x.txt")

        with patch(
            "tg_msg_manager.cli_menu.TerminalInput.prompt_with_esc",
            side_effect=["1", "2", "legacy"],
        ):
            await _handle_menu_db_export(ctx)

        ctx.db_exporter.export_user_messages.assert_awaited_once_with(
            123,
            as_json=False,
            txt_profile="legacy",
        )

    @patch("tg_msg_manager.cli_menu.pause_for_enter")
    async def test_menu_db_export_rejects_invalid_txt_profile(self, mock_pause):
        del mock_pause
        from tg_msg_manager.cli_menu import _handle_menu_db_export

        ctx = MagicMock()
        ctx.storage.get_primary_targets.return_value = [
            PrimaryTarget(user_id=123, chat_id=456, author_name="Target")
        ]
        ctx.db_exporter.export_user_messages = AsyncMock(return_value="x.txt")

        with (
            patch(
                "tg_msg_manager.cli_menu.TerminalInput.prompt_with_esc",
                side_effect=["1", "2", "compact"],
            ),
            patch("tg_msg_manager.cli_menu._print_menu_invalid_selection") as invalid,
        ):
            await _handle_menu_db_export(ctx)

        invalid.assert_called_once()
        ctx.db_exporter.export_user_messages.assert_not_awaited()

    @patch("tg_msg_manager.cli_menu.pause_for_enter")
    async def test_menu_db_export_does_not_prompt_txt_profile_for_json(
        self, mock_pause
    ):
        del mock_pause
        from tg_msg_manager.cli_menu import _handle_menu_db_export

        ctx = MagicMock()
        ctx.storage.get_primary_targets.return_value = [
            PrimaryTarget(user_id=123, chat_id=456, author_name="Target")
        ]
        ctx.db_exporter.export_user_messages = AsyncMock(return_value="x.jsonl")

        with patch(
            "tg_msg_manager.cli_menu.TerminalInput.prompt_with_esc",
            side_effect=["1", "1"],
        ) as prompt:
            await _handle_menu_db_export(ctx)

        self.assertEqual(prompt.call_count, 2)
        ctx.db_exporter.export_user_messages.assert_awaited_once_with(
            123,
            as_json=True,
            txt_profile=DEFAULT_TXT_PROFILE,
        )

    @patch("tg_msg_manager.cli.main_menu", new_callable=AsyncMock)
    @patch("tg_msg_manager.cli.build_cli_parser")
    async def test_run_cli_without_command_in_non_tty_prints_help(
        self,
        mock_build_parser,
        mock_main_menu,
    ):
        parser = MagicMock()
        parser.parse_args.return_value = Namespace(command=None)
        mock_build_parser.return_value = parser

        with (
            patch.object(sys.stdin, "isatty", return_value=False),
            patch.object(sys.stdout, "isatty", return_value=False),
        ):
            await run_cli(runtime=self.runtime)

        parser.print_help.assert_called_once()
        mock_main_menu.assert_not_awaited()


class TestMainMenuRendering(unittest.TestCase):
    def test_render_main_menu_uses_two_digit_labels(self):
        output = StringIO()

        with (
            patch.object(sys.stdout, "isatty", return_value=False),
            redirect_stdout(output),
        ):
            render_main_menu(12345)

        rendered = output.getvalue()
        self.assertIn("01 ▸", rendered)
        self.assertIn("09 ▸", rendered)
        self.assertIn("10 ▸", rendered)
        self.assertIn("11 ▸", rendered)
        self.assertIn("12 ▸", rendered)
        self.assertIn("98 ▸", rendered)
        self.assertIn("00 ▸", rendered)
        self.assertNotIn("[01]", rendered)


if __name__ == "__main__":
    unittest.main()
