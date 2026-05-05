import glob
import logging
import os
from typing import Any, Callable, List, Optional

from ..file_writer import FileRotateWriter
from .jsonl_renderer import DBExportJsonlRenderer
from .models import DBExportWriteResult
from .summary import DBExportSource
from .txt_renderer import DBExportTxtRenderer

logger = logging.getLogger(__name__)


class DBExportPayloadWriter:
    def __init__(
        self,
        *,
        txt_renderer: Optional[DBExportTxtRenderer] = None,
        jsonl_renderer: Optional[DBExportJsonlRenderer] = None,
    ):
        self.txt_renderer = txt_renderer or DBExportTxtRenderer()
        self.jsonl_renderer = jsonl_renderer or DBExportJsonlRenderer()

    def write_batch_size(self, *, as_json: bool, json_profile: str) -> int:
        if not as_json:
            return 100
        if json_profile == "full":
            return 500
        return 1000

    def cleanup_existing_export_files(
        self,
        *,
        output_dir: str,
        user_id: int,
        ext: str,
        output_path: str,
    ) -> None:
        cleanup_patterns = [
            os.path.join(output_dir, f"*_{user_id}{ext}"),
            os.path.join(output_dir, f"*_{user_id}_part*{ext}"),
        ]
        for pattern in cleanup_patterns:
            for old_file in glob.glob(pattern):
                if os.path.abspath(old_file) == os.path.abspath(output_path):
                    continue
                try:
                    os.remove(old_file)
                    logger.debug(
                        "Removed old export file to prevent duplication: %s", old_file
                    )
                except Exception as exc:
                    logger.warning(
                        "Could not remove old export file %s: %s", old_file, exc
                    )

    async def write_payloads(
        self,
        *,
        source: DBExportSource,
        output_path: str,
        as_json: bool,
        json_profile: str,
        expected_count: int,
        overwrite: bool = True,
        on_progress: Optional[Callable[[int, Any], None]] = None,
    ) -> tuple[FileRotateWriter, DBExportWriteResult]:
        writer = FileRotateWriter(
            output_path,
            as_json=as_json,
            overwrite=overwrite,
            persist_every_writes=25 if as_json else 5,
        )
        write_batch_size = self.write_batch_size(
            as_json=as_json, json_profile=json_profile
        )
        msg_lookup = (
            {message.message_id: message for message in (source.messages or [])}
            if not as_json
            else {}
        )

        last_date = None
        last_author_id = None
        pending_blocks: List[str] = []
        pending_count = 0

        async def flush_pending() -> None:
            nonlocal pending_blocks, pending_count
            if not pending_blocks:
                return
            await writer.write_block("".join(pending_blocks), pending_count)
            pending_blocks = []
            pending_count = 0

        count = 0
        iterable = (
            source.export_row_iter_factory()
            if source.export_row_iter_factory is not None
            else source.export_rows
            if source.export_rows is not None
            else (source.messages or [])
        )
        for item in iterable:
            if as_json:
                if (
                    source.export_row_iter_factory is not None
                    or source.export_rows is not None
                ):
                    block = self.jsonl_renderer.render_row(item)
                else:
                    block = self.jsonl_renderer.render_message(
                        item, profile=json_profile
                    )
            else:
                block, last_date, last_author_id = self.txt_renderer.format_block(
                    message=item,
                    msg_lookup=msg_lookup,
                    last_date=last_date,
                    last_author_id=last_author_id,
                )

            pending_blocks.append(block + "\n" if as_json else block)
            pending_count += 1
            count += 1
            if on_progress is not None:
                on_progress(count, item)

            if pending_count >= write_batch_size:
                await flush_pending()

            if count % 100 == 0:
                logger.debug(
                    "Exported %s/%s messages from DB...", count, expected_count
                )

        await flush_pending()
        await writer.finalize()
        return writer, DBExportWriteResult(
            count=count,
            current_part=writer.current_part,
            write_calls=writer.write_calls,
            bytes_written=writer.bytes_written,
            rotation_count=writer.rotation_count,
            state_persist_count=writer.state_persist_count,
        )
