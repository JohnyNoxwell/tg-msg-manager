import asyncio
import logging
import os
import sys
from types import SimpleNamespace
from typing import Optional

from telethon.errors import RPCError

from ..cli_commands import (
    _handle_clean_command,
    _handle_db_export_command,
    _handle_delete_command,
    _handle_export_command,
    _handle_export_channel_command,
    _handle_export_pm_command,
    _handle_inspect_dataset_command,
    _handle_report_command,
    _handle_retry_command,
    _handle_schedule_command,
    _handle_setup_command,
    _handle_target_command,
    _handle_update_command,
    _handle_validate_dataset_command,
)
from ..cli_menu import (
    _dispatch_main_menu_choice,
    _handle_menu_report,
    _handle_menu_retry,
)
from ..cli_parser import build_cli_parser
from ..cli_support import (
    _print_scheduler_setup_result,
    get_dirty_target_ids,
    get_safe_user_and_chat,
    resolve_id,
)
from ..core.logging import setup_logging
from ..core.process import ProcessManager
from ..core.runtime import AppRuntime, build_app_runtime
from ..core.telemetry import telemetry
from ..core.telegram.client import TelethonClientWrapper
from ..cli_io import (
    TerminalInput,
    render_main_menu,
    render_service_event,
)
from ..i18n import _, use_lang
from ..infrastructure.storage.sqlite import SQLiteStorage
from ..services.alias_manager import AliasManager
from ..services.channel_export import ChannelExportService
from ..services.cleaner import CleanerService
from ..services.db_export import DBExportService
from ..services.exporter import ExportService
from ..services.private_archive import PrivateArchiveService
from ..services.retry_worker import RetryWorker


logger = logging.getLogger(__name__)
__all__ = [
    "CLIContext",
    "build_cli_parser",
    "get_dirty_target_ids",
    "get_safe_user_and_chat",
    "resolve_id",
    "run_cli",
    "main_menu",
    "main",
    "_dispatch_main_menu_choice",
    "_handle_menu_report",
    "_handle_menu_retry",
    "_handle_setup_command",
    "_print_scheduler_setup_result",
]


def _format_wait_seconds(seconds: int) -> str:
    seconds = max(0, int(seconds))
    if seconds >= 3600 and seconds % 3600 == 0:
        hours = seconds // 3600
        return _("telegram_login_wait_hours", count=hours)
    if seconds >= 60 and seconds % 60 == 0:
        minutes = seconds // 60
        return _("telegram_login_wait_minutes", count=minutes)
    return _("telegram_login_wait_seconds", count=seconds)


def _format_telegram_login_error(error: BaseException) -> Optional[str]:
    if isinstance(error, RPCError):
        wait_seconds = getattr(error, "seconds", None)
        error_name = error.__class__.__name__
        if wait_seconds is not None:
            return _(
                "telegram_login_failed_flood_wait",
                wait=_format_wait_seconds(wait_seconds),
            )
        if "Flood" in error_name:
            return _("telegram_login_failed_flood_unknown")
        return _("telegram_login_failed_rpc", reason=str(error))
    if isinstance(error, EOFError):
        return _("telegram_login_failed_no_input")
    if isinstance(error, (ConnectionError, TimeoutError, OSError)):
        return _("telegram_login_failed_network", reason=str(error))
    return None


class CLIContext:
    """
    Centralized context for CLI resource management.
    Ensures single initialization of services and graceful shutdown.
    """

    def __init__(self, runtime: AppRuntime, needs_client: bool = True):
        self.runtime = runtime
        self.settings = runtime.settings
        self.paths = runtime.paths
        self.pm = ProcessManager(lock_path=self.paths.lock_path)
        self.storage: Optional[SQLiteStorage] = None
        self.client: Optional[TelethonClientWrapper] = None
        self.needs_client = needs_client

        # Services
        self.exporter: Optional[ExportService] = None
        self.cleaner: Optional[CleanerService] = None
        self.db_exporter: Optional[DBExportService] = None
        self.private_archive: Optional[PrivateArchiveService] = None
        self.channel_exporter: Optional[ChannelExportService] = None
        self.retry_worker: Optional[RetryWorker] = None
        self.alias_manager = AliasManager(
            project_root=self.paths.project_root,
            python_executable=self.runtime.python_executable,
        )

        self.active_uid = None

    async def initialize(self):
        setup_logging(level=self.settings.log_level, log_dir=self.paths.logs_dir)
        telemetry.reset()
        if not self.pm.acquire_lock():
            print(_("error_locked"))
            sys.exit(1)

        # Setup async signals early
        self.pm.setup_async_signals(asyncio.get_running_loop(), self.emergency_callback)

        sys.stdout.write("Opening SQLite database...\n")
        sys.stdout.flush()
        self.storage = SQLiteStorage(self.paths.db_path, process_manager=self.pm)
        sys.stdout.write("SQLite database ready.\n")
        sys.stdout.flush()
        await self.storage.start()

        self.db_exporter = DBExportService(
            self.storage,
            default_output_dir=self.paths.db_exports_dir,
        )

        if self.needs_client:
            sys.stdout.write("Connecting to Telegram...\n")
            sys.stdout.flush()
            self.client = TelethonClientWrapper(
                self.settings.session_name
                if os.path.isabs(self.settings.session_name)
                else os.path.join(self.paths.project_root, self.settings.session_name),
                self.settings.api_id,
                self.settings.api_hash,
                max_rps=self.settings.max_rps,
            )
            try:
                await self.client.connect()
            except Exception as exc:
                message = _format_telegram_login_error(exc)
                if message is None:
                    raise
                sys.stderr.write(f"{message}\n")
                sys.stderr.flush()
                sys.exit(1)
            sys.stdout.write("Telegram connection established.\n")
            sys.stdout.flush()
            self.exporter = ExportService(
                self.client, self.storage, event_sink=render_service_event
            )
            self.private_archive = PrivateArchiveService(
                self.client,
                self.storage,
                base_dir=self.paths.private_dialogs_dir,
                event_sink=render_service_event,
            )
            self.channel_exporter = ChannelExportService(
                client=self.client,
                base_dir=self.paths.channel_exports_dir,
                event_sink=render_service_event,
            )
            self.retry_worker = RetryWorker(
                storage=self.storage,
                client=self.client,
                exporter=self.exporter,
                private_archive=self.private_archive,
            )

        self.cleaner = CleanerService(
            self.client,
            self.storage,
            whitelist=self.settings.whitelist_chats,
            include_list=self.settings.include_chats,
            artifact_roots=self.paths.artifact_roots(),
            event_sink=render_service_event,
        )

    async def shutdown(self):
        if self.client:
            await self.client.disconnect()
        if self.storage:
            await self.storage.close()
        if self.pm:
            self.pm.release_lock()

    async def emergency_callback(self):
        """Async callback for signal handling."""
        if self.active_uid and self.db_exporter:
            sys.stdout.write(
                f"\n⚠️ Performing emergency JSON export for User ID: {self.active_uid}...\n"
            )
            path = await self.db_exporter.export_user_messages(
                self.active_uid,
                as_json=True,
                include_date=False,
            )
            if path:
                sys.stdout.write(f"✅ Emergency dump saved to: {path}\n")
            sys.stdout.flush()


def _command_needs_client(command: str) -> bool:
    return command not in (
        "setup",
        "schedule",
        "db-export",
        "report",
        "validate-dataset",
        "inspect-dataset",
        "target",
    )


async def run_cli(runtime: Optional[AppRuntime] = None):
    """Main CLI entry point with subcommand support."""
    parser = build_cli_parser()
    args = parser.parse_args()
    if not args.command:
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            parser.print_help()
            return
    active_runtime = runtime or build_app_runtime(
        require_api_credentials=not args.command or _command_needs_client(args.command),
    )
    with use_lang(active_runtime.settings.lang):
        if not args.command:
            await main_menu(runtime=active_runtime)
            return

        filesystem_handlers = {
            "validate-dataset": _handle_validate_dataset_command,
            "inspect-dataset": _handle_inspect_dataset_command,
        }
        filesystem_handler = filesystem_handlers.get(args.command)
        if filesystem_handler is not None:
            await filesystem_handler(None, args)
            return

        if args.command == "target":
            storage = SQLiteStorage(active_runtime.paths.db_path)
            try:
                await _handle_target_command(SimpleNamespace(storage=storage), args)
            finally:
                await storage.close()
            return

        ctx = CLIContext(
            active_runtime, needs_client=_command_needs_client(args.command)
        )

        try:
            await ctx.initialize()
            handlers = {
                "setup": _handle_setup_command,
                "schedule": _handle_schedule_command,
                "delete": _handle_delete_command,
                "db-export": _handle_db_export_command,
                "export": _handle_export_command,
                "update": _handle_update_command,
                "retry": _handle_retry_command,
                "report": _handle_report_command,
                "clean": _handle_clean_command,
                "export-pm": _handle_export_pm_command,
                "export-channel": _handle_export_channel_command,
                "validate-dataset": _handle_validate_dataset_command,
                "inspect-dataset": _handle_inspect_dataset_command,
                "target": _handle_target_command,
            }
            handler = handlers.get(args.command)
            if handler is not None:
                await handler(ctx, args)

        finally:
            await ctx.shutdown()


async def main_menu(runtime: Optional[AppRuntime] = None):
    """Main interactive menu logic."""
    active_runtime = runtime or build_app_runtime()
    with use_lang(active_runtime.settings.lang):
        ctx = CLIContext(active_runtime, needs_client=True)
        try:
            await ctx.initialize()
            me = await ctx.client.get_me()
            me_id = me.id if me else "Unknown"

            while True:
                render_main_menu(me_id)
                choice = TerminalInput.prompt_with_esc(_("choice_prompt") + ": ")
                if choice is None:
                    continue
                if not await _dispatch_main_menu_choice(ctx, choice):
                    break
        finally:
            await ctx.shutdown()


def main():
    try:
        asyncio.run(run_cli())
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
