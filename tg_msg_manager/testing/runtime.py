import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from ..infrastructure.storage.sqlite import SQLiteStorage
from ..services.db_export.service import DBExportService
from ..services.export.service import ExportService
from ..services.private_archive.service import PrivateArchiveService
from ..services.reporting import ReportCollector
from ..services.retry_worker import RetryWorker
from .fake_telegram import FakeTelegramClient


@dataclass(frozen=True)
class FixtureRuntimePaths:
    root: Path
    db_path: Path
    db_exports_dir: Path
    private_dialogs_dir: Path
    public_groups_dir: Path


class FixtureRuntime:
    def __init__(self, *, tmpdir: tempfile.TemporaryDirectory[str], dataset: Any):
        self._tmpdir = tmpdir
        root = Path(tmpdir.name)
        self.paths = FixtureRuntimePaths(
            root=root,
            db_path=root / "messages.db",
            db_exports_dir=root / "DB_EXPORTS",
            private_dialogs_dir=root / "PRIVAT_DIALOGS",
            public_groups_dir=root / "PUBLIC_GROUPS",
        )
        self.paths.db_exports_dir.mkdir(parents=True, exist_ok=True)
        self.paths.private_dialogs_dir.mkdir(parents=True, exist_ok=True)
        self.paths.public_groups_dir.mkdir(parents=True, exist_ok=True)

        self.dataset = dataset
        self.client = FakeTelegramClient(dataset)
        self.storage = SQLiteStorage(str(self.paths.db_path))
        self.exporter = ExportService(self.client, self.storage)
        self.db_exporter = DBExportService(
            self.storage,
            default_output_dir=str(self.paths.db_exports_dir),
        )
        self.private_archive = PrivateArchiveService(
            self.client,
            self.storage,
            base_dir=str(self.paths.private_dialogs_dir),
        )
        self.retry_worker = RetryWorker(
            storage=self.storage,
            client=self.client,
            exporter=self.exporter,
            private_archive=self.private_archive,
        )

    @classmethod
    async def create(cls, dataset: Any) -> "FixtureRuntime":
        runtime = cls(
            tmpdir=tempfile.TemporaryDirectory(prefix="tg-msg-fixture-"),
            dataset=dataset,
        )
        await runtime.storage.start()
        await runtime.client.connect()
        return runtime

    def replace_dataset(self, dataset: Any) -> None:
        self.dataset = dataset
        self.client.replace_dataset(dataset)

    def build_report(self, *, now_ts: Optional[int] = None):
        collector = ReportCollector(
            storage=self.storage,
            exports_dir=self.paths.db_exports_dir,
            now_ts=now_ts,
        )
        return collector.collect()

    async def close(self) -> None:
        await self.client.disconnect()
        await self.storage.close()
        self._tmpdir.cleanup()
