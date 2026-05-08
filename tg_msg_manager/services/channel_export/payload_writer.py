from datetime import datetime
from pathlib import Path
from typing import Callable, Optional, TextIO

from .jsonl_renderer import ChannelJsonlRenderer
from .media_manifest_writer import ChannelMediaManifestWriter
from .models import ChannelExportPlan, ChannelExportRunStats, ChannelPostRecord
from .txt_renderer import ChannelTxtRenderer

WRITE_MODE_OVERWRITE = "write"
WRITE_MODE_APPEND = "append"
ProgressCallback = Optional[Callable[[dict[str, object]], None]]


class ChannelPayloadWriteSession:
    def __init__(
        self,
        *,
        plan: ChannelExportPlan,
        jsonl_renderer: ChannelJsonlRenderer,
        txt_renderer: ChannelTxtRenderer,
        media_manifest_writer: ChannelMediaManifestWriter,
        run_mode: str,
        write_mode: str = WRITE_MODE_OVERWRITE,
        include_jsonl: bool = True,
        include_txt: bool = True,
        progress_callback: ProgressCallback = None,
        progress_interval: int = 100,
    ):
        self.plan = plan
        self.jsonl_renderer = jsonl_renderer
        self.txt_renderer = txt_renderer
        self.media_manifest_writer = media_manifest_writer
        self.run_mode = run_mode
        self.write_mode = write_mode
        self.include_jsonl = include_jsonl
        self.include_txt = include_txt
        self.progress_callback = progress_callback
        self.progress_interval = max(1, int(progress_interval))
        self.message_count = 0
        self.media_count = 0
        self.downloaded_media_count = 0
        self.skipped_media_count = 0
        self.date_from: Optional[datetime] = None
        self.date_to: Optional[datetime] = None
        self.last_exported_message_id: Optional[int] = None
        self._last_progress_message_count = 0
        self._jsonl_handle: Optional[TextIO] = None
        self._txt_handle: Optional[TextIO] = None
        self._media_handle: Optional[TextIO] = None

    def open(self) -> "ChannelPayloadWriteSession":
        self.plan.output_dir.mkdir(parents=True, exist_ok=True)
        Path(self.plan.media_dir).mkdir(parents=True, exist_ok=True)
        file_mode = "a" if self.write_mode == WRITE_MODE_APPEND else "w"
        self._jsonl_handle = Path(self.plan.messages_jsonl_path).open(
            file_mode, encoding="utf-8"
        )
        self._txt_handle = Path(self.plan.messages_txt_path).open(
            file_mode, encoding="utf-8"
        )
        self._media_handle = Path(self.plan.media_manifest_path).open(
            file_mode, encoding="utf-8"
        )
        return self

    def close(self) -> None:
        for handle in (self._jsonl_handle, self._txt_handle, self._media_handle):
            if handle is not None:
                handle.close()
        self._jsonl_handle = None
        self._txt_handle = None
        self._media_handle = None

    def __enter__(self) -> "ChannelPayloadWriteSession":
        return self.open()

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def write_record(self, record: ChannelPostRecord) -> None:
        if (
            self._jsonl_handle is None
            or self._txt_handle is None
            or self._media_handle is None
        ):
            raise RuntimeError("ChannelPayloadWriteSession must be opened before use")

        self.message_count += 1
        if self.date_from is None or record.timestamp < self.date_from:
            self.date_from = record.timestamp
        if self.date_to is None or record.timestamp > self.date_to:
            self.date_to = record.timestamp
        if (
            self.last_exported_message_id is None
            or record.message_id > self.last_exported_message_id
        ):
            self.last_exported_message_id = record.message_id

        if self.include_jsonl:
            self._jsonl_handle.write(self.jsonl_renderer.render_line(record) + "\n")
        if self.include_txt:
            self._txt_handle.write(self.txt_renderer.render_block(record) + "\n")

        for media_record in record.media:
            self.media_count += 1
            if media_record.download_status == "downloaded":
                self.downloaded_media_count += 1
            if media_record.download_status == "skipped_by_mode":
                self.skipped_media_count += 1
            self._media_handle.write(
                self.media_manifest_writer.render_line(media_record) + "\n"
            )

        if self.message_count % self.progress_interval == 0:
            self._emit_progress()

    def finish(self) -> ChannelExportRunStats:
        if (
            self.message_count > 0
            and self._last_progress_message_count != self.message_count
        ):
            self._emit_progress()
        return ChannelExportRunStats(
            mode=self.run_mode,
            posts_exported=self.message_count,
            media_records_added=self.media_count,
            downloaded_media_count=self.downloaded_media_count,
            skipped_media_count=self.skipped_media_count,
            date_from=self.date_from,
            date_to=self.date_to,
            last_exported_message_id=self.last_exported_message_id,
        )

    def _emit_progress(self) -> None:
        if self.progress_callback is None:
            return
        self._last_progress_message_count = self.message_count
        self.progress_callback(
            {
                "processed_posts": self.message_count,
                "media_records": self.media_count,
                "mode": self.run_mode,
                "total_posts": None,
                "last_message_id": self.last_exported_message_id,
            }
        )


class ChannelPayloadWriter:
    def open_session(
        self,
        *,
        plan: ChannelExportPlan,
        jsonl_renderer: ChannelJsonlRenderer,
        txt_renderer: ChannelTxtRenderer,
        media_manifest_writer: ChannelMediaManifestWriter,
        run_mode: str,
        write_mode: str = WRITE_MODE_OVERWRITE,
        include_jsonl: bool = True,
        include_txt: bool = True,
        progress_callback: ProgressCallback = None,
        progress_interval: int = 100,
    ) -> ChannelPayloadWriteSession:
        return ChannelPayloadWriteSession(
            plan=plan,
            jsonl_renderer=jsonl_renderer,
            txt_renderer=txt_renderer,
            media_manifest_writer=media_manifest_writer,
            run_mode=run_mode,
            write_mode=write_mode,
            include_jsonl=include_jsonl,
            include_txt=include_txt,
            progress_callback=progress_callback,
            progress_interval=progress_interval,
        )
