import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from tg_msg_manager.application import ApplicationSession
from tg_msg_manager.core.config import Settings
from tg_msg_manager.core.runtime import AppPaths, AppRuntime


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class TestApplicationRuntimeContract(unittest.IsolatedAsyncioTestCase):
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

    def test_application_package_imports_runtime_without_cli_modules(self):
        code = """
import json
import sys

from tg_msg_manager.application import ApplicationSession, RuntimeResourceFactory

del ApplicationSession, RuntimeResourceFactory
cli_modules = sorted(
    name
    for name in sys.modules
    if name == "tg_msg_manager.cli"
    or name.startswith("tg_msg_manager.cli.")
    or name.startswith("tg_msg_manager.cli_")
)
print(json.dumps(cli_modules))
"""
        completed = subprocess.run(
            [sys.executable, "-c", code],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual(json.loads(completed.stdout), [])

    @patch("tg_msg_manager.application.session.setup_logging")
    @patch("tg_msg_manager.application.services.AliasManager")
    @patch("tg_msg_manager.application.services.DBExportService")
    @patch("tg_msg_manager.application.services.CleanerService")
    @patch("tg_msg_manager.application.resources.SQLiteStorage")
    async def test_headless_session_initializes_without_telegram_client(
        self,
        mock_storage_cls,
        mock_cleaner_cls,
        mock_db_exporter_cls,
        mock_alias_cls,
        mock_setup_logging,
    ):
        mock_storage = MagicMock()
        mock_storage.start = AsyncMock()
        mock_storage.close = AsyncMock()
        mock_storage_cls.return_value = mock_storage

        with (
            patch(
                "tg_msg_manager.application.resources.TelethonClientWrapper"
            ) as mock_client_cls,
            patch(
                "tg_msg_manager.application.resources.ProcessManager.acquire_lock",
                return_value=True,
            ),
            patch(
                "tg_msg_manager.application.resources.ProcessManager.setup_async_signals"
            ),
            patch("tg_msg_manager.application.resources.ProcessManager.release_lock"),
        ):
            session = ApplicationSession(
                self.runtime,
                needs_client=False,
                event_sink=lambda event: None,
            )
            await session.initialize()

            self.assertIsNone(session.client)
            self.assertIsNone(session.services.exporter)
            self.assertIsNone(session.services.private_archive)
            self.assertIsNone(session.services.channel_exporter)
            self.assertIsNone(session.services.retry_worker)
            self.assertIs(session.services.cleaner, mock_cleaner_cls.return_value)
            self.assertIs(session.services.db_exporter, mock_db_exporter_cls.return_value)
            self.assertIs(session.services.alias_manager, mock_alias_cls.return_value)
            mock_client_cls.assert_not_called()
            mock_setup_logging.assert_called_once_with(
                level="INFO",
                log_dir="/tmp/tg-msg-manager/LOGS",
            )
            mock_storage.start.assert_awaited_once()

            await session.shutdown()
            mock_storage.close.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
