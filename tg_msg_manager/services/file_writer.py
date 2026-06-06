import os
import asyncio
import logging

from ..core.telemetry import telemetry
from .file_writer_state import WriterState, WriterStateStore

logger = logging.getLogger(__name__)


class FileRotateWriter:
    """
    Handles writing content to files with automatic rotation into multiple parts.
    Ensures that individual files do not exceed a certain message count.
    """

    def __init__(
        self,
        base_path: str,
        as_json: bool = False,
        max_msgs: int = 5000,
        overwrite: bool = False,
        persist_every_writes: int = 1,
    ):
        self.base_path = base_path
        self.as_json = as_json
        self.max_msgs = max_msgs
        self.persist_every_writes = max(1, persist_every_writes)
        self.lock = asyncio.Lock()

        self.directory = os.path.dirname(base_path)
        if self.directory and not os.path.exists(self.directory):
            os.makedirs(self.directory)

        self.filename = os.path.basename(base_path)
        self.name_no_ext, self.ext = os.path.splitext(self.filename)
        self.state_dir = os.path.join(self.directory, ".writer_state")
        self.state_path = os.path.join(self.state_dir, f"{self.name_no_ext}.json")
        self.legacy_state_path = os.path.join(
            self.directory, f".{self.name_no_ext}.writer_state.json"
        )
        self.state_store = WriterStateStore(self.state_path, self.legacy_state_path)

        self.current_part = 1
        self.current_count = 0
        self.bytes_written = 0
        self.write_calls = 0
        self.state_persist_count = 0
        self.rotation_count = 0
        self._writes_since_persist = 0

        if overwrite:
            self._cleanup_existing_files()

        self.current_file_path = self._get_path()
        self._detect_current_state()

    def _cleanup_existing_files(self):
        """Removes all parts of the export if a full resync is requested."""
        part = 1
        while True:
            path = self._get_path_for_part(part)
            if os.path.exists(path):
                try:
                    os.remove(path)
                    logger.debug(f"Removed old export file: {path}")
                except Exception as e:
                    logger.error(f"Error removing {path}: {e}")
                part += 1
            else:
                break
        self._remove_state_file(self.state_path)
        self._remove_state_file(self.legacy_state_path)

    def _remove_state_file(self, path: str):
        if os.path.exists(path):
            try:
                self.state_store.remove(path)
            except Exception as e:
                logger.error(f"Error removing writer state {path}: {e}")

    def _get_path_for_part(self, part: int) -> str:
        if part == 1:
            return os.path.join(self.directory, f"{self.name_no_ext}{self.ext}")
        return os.path.join(self.directory, f"{self.name_no_ext}_part{part}{self.ext}")

    def _get_path(self) -> str:
        return self._get_path_for_part(self.current_part)

    def _persist_state_sync(self):
        self.state_store.save(
            WriterState(
                current_part=self.current_part,
                current_count=self.current_count,
            )
        )
        self.state_persist_count += 1
        telemetry.track_counter("file_writer.state_persists", 1)

    async def _maybe_persist_state(self, force: bool = False):
        if force or self._writes_since_persist >= self.persist_every_writes:
            await asyncio.to_thread(self._persist_state_sync)
            self._writes_since_persist = 0

    @staticmethod
    def _append_content_sync(path: str, content: str):
        with open(path, "a", encoding="utf-8") as f:
            f.write(content)
            f.flush()

    def _detect_current_state(self):
        """Finds the highest part number that exists and counts its messages."""
        recovery = self.state_store.recover(
            path_for_part=self._get_path_for_part,
            as_json=self.as_json,
            max_msgs=self.max_msgs,
        )
        self.current_part = recovery.state.current_part
        self.current_count = recovery.state.current_count
        self.current_file_path = self._get_path()
        if recovery.persist:
            self._persist_state_sync()
        if recovery.remove_legacy:
            self._remove_state_file(self.legacy_state_path)

    async def write_block(self, content: str, msg_count: int = 1):
        """Writes a block of content to the current file, rotating if needed."""
        async with self.lock:
            rotated = False
            if self.current_count + msg_count > self.max_msgs:
                self.current_part += 1
                self.current_count = 0
                self.current_file_path = self._get_path()
                self.rotation_count += 1
                rotated = True
                telemetry.track_counter("file_writer.rotations", 1)
                logger.info(
                    f"File limit reached. Rotating to part {self.current_part}: {self.current_file_path}"
                )

            started_at = asyncio.get_running_loop().time()
            await asyncio.to_thread(
                self._append_content_sync, self.current_file_path, content
            )
            telemetry.track_duration(
                "file_writer.write_block.total",
                asyncio.get_running_loop().time() - started_at,
            )
            self.current_count += msg_count
            self.bytes_written += len(content.encode("utf-8"))
            self.write_calls += 1
            self._writes_since_persist += 1
            telemetry.track_counter("file_writer.write_calls", 1)
            telemetry.track_counter("file_writer.messages_written", msg_count)
            telemetry.track_counter(
                "file_writer.bytes_written", len(content.encode("utf-8"))
            )
            await self._maybe_persist_state(force=rotated)

    async def finalize(self):
        async with self.lock:
            await self._maybe_persist_state(force=True)
