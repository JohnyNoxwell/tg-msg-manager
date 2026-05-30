import asyncio
import logging
from typing import Any, Optional

from ...core.telegram.interface import TelegramClientInterface
from ...infrastructure.storage.contracts.private_archive_storage import (
    PrivateArchiveStorage,
)
from .archive_writer import PrivateArchiveWriter
from .event_emitter import PrivateArchiveEventEmitter
from .media_downloader import PrivateArchiveMediaDownloader
from .media_policy import PrivateArchiveMediaPolicy
from .planner import PrivateArchivePlanner
from .source_resolver import PrivateArchiveSourceResolver
from .state_manager import PrivateArchiveStateManager
from .stream_processor import PrivateArchiveStreamProcessor

logger = logging.getLogger(__name__)


class PrivateArchiveService:
    """
    Thin orchestration facade for PM archive creation.
    """

    def __init__(
        self,
        client: TelegramClientInterface,
        storage: PrivateArchiveStorage,
        base_dir: str = "PRIVAT_DIALOGS",
        max_file_size: int = 50 * 1024 * 1024,
        event_sink=None,
        source_resolver: Optional[PrivateArchiveSourceResolver] = None,
        planner: Optional[PrivateArchivePlanner] = None,
        media_policy: Optional[PrivateArchiveMediaPolicy] = None,
        archive_writer: Optional[PrivateArchiveWriter] = None,
        state_manager: Optional[PrivateArchiveStateManager] = None,
        event_emitter: Optional[PrivateArchiveEventEmitter] = None,
        media_downloader: Optional[PrivateArchiveMediaDownloader] = None,
        stream_processor: Optional[PrivateArchiveStreamProcessor] = None,
    ):
        self.client = client
        self.storage = storage
        self.base_dir = base_dir
        self.max_file_size = max_file_size
        self.download_semaphore = asyncio.Semaphore(3)
        self.source_resolver = source_resolver or PrivateArchiveSourceResolver()
        self.planner = planner or PrivateArchivePlanner(base_dir=base_dir)
        self.media_policy = media_policy or PrivateArchiveMediaPolicy()
        self.archive_writer = archive_writer or PrivateArchiveWriter()
        self.state_manager = state_manager or PrivateArchiveStateManager(storage)
        self.event_emitter = event_emitter or PrivateArchiveEventEmitter(event_sink)
        self.media_downloader = media_downloader or PrivateArchiveMediaDownloader(
            client,
            media_policy=self.media_policy,
            download_semaphore=self.download_semaphore,
        )
        self.stream_processor = stream_processor or PrivateArchiveStreamProcessor(
            client=client,
            storage=storage,
            archive_writer=self.archive_writer,
            event_emitter=self.event_emitter,
            media_policy=self.media_policy,
            media_downloader=self.media_downloader,
        )

    async def archive_pm(self, user_entity: Any):
        descriptor = self.source_resolver.resolve(user_entity)
        archive_context = self.planner.build_context(descriptor)
        self.archive_writer.ensure_archive_dirs(archive_context.media_dir)

        writer = self.archive_writer.create_log_writer(archive_context.chat_log_path)
        last_id = self.state_manager.get_last_msg_id(archive_context.user_id)
        self.state_manager.register_target(
            user_id=archive_context.user_id,
            target_name=archive_context.target_name,
        )
        self.event_emitter.emit_started(
            target_name=archive_context.target_name,
            user_id=archive_context.user_id,
            user_dir=archive_context.user_dir,
            last_id=last_id,
        )
        logger.info(
            "PM Archive start for %s. Last ID: %s", archive_context.user_id, last_id
        )
        count, stats, archive_stats = await self.stream_processor.process_stream(
            user_entity,
            user_id=archive_context.user_id,
            last_id=last_id,
            media_dir=archive_context.media_dir,
            writer=writer,
        )
        await self.storage.flush()
        self.event_emitter.emit_completed(
            target_name=archive_context.target_name,
            count=count,
            stats=stats,
            archive_stats=archive_stats,
        )
        self.state_manager.mark_synced(archive_context.user_id)
        logger.info(
            "PM Archive complete for %s. %s messages, %s media, downloaded=%s, skipped=%s.",
            archive_context.user_id,
            count,
            stats.total,
            archive_stats.downloaded,
            archive_stats.skipped,
        )
        return archive_context.user_dir
