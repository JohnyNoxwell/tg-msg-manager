import asyncio
import logging
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
from ..application.session import ApplicationSession, ApplicationSessionLockError
from ..core.config import ConfigurationSetupRequired
from ..core.runtime import AppRuntime, build_app_runtime
from ..cli_io import (
    TerminalInput,
    render_main_menu,
    render_service_event,
)
from ..i18n import _, use_lang
from ..infrastructure.storage.sqlite import SQLiteStorage


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


_LIFECYCLE_MESSAGES = {
    "storage_opening": "Opening SQLite database...\n",
    "storage_ready": "SQLite database ready.\n",
    "telegram_connecting": "Connecting to Telegram...\n",
    "telegram_connected": "Telegram connection established.\n",
}


class CLIContext:
    """
    Centralized context for CLI resource management.
    Ensures single initialization of services and graceful shutdown.
    """

    def __init__(self, runtime: AppRuntime, needs_client: bool = True):
        self.runtime = runtime
        self.settings = runtime.settings
        self.paths = runtime.paths
        self.needs_client = needs_client
        self.session = ApplicationSession(
            runtime,
            needs_client=needs_client,
            event_sink=render_service_event,
            lifecycle_event_sink=self._render_lifecycle_event,
            login_error_handler=self._handle_telegram_login_error,
            interrupt_callback=self.emergency_callback,
        )
        self.pm = self.session.pm
        self.storage: Optional[SQLiteStorage] = None
        self.client = None

        self.exporter = None
        self.cleaner = None
        self.db_exporter = None
        self.private_archive = None
        self.channel_exporter = None
        self.retry_worker = None
        self.alias_manager = None

        self.active_uid = None

    def _render_lifecycle_event(self, event: str) -> None:
        message = _LIFECYCLE_MESSAGES.get(event)
        if message is None:
            return
        sys.stdout.write(message)
        sys.stdout.flush()

    def _handle_telegram_login_error(self, error: BaseException) -> bool:
        message = _format_telegram_login_error(error)
        if message is None:
            return False
        sys.stderr.write(f"{message}\n")
        sys.stderr.flush()
        sys.exit(1)

    def _sync_session_attributes(self) -> None:
        self.pm = self.session.pm
        self.storage = self.session.storage
        self.client = self.session.client
        services = self.session.services
        if services is None:
            return
        self.exporter = services.exporter
        self.cleaner = services.cleaner
        self.db_exporter = services.db_exporter
        self.private_archive = services.private_archive
        self.channel_exporter = services.channel_exporter
        self.retry_worker = services.retry_worker
        self.alias_manager = services.alias_manager

    async def initialize(self):
        try:
            await self.session.initialize()
        except ApplicationSessionLockError:
            print(_("error_locked"))
            sys.exit(1)
        finally:
            self._sync_session_attributes()

    async def shutdown(self):
        await self.session.shutdown()
        self._sync_session_attributes()

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
    except ConfigurationSetupRequired as exc:
        sys.stderr.write(f"{exc}\n")
        sys.exit(2)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
