import unittest


class TestCompatibilityImports(unittest.TestCase):
    def test_db_exporter_compat_import(self):
        from tg_msg_manager.services.db_export.service import DBExportService as New
        from tg_msg_manager.services.db_exporter import DBExportService as Old

        self.assertIs(Old, New)

    def test_private_archive_compat_import(self):
        from tg_msg_manager.services.private_archive import (
            PrivateArchiveService as Compat,
        )
        from tg_msg_manager.services.private_archive.service import (
            PrivateArchiveService as Direct,
        )

        self.assertIs(Compat, Direct)

    def test_service_payloads_compat_imports(self):
        from tg_msg_manager.core.models.payloads.export import (
            ExportSyncStartedPayload as ExportSyncStartedPayloadDirect,
        )
        from tg_msg_manager.core.models.payloads.private_archive import (
            PrivateArchiveStartedPayload as PrivateArchiveStartedPayloadDirect,
        )
        from tg_msg_manager.core.models.service_payloads import (
            ExportSyncStartedPayload,
            PrivateArchiveStartedPayload,
        )

        self.assertIs(ExportSyncStartedPayload, ExportSyncStartedPayloadDirect)
        self.assertIs(
            PrivateArchiveStartedPayload,
            PrivateArchiveStartedPayloadDirect,
        )


if __name__ == "__main__":
    unittest.main()
