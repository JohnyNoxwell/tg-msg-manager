import os
from typing import Any

from ...core.models.message import MessageData
from ...core.models.payloads.private_archive import (
    PrivateArchiveMediaStats,
    PrivateArchiveTransferStats,
)
from ...core.telemetry import telemetry
from ..file_writer import FileRotateWriter
from .archive_writer import PrivateArchiveWriter
from .event_emitter import PrivateArchiveEventEmitter
from .media_downloader import PrivateArchiveMediaDownloader
from .media_policy import PrivateArchiveMediaPolicy


class PrivateArchiveStreamProcessor:
    def __init__(
        self,
        *,
        client: Any,
        storage: Any,
        archive_writer: PrivateArchiveWriter,
        event_emitter: PrivateArchiveEventEmitter,
        media_policy: PrivateArchiveMediaPolicy,
        media_downloader: PrivateArchiveMediaDownloader,
    ):
        self.client = client
        self.storage = storage
        self.archive_writer = archive_writer
        self.event_emitter = event_emitter
        self.media_policy = media_policy
        self.media_downloader = media_downloader

    @staticmethod
    def initial_media_stats() -> PrivateArchiveMediaStats:
        return PrivateArchiveMediaStats()

    @staticmethod
    def initial_archive_stats() -> PrivateArchiveTransferStats:
        return PrivateArchiveTransferStats()

    async def process_media(
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
        downloaded_path = await self.media_downloader.download(
            message,
            media_dir=media_dir,
        )
        if downloaded_path:
            archive_stats.downloaded += 1
            self.event_emitter.emit_media_saved(
                filename=os.path.basename(downloaded_path),
                path=downloaded_path,
            )
        else:
            archive_stats.skipped += 1

    async def process_message(
        self,
        message: MessageData,
        *,
        user_id: int,
        media_dir: str,
        writer: FileRotateWriter,
        stats: PrivateArchiveMediaStats,
        archive_stats: PrivateArchiveTransferStats,
    ) -> None:
        await self.storage.save_message(message, target_id=user_id, flush=False)
        await self.process_media(
            message,
            media_dir=media_dir,
            stats=stats,
            archive_stats=archive_stats,
        )
        await self.archive_writer.append_message(writer, message)

    async def process_stream(
        self,
        user_entity: Any,
        *,
        user_id: int,
        last_id: int,
        media_dir: str,
        writer: FileRotateWriter,
    ) -> tuple[int, PrivateArchiveMediaStats, PrivateArchiveTransferStats]:
        count = 0
        stats = self.initial_media_stats()
        archive_stats = self.initial_archive_stats()

        async for message in self.client.iter_messages(
            user_entity, limit=None, offset_id=0
        ):
            if message.message_id <= last_id:
                break

            await self.process_message(
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
