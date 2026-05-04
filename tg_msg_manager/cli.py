import asyncio
import logging
import sys
from typing import Optional

from .cli_commands import (
    _handle_clean_command,
    _handle_db_export_command,
    _handle_delete_command,
    _handle_export_command,
    _handle_export_pm_command,
    _handle_report_command,
    _handle_retry_command,
    _handle_schedule_command,
    _handle_setup_command,
    _handle_update_command,
)
from .cli_menu import (
    _dispatch_main_menu_choice,
    _handle_menu_report,
    _handle_menu_retry,
)
from .cli_parser import build_cli_parser
from .cli_support import (
    _print_scheduler_setup_result,
    get_dirty_target_ids,
    get_safe_user_and_chat,
    resolve_id,
)
from .core.logging import setup_logging
from .core.process import ProcessManager
from .core.runtime import AppRuntime, build_app_runtime
from .core.telemetry import telemetry
from .core.telegram.client import TelethonClientWrapper
from .cli_io import (
    TerminalInput,
    render_main_menu,
    render_service_event,
)
from .i18n import _, use_lang
from .infrastructure.storage.sqlite import SQLiteStorage
from .services.alias_manager import AliasManager
from .services.cleaner import CleanerService
from .services.db_exporter import DBExportService
from .services.exporter import ExportService
from .services.private_archive import PrivateArchiveService
from .services.retry_worker import RetryWorker


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
        self.retry_worker: Optional[RetryWorker] = None
        self.alias_manager = AliasManager(
            project_root=self.paths.project_root,
            python_executable=self.runtime.python_executable,
        )

        self.active_uid = None

    async def initialize(self):
        setup_logging()
        telemetry.reset()
        if not self.pm.acquire_lock():
            print(_("error_locked"))
            sys.exit(1)

        # Setup async signals early
        self.pm.setup_async_signals(asyncio.get_running_loop(), self.emergency_callback)

        self.storage = SQLiteStorage(self.paths.db_path, process_manager=self.pm)
        await self.storage.start()

        self.db_exporter = DBExportService(
            self.storage,
            default_output_dir=self.paths.db_exports_dir,
        )

        if self.needs_client:
            self.client = TelethonClientWrapper(
                self.settings.session_name,
                self.settings.api_id,
                self.settings.api_hash,
                max_rps=self.settings.max_rps,
            )
            await self.client.connect()
            self.exporter = ExportService(
                self.client, self.storage, event_sink=render_service_event
            )
            self.private_archive = PrivateArchiveService(
                self.client,
                self.storage,
                base_dir=self.paths.private_dialogs_dir,
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
    return command not in ("setup", "schedule", "db-export", "report")


async def run_cli(runtime: Optional[AppRuntime] = None):
    """Main CLI entry point with subcommand support."""
    active_runtime = runtime or build_app_runtime()
    with use_lang(active_runtime.settings.lang):
        parser = build_cli_parser()
        args = parser.parse_args()

        if not args.command:
            if not sys.stdin.isatty() or not sys.stdout.isatty():
                parser.print_help()
                return
            await main_menu(runtime=active_runtime)
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
                sys.stdout.write(_("choice_prompt") + ": ")
                sys.stdout.flush()
                char = TerminalInput.get_char()
                if char == "\x1b":
                    continue
                choice = char.upper()
                print(choice)
                if not await _dispatch_main_menu_choice(ctx, choice):
                    break
        finally:
            await ctx.shutdown()


def main():
    try:
        asyncio.run(run_cli(runtime=build_app_runtime()))
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
