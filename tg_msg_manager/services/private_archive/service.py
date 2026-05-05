import asyncio
import logging
import os
from typing import Any, Optional

from ...core.models.message import MessageData
from ...core.models.payloads.private_archive import (
    PrivateArchiveMediaStats,
    PrivateArchiveTransferStats,
)
from ...core.telegram.interface import TelegramClientInterface
from ...core.telemetry import telemetry
from ...infrastructure.storage.contracts.private_archive_storage import (
    PrivateArchiveStorage,
)
from ..file_writer import FileRotateWriter
from .archive_writer import PrivateArchiveWriter
from .event_emitter import PrivateArchiveEventEmitter
from .media_policy import PrivateArchiveMediaPolicy
from .planner import PrivateArchivePlanner
from .source_resolver import PrivateArchiveSourceResolver
from .state_manager import PrivateArchiveStateManager

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

    @staticmethod
    def _initial_media_stats() -> PrivateArchiveMediaStats:
        return PrivateArchiveMediaStats()

    @staticmethod
    def _initial_archive_stats() -> PrivateArchiveTransferStats:
        return PrivateArchiveTransferStats()

    async def _download_media(
        self, message: MessageData, media_dir: str
    ) -> Optional[str]:
        if not self.media_policy.should_download(message):
            return None
        target_path = self.media_policy.target_path(
            media_dir=media_dir, message=message
        )
        async with self.download_semaphore:
            return await self.client.download_media(message.media_ref, file=target_path)

    async def _process_archive_media(
        self,
        message: MessageData,
        *,
        media_dir: str,
        stats: PrivateArchiveMediaStats,
        archive_stats: PrivateArchiveTransferStats,
    ) -> None:
        if not message.media_type:
            return

        self.media_policy.track_media_stats(stats, message.media_type)
        telemetry.track_messages(1)
        downloaded_path = await self._download_media(message, media_dir)
        if downloaded_path:
            archive_stats.downloaded += 1
            self.event_emitter.emit_media_saved(
                filename=os.path.basename(downloaded_path),
                path=downloaded_path,
            )
        else:
            archive_stats.skipped += 1

    async def _archive_message(
        self,
        message: MessageData,
        *,
        user_id: int,
        media_dir: str,
        writer: FileRotateWriter,
        stats: PrivateArchiveMediaStats,
        archive_stats: PrivateArchiveTransferStats,
    ) -> None:
        await self.storage.save_message(message, target_id=user_id)
        await self._process_archive_media(
            message,
            media_dir=media_dir,
            stats=stats,
            archive_stats=archive_stats,
        )
        await self.archive_writer.append_message(writer, message)

    async def _archive_message_stream(
        self,
        user_entity: Any,
        *,
        user_id: int,
        last_id: int,
        media_dir: str,
        writer: FileRotateWriter,
    ) -> tuple[int, PrivateArchiveMediaStats, PrivateArchiveTransferStats]:
        count = 0
        stats = self._initial_media_stats()
        archive_stats = self._initial_archive_stats()

        async for message in self.client.iter_messages(
            user_entity, limit=None, offset_id=0
        ):
            if message.message_id <= last_id:
                break

            await self._archive_message(
                message,
                user_id=user_id,
                media_dir=media_dir,
                writer=writer,
                stats=stats,
                archive_stats=archive_stats,
            )
            count += 1
            if count % 5 == 0:
                self.event_emitter.emit_progress(
                    count=count,
                    stats=stats,
                    archive_stats=archive_stats,
                )

        return count, stats, archive_stats

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
        count, stats, archive_stats = await self._archive_message_stream(
            user_entity,
            user_id=archive_context.user_id,
            last_id=last_id,
            media_dir=archive_context.media_dir,
            writer=writer,
        )
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
