from pathlib import Path
from typing import Optional, TextIO

from ..atomic_writer import AtomicTextFile
from .jsonl_renderer import ChannelDiscussionJsonlRenderer
from .models import (
    DISCUSSION_THREAD_STATUS_FAILED,
    DISCUSSION_THREAD_STATUS_NO_COMMENTS,
    DISCUSSION_THREAD_STATUS_NOT_AVAILABLE,
    DISCUSSION_THREAD_STATUS_NOT_LINKED,
    DISCUSSION_THREAD_STATUS_PARTIAL,
    ChannelDiscussionCommentRecord,
    ChannelDiscussionMetadataRecord,
    ChannelDiscussionRunStats,
    ChannelDiscussionThreadRecord,
)
from .txt_renderer import ChannelDiscussionTxtRenderer

WRITE_MODE_OVERWRITE = "write"
WRITE_MODE_APPEND = "append"


class ChannelDiscussionPayloadWriteSession:
    def __init__(
        self,
        *,
        comments_jsonl_path: Path,
        comments_txt_path: Path,
        threads_jsonl_path: Path,
        jsonl_renderer: ChannelDiscussionJsonlRenderer,
        txt_renderer: ChannelDiscussionTxtRenderer,
        run_mode: str,
        write_mode: str = WRITE_MODE_OVERWRITE,
    ):
        self.comments_jsonl_path = Path(comments_jsonl_path)
        self.comments_txt_path = Path(comments_txt_path)
        self.threads_jsonl_path = Path(threads_jsonl_path)
        self.jsonl_renderer = jsonl_renderer
        self.txt_renderer = txt_renderer
        self.run_mode = run_mode
        self.write_mode = write_mode
        self._comments_jsonl_handle: Optional[TextIO] = None
        self._comments_txt_handle: Optional[TextIO] = None
        self._threads_jsonl_handle: Optional[TextIO] = None
        self._comments_jsonl_file: Optional[AtomicTextFile] = None
        self._comments_txt_file: Optional[AtomicTextFile] = None
        self._threads_jsonl_file: Optional[AtomicTextFile] = None
        self.thread_count = 0
        self.comment_count = 0
        self.failed_thread_count = 0
        self.partial_thread_count = 0
        self.not_linked_thread_count = 0
        self.not_available_thread_count = 0
        self.no_comments_thread_count = 0

    def open(self) -> "ChannelDiscussionPayloadWriteSession":
        self.comments_jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        file_mode = "a" if self.write_mode == WRITE_MODE_APPEND else "w"
        self._comments_jsonl_file = AtomicTextFile(
            self.comments_jsonl_path, mode=file_mode
        )
        self._comments_txt_file = AtomicTextFile(self.comments_txt_path, mode=file_mode)
        self._threads_jsonl_file = AtomicTextFile(
            self.threads_jsonl_path, mode=file_mode
        )
        try:
            self._comments_jsonl_handle = self._comments_jsonl_file.open()
            self._comments_txt_handle = self._comments_txt_file.open()
            self._threads_jsonl_handle = self._threads_jsonl_file.open()
        except Exception:
            self.rollback()
            raise
        return self

    def close(self) -> None:
        for handle in (
            self._comments_jsonl_handle,
            self._comments_txt_handle,
            self._threads_jsonl_handle,
        ):
            if handle is not None:
                handle.close()
        self._comments_jsonl_handle = None
        self._comments_txt_handle = None
        self._threads_jsonl_handle = None

    def commit(self) -> None:
        for atomic_file in (
            self._comments_jsonl_file,
            self._comments_txt_file,
            self._threads_jsonl_file,
        ):
            if atomic_file is not None:
                atomic_file.commit()

    def rollback(self) -> None:
        for atomic_file in (
            self._comments_jsonl_file,
            self._comments_txt_file,
            self._threads_jsonl_file,
        ):
            if atomic_file is not None:
                atomic_file.rollback()

    def __enter__(self) -> "ChannelDiscussionPayloadWriteSession":
        return self.open()

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc_type is None:
            self.commit()
        else:
            self.rollback()

    def write_thread(self, record: ChannelDiscussionThreadRecord) -> None:
        if self._threads_jsonl_handle is None:
            raise RuntimeError(
                "ChannelDiscussionPayloadWriteSession must be opened before use"
            )
        self.thread_count += 1
        if record.status == DISCUSSION_THREAD_STATUS_FAILED:
            self.failed_thread_count += 1
        elif record.status == DISCUSSION_THREAD_STATUS_PARTIAL:
            self.partial_thread_count += 1
        elif record.status == DISCUSSION_THREAD_STATUS_NOT_LINKED:
            self.not_linked_thread_count += 1
        elif record.status == DISCUSSION_THREAD_STATUS_NOT_AVAILABLE:
            self.not_available_thread_count += 1
        elif record.status == DISCUSSION_THREAD_STATUS_NO_COMMENTS:
            self.no_comments_thread_count += 1
        self._threads_jsonl_handle.write(
            self.jsonl_renderer.render_thread_line(record) + "\n"
        )

    def write_comment(self, record: ChannelDiscussionCommentRecord) -> None:
        if self._comments_jsonl_handle is None or self._comments_txt_handle is None:
            raise RuntimeError(
                "ChannelDiscussionPayloadWriteSession must be opened before use"
            )
        self.comment_count += 1
        self._comments_jsonl_handle.write(
            self.jsonl_renderer.render_comment_line(record) + "\n"
        )
        self._comments_txt_handle.write(
            self.txt_renderer.render_comment_block(record) + "\n"
        )

    def finish(self) -> ChannelDiscussionRunStats:
        return ChannelDiscussionRunStats(
            mode=self.run_mode,
            thread_count=self.thread_count,
            comment_count=self.comment_count,
            failed_thread_count=self.failed_thread_count,
            partial_thread_count=self.partial_thread_count,
            not_linked_thread_count=self.not_linked_thread_count,
            not_available_thread_count=self.not_available_thread_count,
            no_comments_thread_count=self.no_comments_thread_count,
        )


class ChannelDiscussionPayloadWriter:
    def open_session(
        self,
        *,
        comments_jsonl_path: Path,
        comments_txt_path: Path,
        threads_jsonl_path: Path,
        jsonl_renderer: ChannelDiscussionJsonlRenderer,
        txt_renderer: ChannelDiscussionTxtRenderer,
        run_mode: str,
        write_mode: str = WRITE_MODE_OVERWRITE,
    ) -> ChannelDiscussionPayloadWriteSession:
        return ChannelDiscussionPayloadWriteSession(
            comments_jsonl_path=comments_jsonl_path,
            comments_txt_path=comments_txt_path,
            threads_jsonl_path=threads_jsonl_path,
            jsonl_renderer=jsonl_renderer,
            txt_renderer=txt_renderer,
            run_mode=run_mode,
            write_mode=write_mode,
        )


class ChannelDiscussionMetadataWriteSession:
    def __init__(
        self,
        *,
        metadata_jsonl_path: Path,
        jsonl_renderer: ChannelDiscussionJsonlRenderer,
        run_mode: str,
        write_mode: str = WRITE_MODE_OVERWRITE,
    ):
        self.metadata_jsonl_path = Path(metadata_jsonl_path)
        self.jsonl_renderer = jsonl_renderer
        self.run_mode = run_mode
        self.write_mode = write_mode
        self._metadata_handle: Optional[TextIO] = None
        self._metadata_file: Optional[AtomicTextFile] = None
        self.metadata_count = 0

    def open(self) -> "ChannelDiscussionMetadataWriteSession":
        self.metadata_jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        file_mode = "a" if self.write_mode == WRITE_MODE_APPEND else "w"
        self._metadata_file = AtomicTextFile(self.metadata_jsonl_path, mode=file_mode)
        try:
            self._metadata_handle = self._metadata_file.open()
        except Exception:
            self.rollback()
            raise
        return self

    def close(self) -> None:
        if self._metadata_handle is not None:
            self._metadata_handle.close()
        self._metadata_handle = None

    def commit(self) -> None:
        if self._metadata_file is not None:
            self._metadata_file.commit()

    def rollback(self) -> None:
        if self._metadata_file is not None:
            self._metadata_file.rollback()

    def __enter__(self) -> "ChannelDiscussionMetadataWriteSession":
        return self.open()

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
        if exc_type is None:
            self.commit()
        else:
            self.rollback()

    def write_metadata(self, record: ChannelDiscussionMetadataRecord) -> None:
        if self._metadata_handle is None:
            raise RuntimeError(
                "ChannelDiscussionMetadataWriteSession must be opened before use"
            )
        self.metadata_count += 1
        self._metadata_handle.write(
            self.jsonl_renderer.render_metadata_line(record) + "\n"
        )

    def finish(self) -> ChannelDiscussionRunStats:
        return ChannelDiscussionRunStats(
            mode=self.run_mode,
            thread_count=self.metadata_count,
            comment_count=0,
            failed_thread_count=0,
        )


class ChannelDiscussionMetadataPayloadWriter:
    def open_session(
        self,
        *,
        metadata_jsonl_path: Path,
        jsonl_renderer: ChannelDiscussionJsonlRenderer,
        run_mode: str,
        write_mode: str = WRITE_MODE_OVERWRITE,
    ) -> ChannelDiscussionMetadataWriteSession:
        return ChannelDiscussionMetadataWriteSession(
            metadata_jsonl_path=metadata_jsonl_path,
            jsonl_renderer=jsonl_renderer,
            run_mode=run_mode,
            write_mode=write_mode,
        )
