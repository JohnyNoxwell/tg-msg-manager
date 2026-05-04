import os
import glob
import logging
from time import perf_counter
from typing import Any, Callable, Dict, List, Optional

from .file_writer import FileRotateWriter
from .db_export import (
    DBExportSource as _DBExportSource,
    build_export_fingerprint,
    expected_export_paths,
    format_txt_export_block,
    load_incremental_export_source,
    load_export_manifest,
    load_export_source,
    manifest_dir,
    manifest_path,
    prepare_export_plan,
    serialize_json_message,
    serialize_row_as_ai_jsonl,
)
from ..infrastructure.storage.interface import DBExportStorage
from ..infrastructure.storage.records import (
    UserExportSummary,
    ExportTargetRecord,
    UserExportRow,
)
from ..core.models.message import MessageData
from ..core.telemetry import telemetry

logger = logging.getLogger(__name__)

EXPORT_RUN_STATUS_RUNNING = "running"
EXPORT_RUN_STATUS_SUCCESS = "success"
EXPORT_RUN_STATUS_FAILED = "failed"


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

    def _artifact_paths_exist(self, output_path: str, part_count: int) -> bool:
        return all(
            os.path.exists(path)
            for path in expected_export_paths(output_path, max(1, int(part_count)))
        )

    def _db_skip_match(
        self,
        *,
        output_dir: str,
        user_id: int,
        fingerprint: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        export_target = ExportTargetRecord.coerce(
            getattr(self.storage, "get_export_target", lambda _uid: None)(user_id)
        )
        if export_target is None:
            return None

        output_path = self._resolve_existing_export_path(
            export_target=export_target,
            fallback_output_dir=output_dir,
        )
        if not output_path:
            return None
        if (
            output_dir
            and export_target.export_dir
            and os.path.abspath(output_dir) != os.path.abspath(export_target.export_dir)
        ):
            return None

        if (
            export_target.artifact_message_count != fingerprint.get("message_count")
            or export_target.artifact_first_message_id
            != fingerprint.get("first_message_id")
            or export_target.artifact_last_message_id
            != fingerprint.get("last_message_id")
            or export_target.artifact_first_timestamp
            != fingerprint.get("first_timestamp")
            or export_target.artifact_last_timestamp
            != fingerprint.get("last_timestamp")
            or export_target.artifact_as_json != fingerprint.get("as_json")
            or export_target.artifact_include_date != fingerprint.get("include_date")
            or export_target.artifact_json_profile != fingerprint.get("json_profile")
        ):
            return None

        part_count = getattr(export_target, "export_part_count", None)
        if part_count is None:
            return None

        if not self._artifact_paths_exist(output_path, part_count):
            return None

        return {
            "output_path": output_path,
            "part_count": int(part_count),
        }

    def _legacy_manifest_skip_match(
        self,
        *,
        output_dir: str,
        user_id: int,
        fingerprint: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        manifest = self._load_export_manifest(output_dir, user_id)
        if not manifest or manifest.get("fingerprint") != fingerprint:
            return None

        output_path = manifest.get("output_path")
        if not output_path or not isinstance(output_path, str):
            return None

        try:
            part_count = max(1, int(manifest.get("part_count", 1)))
        except Exception:
            return None

        if not self._artifact_paths_exist(output_path, part_count):
            return None

        return {
            "output_path": output_path,
            "part_count": part_count,
        }

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

    def _load_incremental_export_source(
        self,
        *,
        user_id: int,
        last_exported_message_ts: int,
        last_exported_message_id: int,
        as_json: bool,
        json_profile: str,
    ) -> Optional[_DBExportSource]:
        return load_incremental_export_source(
            self.storage,
            user_id=user_id,
            last_exported_message_ts=last_exported_message_ts,
            last_exported_message_id=last_exported_message_id,
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
    ) -> Optional[Dict[str, Any]]:
        unchanged = self._db_skip_match(
            output_dir=output_dir,
            user_id=user_id,
            fingerprint=fingerprint,
        ) or self._legacy_manifest_skip_match(
            output_dir=output_dir,
            user_id=user_id,
            fingerprint=fingerprint,
        )
        if not unchanged:
            return None

        telemetry.track_counter("db_export.skipped_unchanged", 1)
        logger.info(
            "DB export skipped as unchanged",
            extra={
                "event": "db_export_skipped",
                "metrics": {
                    "user_id": user_id,
                    "messages": source_count,
                    "path": unchanged["output_path"],
                },
            },
        )
        return unchanged

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
        part_count: Optional[int] = None,
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
            export_part_count=part_count,
            artifact_message_count=(
                int(fingerprint["message_count"])
                if fingerprint.get("message_count") is not None
                else None
            ),
            artifact_first_message_id=(
                int(fingerprint["first_message_id"])
                if fingerprint.get("first_message_id") is not None
                else None
            ),
            artifact_last_message_id=(
                int(fingerprint["last_message_id"])
                if fingerprint.get("last_message_id") is not None
                else None
            ),
            artifact_first_timestamp=(
                int(fingerprint["first_timestamp"])
                if fingerprint.get("first_timestamp") is not None
                else None
            ),
            artifact_last_timestamp=(
                int(fingerprint["last_timestamp"])
                if fingerprint.get("last_timestamp") is not None
                else None
            ),
            artifact_as_json=(
                bool(fingerprint["as_json"])
                if fingerprint.get("as_json") is not None
                else None
            ),
            artifact_include_date=(
                bool(fingerprint["include_date"])
                if fingerprint.get("include_date") is not None
                else None
            ),
            artifact_json_profile=(
                str(fingerprint["json_profile"])
                if fingerprint.get("json_profile") is not None
                else None
            ),
            last_known_author_name=target_author,
            last_known_username=username,
        )

    def _start_export_run(self, *, user_id: int) -> Optional[int]:
        starter = getattr(self.storage, "start_export_run", None)
        if not callable(starter):
            return None
        run_id = starter(target_user_id=user_id)
        return int(run_id) if run_id is not None else None

    def _resolve_existing_export_path(
        self,
        *,
        export_target: Any,
        fallback_output_dir: str,
    ) -> Optional[str]:
        export_filename = getattr(export_target, "export_filename", None)
        export_dir = getattr(export_target, "export_dir", None) or fallback_output_dir
        if not export_filename:
            return None
        return os.path.join(export_dir, export_filename)

    def _supports_incremental_update(
        self,
        *,
        export_target: Any,
        output_dir: Optional[str],
        as_json: bool,
        include_date: bool,
        json_profile: str,
    ) -> bool:
        if not as_json or include_date or json_profile != "ai":
            return False
        if export_target is None:
            return False

        export_filename = getattr(export_target, "export_filename", None)
        export_dir = getattr(export_target, "export_dir", None)
        last_ts = getattr(export_target, "last_exported_message_ts", None)
        last_message_id = getattr(export_target, "last_exported_message_id", None)
        if not export_filename or last_ts is None or last_message_id is None:
            return False
        if output_dir and export_dir and os.path.abspath(output_dir) != os.path.abspath(
            export_dir
        ):
            return False
        return export_filename.endswith(".jsonl")

    def _refresh_export_target_artifact_from_db_state(
        self,
        *,
        user_id: int,
        output_path: str,
        as_json: bool,
        include_date: bool,
        json_profile: str,
        part_count: int,
    ) -> None:
        full_summary_getter = getattr(self.storage, "get_user_export_summary", None)
        if not callable(full_summary_getter):
            return
        full_summary = UserExportSummary.coerce(full_summary_getter(user_id))
        if full_summary is None:
            return
        source = _DBExportSource(
            export_summary=full_summary,
            export_rows=None,
            export_row_iter_factory=None,
            messages=None,
            source_count=full_summary.message_count,
        )
        plan = self._prepare_export_plan(
            user_id=user_id,
            output_dir=os.path.dirname(output_path) or self.default_output_dir,
            source=source,
            as_json=as_json,
            include_date=include_date,
            json_profile=json_profile,
        )
        self._upsert_export_target_state(
            user_id=user_id,
            output_path=output_path,
            target_author=plan.target_author,
            source=source,
            fingerprint=plan.fingerprint,
            part_count=part_count,
        )

    def _finish_export_run(
        self,
        run_id: Optional[int],
        *,
        status: str,
        new_messages_count: int = 0,
        last_new_message_ts: Optional[int] = None,
        error: Optional[str] = None,
    ) -> None:
        if run_id is None:
            return
        finisher = getattr(self.storage, "finish_export_run", None)
        if not callable(finisher):
            return
        finisher(
            run_id,
            status=status,
            new_messages_count=new_messages_count,
            last_new_message_ts=last_new_message_ts,
            error=error,
        )

    async def _write_export_payloads(
        self,
        *,
        source: _DBExportSource,
        output_path: str,
        as_json: bool,
        json_profile: str,
        expected_count: int,
        overwrite: bool = True,
        on_progress: Optional[Callable[[int, Any], None]] = None,
    ) -> tuple[FileRotateWriter, int]:
        writer = FileRotateWriter(
            output_path,
            as_json=as_json,
            overwrite=overwrite,
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
            count += 1
            if on_progress is not None:
                on_progress(count, item)

            if pending_count >= write_batch_size:
                await flush_pending()

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
        processed_count = 0
        processed_last_ts: Optional[int] = None
        run_id = self._start_export_run(user_id=user_id)

        def track_progress(count: int, item: Any) -> None:
            nonlocal processed_count, processed_last_ts
            processed_count = count
            timestamp = getattr(item, "timestamp", None)
            if timestamp is None and isinstance(item, dict):
                timestamp = item.get("timestamp")
            if hasattr(timestamp, "timestamp"):
                processed_last_ts = int(timestamp.timestamp())
            elif timestamp is not None:
                processed_last_ts = int(timestamp)

        try:
            source = self._load_export_source(
                user_id=user_id,
                as_json=as_json,
                json_profile=json_profile,
            )
            if source is None:
                logger.warning(f"No messages found in DB for user {user_id}")
                self._finish_export_run(
                    run_id,
                    status=EXPORT_RUN_STATUS_SUCCESS,
                    new_messages_count=0,
                )
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
            unchanged = self._maybe_skip_unchanged_export(
                output_dir=resolved_output_dir,
                user_id=user_id,
                fingerprint=plan.fingerprint,
                source_count=source.source_count,
            )
            if unchanged:
                self._upsert_export_target_state(
                    user_id=user_id,
                    output_path=unchanged["output_path"],
                    target_author=plan.target_author,
                    source=source,
                    fingerprint=plan.fingerprint,
                    part_count=unchanged["part_count"],
                )
                self._finish_export_run(
                    run_id,
                    status=EXPORT_RUN_STATUS_SUCCESS,
                    new_messages_count=0,
                )
                return unchanged["output_path"]

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
                overwrite=True,
                on_progress=track_progress,
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
            self._upsert_export_target_state(
                user_id=user_id,
                output_path=plan.output_path,
                target_author=plan.target_author,
                source=source,
                fingerprint=plan.fingerprint,
                part_count=writer.current_part,
            )
            last_ts, _last_message_id = self._extract_export_cursor(
                source=source,
                fingerprint=plan.fingerprint,
            )
            self._finish_export_run(
                run_id,
                status=EXPORT_RUN_STATUS_SUCCESS,
                new_messages_count=count,
                last_new_message_ts=last_ts,
            )
            logger.info(f"DB Export complete for {plan.target_author}: {count} messages.")
            return plan.output_path
        except Exception as exc:
            self._finish_export_run(
                run_id,
                status=EXPORT_RUN_STATUS_FAILED,
                new_messages_count=processed_count,
                last_new_message_ts=processed_last_ts,
                error=str(exc),
            )
            raise

    async def update_user_messages(
        self,
        user_id: int,
        output_dir: Optional[str] = None,
        as_json: bool = True,
        include_date: bool = False,
        json_profile: str = "ai",
    ) -> str:
        resolved_output_dir = output_dir or self.default_output_dir
        export_target = ExportTargetRecord.coerce(
            getattr(self.storage, "get_export_target", lambda _uid: None)(user_id)
        )
        if not self._supports_incremental_update(
            export_target=export_target,
            output_dir=output_dir,
            as_json=as_json,
            include_date=include_date,
            json_profile=json_profile,
        ):
            return await self.export_user_messages(
                user_id,
                output_dir=output_dir,
                as_json=as_json,
                include_date=include_date,
                json_profile=json_profile,
            )

        output_path = self._resolve_existing_export_path(
            export_target=export_target,
            fallback_output_dir=resolved_output_dir,
        )
        if not output_path or not os.path.exists(output_path):
            return await self.export_user_messages(
                user_id,
                output_dir=output_dir,
                as_json=as_json,
                include_date=include_date,
                json_profile=json_profile,
            )

        last_ts = int(getattr(export_target, "last_exported_message_ts"))
        last_message_id = int(getattr(export_target, "last_exported_message_id"))
        run_id = self._start_export_run(user_id=user_id)
        processed_count = 0
        processed_last_ts: Optional[int] = None
        processed_last_message_id: Optional[int] = None

        def track_progress(count: int, item: Any) -> None:
            nonlocal processed_count, processed_last_ts, processed_last_message_id
            processed_count = count
            timestamp = getattr(item, "timestamp", None)
            message_id = getattr(item, "message_id", None)
            if timestamp is None and isinstance(item, dict):
                timestamp = item.get("timestamp")
            if message_id is None and isinstance(item, dict):
                message_id = item.get("message_id")
            processed_last_ts = int(timestamp) if timestamp is not None else None
            processed_last_message_id = (
                int(message_id) if message_id is not None else None
            )

        try:
            source = self._load_incremental_export_source(
                user_id=user_id,
                last_exported_message_ts=last_ts,
                last_exported_message_id=last_message_id,
                as_json=as_json,
                json_profile=json_profile,
            )
            if source is None:
                self._finish_export_run(
                    run_id,
                    status=EXPORT_RUN_STATUS_SUCCESS,
                    new_messages_count=0,
                )
                return output_path

            target_author = (
                self._prepare_export_plan(
                    user_id=user_id,
                    output_dir=resolved_output_dir,
                    source=source,
                    as_json=as_json,
                    include_date=include_date,
                    json_profile=json_profile,
                ).target_author
            )
            writer, count = await self._write_export_payloads(
                source=source,
                output_path=output_path,
                as_json=as_json,
                json_profile=json_profile,
                expected_count=source.source_count,
                overwrite=False,
                on_progress=track_progress,
            )
            self._refresh_export_target_artifact_from_db_state(
                user_id=user_id,
                output_path=output_path,
                as_json=as_json,
                include_date=include_date,
                json_profile=json_profile,
                part_count=writer.current_part,
            )
            self._finish_export_run(
                run_id,
                status=EXPORT_RUN_STATUS_SUCCESS,
                new_messages_count=count,
                last_new_message_ts=processed_last_ts,
            )
            return output_path
        except Exception as exc:
            self._finish_export_run(
                run_id,
                status=EXPORT_RUN_STATUS_FAILED,
                new_messages_count=processed_count,
                last_new_message_ts=processed_last_ts,
                error=str(exc),
            )
            raise
