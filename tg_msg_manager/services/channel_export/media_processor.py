from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Optional, Tuple

from .event_emitter import ChannelExportEventEmitter
from .media_downloader import ChannelMediaDownloader
from .models import ChannelMediaRecord, ChannelPostRecord


@dataclass
class ChannelMediaProgressTotals:
    processed_media: int = 0
    downloaded: int = 0
    already_exists: int = 0
    skipped_by_size: int = 0
    skipped_by_type: int = 0
    failed: int = 0


class ChannelExportMediaProcessor:
    def __init__(
        self,
        *,
        media_downloader: ChannelMediaDownloader,
        event_emitter: ChannelExportEventEmitter,
    ):
        self.media_downloader = media_downloader
        self.event_emitter = event_emitter
        self._progress_totals = ChannelMediaProgressTotals()

    def reset_progress(self) -> None:
        self._progress_totals = ChannelMediaProgressTotals()

    async def prepare_record(
        self,
        *,
        record: ChannelPostRecord,
        media_mode: str,
        media_ref: Any,
        output_dir: Path,
        max_media_size: Optional[int],
        media_types: Optional[Tuple[str, ...]],
    ) -> ChannelPostRecord:
        if media_mode != "full" or not record.media:
            return record

        updated_media = []
        for media_record in record.media:
            updated_record = await self.media_downloader.download(
                record=media_record,
                media_ref=media_ref,
                output_dir=output_dir,
                max_media_size=max_media_size,
                allowed_media_types=media_types,
            )
            updated_media.append(updated_record)
            self._emit_media_event(updated_record)

        self._emit_media_progress(updated_media)
        return replace(record, media=tuple(updated_media))

    def _emit_media_event(self, record: ChannelMediaRecord) -> None:
        payload = {
            "message_id": record.message_id,
            "media_id": record.media_id,
            "media_type": record.media_type,
            "status": record.download_status,
            "local_path": record.local_path,
            "error": record.error,
        }
        if record.download_status in ("downloaded", "already_exists"):
            self.event_emitter.emit_media_downloaded(**payload)
        elif record.download_status == "failed":
            self.event_emitter.emit_media_failed(**payload)
        else:
            self.event_emitter.emit_media_skipped(**payload)

    def _emit_media_progress(self, media_records: list[ChannelMediaRecord]) -> None:
        for record in media_records:
            self._progress_totals.processed_media += 1
            if record.download_status == "downloaded":
                self._progress_totals.downloaded += 1
            elif record.download_status == "already_exists":
                self._progress_totals.already_exists += 1
            elif record.download_status == "skipped_by_size":
                self._progress_totals.skipped_by_size += 1
            elif record.download_status == "skipped_by_type":
                self._progress_totals.skipped_by_type += 1
            elif record.download_status == "failed":
                self._progress_totals.failed += 1

        self.event_emitter.emit_media_progress(
            processed_media=self._progress_totals.processed_media,
            downloaded=self._progress_totals.downloaded,
            already_exists=self._progress_totals.already_exists,
            skipped_by_size=self._progress_totals.skipped_by_size,
            skipped_by_type=self._progress_totals.skipped_by_type,
            failed=self._progress_totals.failed,
            elapsed_seconds=round(self.event_emitter.elapsed_seconds(), 3),
        )
