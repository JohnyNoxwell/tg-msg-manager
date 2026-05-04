import os
import glob
import logging
from time import perf_counter
from typing import Any, Dict, List, Optional

from .file_writer import FileRotateWriter
from .db_export import (
    DBExportSource as _DBExportSource,
    build_export_fingerprint,
    can_skip_export,
    format_txt_export_block,
    load_export_manifest,
    load_export_source,
    manifest_dir,
    manifest_path,
    persist_export_manifest,
    prepare_export_plan,
    serialize_json_message,
    serialize_row_as_ai_jsonl,
)
from ..infrastructure.storage.interface import DBExportStorage
from ..infrastructure.storage.records import (
    UserExportRow,
)
from ..core.models.message import MessageData
from ..core.telemetry import telemetry

logger = logging.getLogger(__name__)


class DBExportService:
    """
    Service responsible for exporting cached messages from the database into files.
    """

    def __init__(
        self,
        storage: DBExportStorage,
        *,
        default_output_dir: str = "DB_EXPORTS",
    ):
        self.storage = storage
        self.default_output_dir = default_output_dir

    def _manifest_dir(self, output_dir: str) -> str:
        return manifest_dir(output_dir)

    def _manifest_path(self, output_dir: str, user_id: int) -> str:
        return manifest_path(output_dir, user_id)

    def _build_export_fingerprint(
        self,
        user_id: int,
        messages: List[MessageData],
        *,
        as_json: bool,
        include_date: bool,
        json_profile: str,
    ) -> Dict[str, Any]:
        return build_export_fingerprint(
            user_id,
            messages,
            as_json=as_json,
            include_date=include_date,
            json_profile=json_profile,
        )

    def _load_export_manifest(
        self, output_dir: str, user_id: int
    ) -> Optional[Dict[str, Any]]:
        return load_export_manifest(output_dir, user_id)

    def _persist_export_manifest(
        self,
        output_dir: str,
        user_id: int,
        payload: Dict[str, Any],
    ) -> None:
        persist_export_manifest(output_dir, user_id, payload)

    def _can_skip_export(
        self,
        output_dir: str,
        user_id: int,
        fingerprint: Dict[str, Any],
    ) -> Optional[str]:
        return can_skip_export(output_dir, user_id, fingerprint)

    def _resolve_export_author_name(
        self, user_id: int, messages: List[MessageData]
    ) -> str:
        plan = prepare_export_plan(
            self.storage,
            user_id=user_id,
            output_dir=".",
            source=_DBExportSource(
                export_summary=None,
                export_rows=None,
                export_row_iter_factory=None,
                messages=messages,
                source_count=len(messages),
            ),
            as_json=False,
            include_date=False,
            json_profile="ai",
        )
        return plan.target_author

    def _resolve_export_author_name_from_rows(
        self, user_id: int, rows: List[UserExportRow]
    ) -> str:
        plan = prepare_export_plan(
            self.storage,
            user_id=user_id,
            output_dir=".",
            source=_DBExportSource(
                export_summary=None,
                export_rows=rows,
                export_row_iter_factory=None,
                messages=None,
                source_count=len(rows),
            ),
            as_json=True,
            include_date=False,
            json_profile="ai",
        )
        return plan.target_author

    def format_message(
        self, m: MessageData, as_json: bool = False, json_profile: str = "ai"
    ) -> str:
        """Formats a MessageData object into a string for file output."""
        if as_json:
            return serialize_json_message(m, profile=json_profile)

        # Human-readable text format
        dt_str = m.timestamp.strftime("%Y-%m-%d][%H:%M:%S")
        reply_str = f" (в ответ на {m.reply_to_id})" if m.reply_to_id else ""
        fwd_str = f" [FWD from {m.fwd_from_id}]" if m.fwd_from_id else ""
        media_str = f" [{m.media_type}]" if m.media_type else ""

        # We use a placeholder for user_name if we have it in MessageData (I added it recently)
        author = m.author_name or f"User_{m.user_id}"
        header = f"[{dt_str}] <{author} ({m.user_id})>{reply_str}{fwd_str}{media_str}:"

        return f"{header}\n{m.text or '(пусто)'}"

    def _serialize_ai_row(self, row: UserExportRow) -> str:
        return serialize_row_as_ai_jsonl(row)

    def _write_batch_size(self, *, as_json: bool, json_profile: str) -> int:
        if not as_json:
            return 100
        if json_profile == "full":
            return 500
        return 1000

    def _load_export_source(
        self,
        *,
        user_id: int,
        as_json: bool,
        json_profile: str,
    ) -> Optional[_DBExportSource]:
        return load_export_source(
            self.storage,
            user_id=user_id,
            as_json=as_json,
            json_profile=json_profile,
        )

    def _prepare_export_plan(
        self,
        *,
        user_id: int,
        output_dir: str,
        source: _DBExportSource,
        as_json: bool,
        include_date: bool,
        json_profile: str,
    ):
        return prepare_export_plan(
            self.storage,
            user_id=user_id,
            output_dir=output_dir,
            source=source,
            as_json=as_json,
            include_date=include_date,
            json_profile=json_profile,
        )

    def _maybe_skip_unchanged_export(
        self,
        *,
        output_dir: str,
        user_id: int,
        fingerprint: Dict[str, Any],
        source_count: int,
    ) -> Optional[str]:
        unchanged_path = self._can_skip_export(output_dir, user_id, fingerprint)
        if not unchanged_path:
            return None

        telemetry.track_counter("db_export.skipped_unchanged", 1)
        logger.info(
            "DB export skipped as unchanged",
            extra={
                "event": "db_export_skipped",
                "metrics": {
                    "user_id": user_id,
                    "messages": source_count,
                    "path": unchanged_path,
                },
            },
        )
        return unchanged_path

    def _cleanup_existing_export_files(
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
                        f"Removed old export file to prevent duplication: {old_file}"
                    )
                except Exception as e:
                    logger.warning(f"Could not remove old export file {old_file}: {e}")

    def _format_txt_export_block(
        self,
        *,
        message: MessageData,
        msg_lookup: Dict[int, MessageData],
        last_date: Any,
        last_author_id: Optional[int],
    ) -> tuple[str, Any, Optional[int]]:
        current_date = message.timestamp.date()
        formatted_block = ""

        if current_date != last_date:
            date_header = current_date.strftime("%d %B %Y")
            formatted_block += f"\n\n{'=' * 20} {date_header} {'=' * 20}\n\n"
            last_date = current_date
            last_author_id = None

        reply_context = ""
        if message.reply_to_id and message.reply_to_id in msg_lookup:
            target = msg_lookup[message.reply_to_id]
            clean_text = (target.text or "").replace("\n", " ").strip()
            snippet = (clean_text[:40] + "...") if len(clean_text) > 40 else clean_text
            if snippet:
                reply_context = f'        re: "{snippet}"\n'

        author = message.author_name or f"User_{message.user_id}"
        time_str = message.timestamp.strftime("%H:%M:%S")

        if message.user_id == last_author_id and not reply_context:
            formatted_block += f"        {message.text or '(пусто)'}\n"
            return formatted_block, last_date, last_author_id

        if message.user_id == last_author_id:
            formatted_block += "\n"

        header = f"[{time_str}] <{author} ({message.user_id})>:"
        formatted_block += (
            f"{header}\n{reply_context}        {message.text or '(пусто)'}\n\n"
        )
        return formatted_block, last_date, message.user_id

    def _extract_export_cursor(
        self,
        *,
        source: _DBExportSource,
        fingerprint: Dict[str, Any],
    ) -> tuple[Optional[int], Optional[int]]:
        last_ts = fingerprint.get("last_timestamp")
        last_message_id = fingerprint.get("last_message_id")
        if last_ts is not None or last_message_id is not None:
            return (
                int(last_ts) if last_ts is not None else None,
                int(last_message_id) if last_message_id is not None else None,
            )

        if source.export_summary is not None:
            return (
                source.export_summary.last_timestamp,
                source.export_summary.last_message_id,
            )

        if source.export_rows:
            last_row = source.export_rows[-1]
            return last_row.timestamp, last_row.message_id

        if source.messages:
            last_message = sorted(
                source.messages, key=lambda message: (message.timestamp, message.message_id)
            )[-1]
            return int(last_message.timestamp.timestamp()), last_message.message_id

        return None, None

    def _upsert_export_target_state(
        self,
        *,
        user_id: int,
        output_path: str,
        target_author: str,
        source: _DBExportSource,
        fingerprint: Dict[str, Any],
    ) -> None:
        updater = getattr(self.storage, "upsert_export_target", None)
        if not callable(updater):
            return

        db_user = getattr(self.storage, "get_user", lambda _user_id: None)(user_id)
        username = None
        if db_user is not None:
            username = getattr(db_user, "username", None)
            if username is None and isinstance(db_user, dict):
                username = db_user.get("username")

        last_ts, last_message_id = self._extract_export_cursor(
            source=source,
            fingerprint=fingerprint,
        )
        updater(
            target_user_id=user_id,
            export_filename=os.path.basename(output_path) or None,
            export_dir=os.path.dirname(output_path) or None,
            last_exported_message_ts=last_ts,
            last_exported_message_id=last_message_id,
            last_known_author_name=target_author,
            last_known_username=username,
        )

    async def _write_export_payloads(
        self,
        *,
        source: _DBExportSource,
        output_path: str,
        as_json: bool,
        json_profile: str,
        expected_count: int,
    ) -> tuple[FileRotateWriter, int]:
        writer = FileRotateWriter(
            output_path,
            as_json=as_json,
            overwrite=True,
            persist_every_writes=25 if as_json else 5,
        )
        write_batch_size = self._write_batch_size(
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
                    block = self._serialize_ai_row(item)
                else:
                    block = self.format_message(
                        item, as_json=True, json_profile=json_profile
                    )
            else:
                block, last_date, last_author_id = format_txt_export_block(
                    message=item,
                    msg_lookup=msg_lookup,
                    last_date=last_date,
                    last_author_id=last_author_id,
                )

            pending_blocks.append(block + "\n" if as_json else block)
            pending_count += 1

            if pending_count >= write_batch_size:
                await flush_pending()

            count += 1
            if count % 100 == 0:
                logger.debug(f"Exported {count}/{expected_count} messages from DB...")

        await flush_pending()
        await writer.finalize()
        return writer, count

    async def export_user_messages(
        self,
        user_id: int,
        output_dir: Optional[str] = None,
        as_json: bool = False,
        include_date: bool = False,
        json_profile: str = "ai",
    ) -> str:
        """
        Fetches all messages for a user from storage and writes them to parts using FileRotateWriter.
        Returns the base output path.
        """
        started_at = perf_counter()
        resolved_output_dir = output_dir or self.default_output_dir

        source = self._load_export_source(
            user_id=user_id,
            as_json=as_json,
            json_profile=json_profile,
        )
        if source is None:
            logger.warning(f"No messages found in DB for user {user_id}")
            return ""

        if not os.path.exists(resolved_output_dir):
            os.makedirs(resolved_output_dir)

        plan = self._prepare_export_plan(
            user_id=user_id,
            output_dir=resolved_output_dir,
            source=source,
            as_json=as_json,
            include_date=include_date,
            json_profile=json_profile,
        )
        unchanged_path = self._maybe_skip_unchanged_export(
            output_dir=resolved_output_dir,
            user_id=user_id,
            fingerprint=plan.fingerprint,
            source_count=source.source_count,
        )
        if unchanged_path:
            self._upsert_export_target_state(
                user_id=user_id,
                output_path=unchanged_path,
                target_author=plan.target_author,
                source=source,
                fingerprint=plan.fingerprint,
            )
            return unchanged_path

        self._cleanup_existing_export_files(
            output_dir=resolved_output_dir,
            user_id=user_id,
            ext=plan.ext,
            output_path=plan.output_path,
        )
        writer, count = await self._write_export_payloads(
            source=source,
            output_path=plan.output_path,
            as_json=as_json,
            json_profile=json_profile,
            expected_count=source.source_count,
        )
        elapsed_seconds = perf_counter() - started_at
        telemetry.track_counter("db_export.users", 1)
        telemetry.track_counter("db_export.messages", count)
        telemetry.track_duration("db_export.total", elapsed_seconds)
        logger.info(
            "DB export complete",
            extra={
                "event": "db_export_complete",
                "metrics": {
                    "user_id": user_id,
                    "messages": count,
                    "json": as_json,
                    "path": plan.output_path,
                    "elapsed_seconds": round(elapsed_seconds, 3),
                    "writer_write_calls": writer.write_calls,
                    "writer_bytes_written": writer.bytes_written,
                    "writer_rotations": writer.rotation_count,
                    "writer_state_persists": writer.state_persist_count,
                },
            },
        )
        self._persist_export_manifest(
            resolved_output_dir,
            user_id,
            {
                "output_path": plan.output_path,
                "part_count": writer.current_part,
                "fingerprint": plan.fingerprint,
            },
        )
        self._upsert_export_target_state(
            user_id=user_id,
            output_path=plan.output_path,
            target_author=plan.target_author,
            source=source,
            fingerprint=plan.fingerprint,
        )
        logger.info(f"DB Export complete for {plan.target_author}: {count} messages.")
        return plan.output_path
