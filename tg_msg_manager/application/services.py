"""Application service bundle construction."""

from dataclasses import dataclass
from typing import Any, Optional

from ..core.runtime import AppRuntime
from ..core.service_events import ServiceEventSink
from ..core.telegram.interface import TelegramClientInterface
from ..services.alias_manager import AliasManager
from ..services.channel_export import ChannelBatchUpdateService, ChannelExportService
from ..services.cleaner import CleanerService
from ..services.db_export.service import DBExportService
from ..services.export.service import ExportService
from ..services.private_archive.service import PrivateArchiveService
from ..services.retry_worker import RetryWorker


@dataclass(frozen=True)
class ServiceBundle:
    exporter: Optional[ExportService]
    cleaner: CleanerService
    db_exporter: DBExportService
    private_archive: Optional[PrivateArchiveService]
    channel_exporter: Optional[ChannelExportService]
    channel_batch_updater: Optional[ChannelBatchUpdateService]
    retry_worker: Optional[RetryWorker]
    alias_manager: AliasManager


def create_service_bundle(
    *,
    runtime: AppRuntime,
    storage: Any,
    client: Optional[TelegramClientInterface],
    needs_client: bool,
    event_sink: ServiceEventSink,
) -> ServiceBundle:
    settings = runtime.settings
    paths = runtime.paths

    db_exporter = DBExportService(
        storage,
        default_output_dir=paths.db_exports_dir,
    )

    exporter = None
    private_archive = None
    channel_exporter = None
    channel_batch_updater = None
    retry_worker = None
    if needs_client:
        exporter = ExportService(client, storage, event_sink=event_sink)
        private_archive = PrivateArchiveService(
            client,
            storage,
            base_dir=paths.private_dialogs_dir,
            event_sink=event_sink,
        )
        channel_exporter = ChannelExportService(
            client=client,
            base_dir=paths.channel_exports_dir,
            event_sink=event_sink,
        )
        channel_batch_updater = ChannelBatchUpdateService(
            channel_exporter=channel_exporter
        )
        retry_worker = RetryWorker(
            storage=storage,
            client=client,
            exporter=exporter,
            private_archive=private_archive,
        )

    cleaner = CleanerService(
        client,
        storage,
        whitelist=settings.whitelist_chats,
        include_list=settings.include_chats,
        artifact_roots=paths.artifact_roots(),
        event_sink=event_sink,
    )
    alias_manager = AliasManager(
        project_root=paths.project_root,
        python_executable=runtime.python_executable,
    )

    return ServiceBundle(
        exporter=exporter,
        cleaner=cleaner,
        db_exporter=db_exporter,
        private_archive=private_archive,
        channel_exporter=channel_exporter,
        channel_batch_updater=channel_batch_updater,
        retry_worker=retry_worker,
        alias_manager=alias_manager,
    )
