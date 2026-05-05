import importlib
import unittest
from pathlib import Path


class TestArchitectureWrappers(unittest.TestCase):
    def _read_text(self, path: str) -> str:
        return Path(path).read_text(encoding="utf-8")

    def test_db_exporter_wrapper_has_no_active_class_definition(self):
        text = self._read_text("tg_msg_manager/services/db_exporter.py")
        self.assertNotIn("class DBExportService", text)

    def test_db_exporter_compat_import_points_to_new_service(self):
        from tg_msg_manager.services.db_export.service import DBExportService
        from tg_msg_manager.services.db_exporter import (
            DBExportService as CompatDBExportService,
        )

        self.assertIs(CompatDBExportService, DBExportService)

    def test_private_archive_wrapper_has_no_active_class_definition(self):
        text = self._read_text("tg_msg_manager/services/private_archive.py")
        self.assertNotIn("class PrivateArchiveService", text)

    def test_private_archive_import_resolution_uses_package(self):
        private_archive = importlib.import_module(
            "tg_msg_manager.services.private_archive"
        )

        self.assertTrue(
            getattr(private_archive, "__file__", "").endswith(
                "services/private_archive/__init__.py"
            )
        )
        self.assertTrue(hasattr(private_archive, "PrivateArchiveService"))

    def test_private_archive_compat_import_points_to_new_service(self):
        from tg_msg_manager.services.private_archive import (
            PrivateArchiveService as CompatPrivateArchiveService,
        )
        from tg_msg_manager.services.private_archive.service import (
            PrivateArchiveService,
        )

        self.assertIs(CompatPrivateArchiveService, PrivateArchiveService)

    def test_simple_wrapper_files_remain_small(self):
        wrapper_paths = [
            Path("tg_msg_manager/services/exporter.py"),
            Path("tg_msg_manager/services/context_engine.py"),
            Path("tg_msg_manager/services/db_exporter.py"),
            Path("tg_msg_manager/services/private_archive.py"),
        ]

        for path in wrapper_paths:
            with self.subTest(path=str(path)):
                self.assertLessEqual(
                    len(path.read_text(encoding="utf-8").splitlines()),
                    20,
                )

    def test_service_payloads_is_compatibility_aggregator(self):
        text = self._read_text("tg_msg_manager/core/models/service_payloads.py")
        self.assertIn("Compatibility aggregator", text)
        self.assertIn("core.models.payloads", text)

    def test_storage_interface_stays_contract_only(self):
        text = self._read_text("tg_msg_manager/infrastructure/storage/interface.py")
        self.assertIn("Compatibility aggregator", text)
        self.assertNotIn("sqlite3", text)
        self.assertNotIn("cursor.execute(", text)
        self.assertNotIn("connection.execute(", text)
        self.assertNotIn("SQLiteStorage", text)


if __name__ == "__main__":
    unittest.main()
