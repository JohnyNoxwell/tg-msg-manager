import os
import re
import glob
import json
import logging
from time import perf_counter
from datetime import datetime
from typing import Any, Dict, List, Optional
from .file_writer import FileRotateWriter
from ..infrastructure.storage.interface import BaseStorage
from ..core.models.message import MessageData
from ..core.telemetry import telemetry
from ..utils.ui import UI

logger = logging.getLogger(__name__)

class DBExportService:
    """
    Service responsible for exporting cached messages from the database into files.
    """
    def __init__(self, storage: BaseStorage):
        self.storage = storage

    def _manifest_dir(self, output_dir: str) -> str:
        return os.path.join(output_dir, ".export_state")

    def _manifest_path(self, output_dir: str, user_id: int) -> str:
        return os.path.join(self._manifest_dir(output_dir), f"{user_id}.json")

    def _build_export_fingerprint(
        self,
        user_id: int,
        messages: List[MessageData],
        *,
        as_json: bool,
        include_date: bool,
        json_profile: str,
    ) -> Dict[str, Any]:
        first = messages[0]
        last = messages[-1]
        return {
            "user_id": user_id,
            "message_count": len(messages),
            "first_message_id": first.message_id,
            "last_message_id": last.message_id,
            "first_timestamp": int(first.timestamp.timestamp()),
            "last_timestamp": int(last.timestamp.timestamp()),
            "as_json": as_json,
            "include_date": include_date,
            "json_profile": json_profile,
        }

    def _load_export_manifest(self, output_dir: str, user_id: int) -> Optional[Dict[str, Any]]:
        path = self._manifest_path(output_dir, user_id)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            return loaded if isinstance(loaded, dict) else None
        except Exception:
            return None

    def _persist_export_manifest(
        self,
        output_dir: str,
        user_id: int,
        payload: Dict[str, Any],
    ) -> None:
        os.makedirs(self._manifest_dir(output_dir), exist_ok=True)
        with open(self._manifest_path(output_dir, user_id), "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))

    def _expected_export_paths(self, output_path: str, part_count: int) -> List[str]:
        if part_count <= 1:
            return [output_path]
        root, ext = os.path.splitext(output_path)
        paths = [output_path]
        for part in range(2, part_count + 1):
            paths.append(f"{root}_part{part}{ext}")
        return paths

    def _can_skip_export(
        self,
        output_dir: str,
        user_id: int,
        fingerprint: Dict[str, Any],
    ) -> Optional[str]:
        manifest = self._load_export_manifest(output_dir, user_id)
        if not manifest:
            return None
        if manifest.get("fingerprint") != fingerprint:
            return None

        output_path = manifest.get("output_path")
        if not output_path or not isinstance(output_path, str):
            return None

        part_count = manifest.get("part_count", 1)
        try:
            part_count = max(1, int(part_count))
        except Exception:
            return None

        expected_paths = self._expected_export_paths(output_path, part_count)
        if all(os.path.exists(path) for path in expected_paths):
            return output_path
        return None

    def _resolve_export_author_name(self, user_id: int, messages: List[MessageData]) -> str:
        db_user = self.storage.get_user(user_id)
        if db_user:
            formatted = UI.format_name(db_user)
            if formatted and formatted != "Unknown" and not formatted.startswith("ID:"):
                return formatted

        for m in messages:
            if m.user_id == user_id and m.author_name and m.author_name.strip():
                return m.author_name.strip()

        return f"User_{user_id}"

    def _resolve_export_author_name_from_rows(self, user_id: int, rows: List[Dict[str, Any]]) -> str:
        db_user = self.storage.get_user(user_id)
        if db_user:
            formatted = UI.format_name(db_user)
            if formatted and formatted != "Unknown" and not formatted.startswith("ID:"):
                return formatted

        for row in rows:
            if row.get("user_id") == user_id and row.get("author_name"):
                return str(row["author_name"]).strip()

        return f"User_{user_id}"

    def format_message(self, m: MessageData, as_json: bool = False, json_profile: str = "ai") -> str:
        """Formats a MessageData object into a string for file output."""
        if as_json:
            payload = self._serialize_json_message(m, profile=json_profile)
            return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        
        # Human-readable text format
        dt_str = m.timestamp.strftime("%Y-%m-%d][%H:%M:%S")
        reply_str = f" (в ответ на {m.reply_to_id})" if m.reply_to_id else ""
        fwd_str = f" [FWD from {m.fwd_from_id}]" if m.fwd_from_id else ""
        media_str = f" [{m.media_type}]" if m.media_type else ""
        
        # We use a placeholder for user_name if we have it in MessageData (I added it recently)
        author = m.author_name or f"User_{m.user_id}"
        header = f"[{dt_str}] <{author} ({m.user_id})>{reply_str}{fwd_str}{media_str}:"
        
        return f"{header}\n{m.text or '(пусто)'}"

    def _serialize_json_message(self, m: MessageData, profile: str = "ai") -> Dict[str, Any]:
        if profile == "full":
            return m.to_dict()
        if profile != "ai":
            raise ValueError(f"Unsupported JSON profile: {profile}")
        return self._serialize_ai_message(m)

    def _serialize_ai_message(self, m: MessageData) -> Dict[str, Any]:
        raw = m.raw_payload if isinstance(m.raw_payload, dict) else {}
        return self._serialize_ai_payload(
            message_id=m.message_id,
            chat_id=m.chat_id,
            user_id=m.user_id,
            author_name=m.author_name,
            timestamp=int(m.timestamp.timestamp()),
            text=m.text,
            reply_to_id=m.reply_to_id,
            media_type=m.media_type,
            fwd_from_id=m.fwd_from_id,
            context_group_id=m.context_group_id,
            is_service=m.is_service,
            raw=raw,
        )

    def _serialize_ai_row(self, row: Dict[str, Any]) -> str:
        raw_payload = row.get("raw_payload")
        if isinstance(raw_payload, str):
            try:
                raw = json.loads(raw_payload)
            except Exception:
                raw = {}
        elif isinstance(raw_payload, dict):
            raw = raw_payload
        else:
            raw = {}

        payload = self._serialize_ai_payload(
            message_id=row["message_id"],
            chat_id=row["chat_id"],
            user_id=row["user_id"],
            author_name=row.get("author_name"),
            timestamp=row["timestamp"],
            text=row.get("text"),
            reply_to_id=row.get("reply_to_id"),
            media_type=row.get("media_type"),
            fwd_from_id=row.get("fwd_from_id"),
            context_group_id=row.get("context_group_id"),
            is_service=bool(row.get("is_service")),
            raw=raw,
        )
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    def _serialize_ai_payload(
        self,
        *,
        message_id: int,
        chat_id: int,
        user_id: int,
        author_name: Optional[str],
        timestamp: int,
        text: Optional[str],
        reply_to_id: Optional[int],
        media_type: Optional[str],
        fwd_from_id: Optional[int],
        context_group_id: Optional[str],
        is_service: bool,
        raw: Dict[str, Any],
    ) -> Dict[str, Any]:
        reply_to = raw.get("reply_to") if isinstance(raw.get("reply_to"), dict) else {}
        reply_to_id = reply_to_id or reply_to.get("reply_to_msg_id")
        reply_to_top_id = reply_to.get("reply_to_top_id")
        forum_topic = True if reply_to.get("forum_topic") else None

        payload = {
            "edit_date": raw.get("edit_date"),
            "message_id": message_id,
            "chat_id": chat_id,
            "user_id": user_id,
            "author_name": author_name,
            "timestamp": timestamp,
            "text": text,
            "reply_to_id": reply_to_id,
            "reply_to_top_id": reply_to_top_id,
            "forum_topic": forum_topic,
            "media_type": media_type,
            "fwd_from_id": fwd_from_id,
            "context_group_id": context_group_id,
            "is_service": True if is_service else None,
            "reactions": self._extract_reaction_summary(raw),
        }
        return {k: v for k, v in payload.items() if v not in (None, "", [])}

    def _extract_reaction_summary(self, raw: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        reactions = raw.get("reactions")
        if not isinstance(reactions, dict):
            return None

        summary: List[Dict[str, Any]] = []
        for item in reactions.get("results") or []:
            if not isinstance(item, dict):
                continue
            reaction = item.get("reaction")
            count = item.get("count")
            emoji = self._reaction_label(reaction)
            if emoji is None or count is None:
                continue
            summary.append({"emoji": emoji, "count": count})

        return summary or None

    def _reaction_label(self, reaction: Any) -> Optional[str]:
        if not isinstance(reaction, dict):
            return None
        emoticon = reaction.get("emoticon")
        if emoticon:
            return emoticon
        if reaction.get("_") == "ReactionCustomEmoji":
            document_id = reaction.get("document_id")
            return f"custom:{document_id}" if document_id is not None else "custom"
        return reaction.get("_")

    def _write_batch_size(self, *, as_json: bool, json_profile: str) -> int:
        if not as_json:
            return 100
        if json_profile == "full":
            return 500
        return 1000

    async def export_user_messages(
        self,
        user_id: int,
        output_dir: str = "DB_EXPORTS",
        as_json: bool = False,
        include_date: bool = False,
        json_profile: str = "ai",
    ) -> str:
        """
        Fetches all messages for a user from storage and writes them to parts using FileRotateWriter.
        Returns the base output path.
        """
        started_at = perf_counter()
        export_rows = None
        if as_json and json_profile == "ai":
            getter = getattr(self.storage, "get_user_export_rows", None)
            if callable(getter):
                export_rows = getter(user_id)

        messages = None if export_rows is not None else self.storage.get_user_messages(user_id)
        source_items = export_rows if export_rows is not None else messages
        if not source_items:
            logger.warning(f"No messages found in DB for user {user_id}")
            return ""

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Find the correct author name for the filename
        if export_rows is not None:
            target_author = self._resolve_export_author_name_from_rows(user_id, export_rows)
        else:
            target_author = self._resolve_export_author_name(user_id, messages)
            
        safe_name = re.sub(r'[^\w\s-]', '', target_author).strip()
        safe_name = re.sub(r'[-\s]+', '_', safe_name)
        
        date_suffix = f"_date({datetime.now().strftime('%m-%d')})" if include_date else ""
        ext = ".jsonl" if as_json else ".txt"
        filename = f"{safe_name}_{user_id}{date_suffix}{ext}"
        output_path = os.path.join(output_dir, filename)

        # Sort messages by date to ensure chronological chat flow
        if export_rows is not None:
            fingerprint = {
                "user_id": user_id,
                "message_count": len(export_rows),
                "first_message_id": export_rows[0]["message_id"],
                "last_message_id": export_rows[-1]["message_id"],
                "first_timestamp": export_rows[0]["timestamp"],
                "last_timestamp": export_rows[-1]["timestamp"],
                "as_json": as_json,
                "include_date": include_date,
                "json_profile": json_profile,
            }
        else:
            messages.sort(key=lambda x: (x.timestamp, x.message_id))
            fingerprint = self._build_export_fingerprint(
                user_id,
                messages,
                as_json=as_json,
                include_date=include_date,
                json_profile=json_profile,
            )
        unchanged_path = self._can_skip_export(output_dir, user_id, fingerprint)
        if unchanged_path:
            telemetry.track_counter("db_export.skipped_unchanged", 1)
            source_count = len(source_items)
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

        # 1. Cleanup existing files for this user_id to avoid duplication if name changed or was missing
        # We look for *_{user_id}.ext and *_{user_id}_part*.ext
        cleanup_patterns = [
            os.path.join(output_dir, f"*_{user_id}{ext}"),
            os.path.join(output_dir, f"*_{user_id}_part*{ext}")
        ]
        for pattern in cleanup_patterns:
            for old_file in glob.glob(pattern):
                # Don't delete the file we are about to create if it happens to match (though overwrite=True handles it)
                if os.path.abspath(old_file) == os.path.abspath(output_path):
                    continue
                try:
                    os.remove(old_file)
                    logger.debug(f"Removed old export file to prevent duplication: {old_file}")
                except Exception as e:
                    logger.warning(f"Could not remove old export file {old_file}: {e}")

        # Message lookup for resolving replies (only for TXT format)
        msg_lookup = {m.message_id: m for m in messages} if (messages is not None and not as_json) else {}

        writer = FileRotateWriter(
            output_path,
            as_json=as_json,
            overwrite=True,
            persist_every_writes=25 if as_json else 5,
        )
        write_batch_size = self._write_batch_size(as_json=as_json, json_profile=json_profile)
        
        last_date = None
        last_author_id = None
        
        pending_blocks: List[str] = []
        pending_count = 0

        async def flush_pending():
            nonlocal pending_blocks, pending_count
            if not pending_blocks:
                return
            await writer.write_block("".join(pending_blocks), pending_count)
            pending_blocks = []
            pending_count = 0

        count = 0
        iterable = export_rows if export_rows is not None else messages
        for item in iterable:
            if as_json:
                if export_rows is not None:
                    block = self._serialize_ai_row(item)
                else:
                    block = self.format_message(item, as_json=True, json_profile=json_profile)
                pending_blocks.append(block + "\n")
                pending_count += 1
            else:
                # Chat-like TXT formatting
                m = item
                current_date = m.timestamp.date()
                formatted_block = ""
                
                # 1. Date Header
                if current_date != last_date:
                    date_header = current_date.strftime("%d %B %Y")
                    formatted_block += f"\n\n{'=' * 20} {date_header} {'=' * 20}\n\n"
                    last_date = current_date
                    last_author_id = None # Reset author grouping on new day
                
                # 2. Reply Context
                reply_context = ""
                if m.reply_to_id and m.reply_to_id in msg_lookup:
                    target = msg_lookup[m.reply_to_id]
                    clean_text = (target.text or "").replace("\n", " ").strip()
                    snippet = (clean_text[:40] + "...") if len(clean_text) > 40 else clean_text
                    if snippet:
                        reply_context = f"        re: \"{snippet}\"\n"
                
                # 3. Message Body (Grouping)
                author = m.author_name or f"User_{m.user_id}"
                time_str = m.timestamp.strftime("%H:%M:%S")
                
                if m.user_id == last_author_id and not reply_context:
                    # Same author and NO reply context - condensed grouping
                    formatted_block += f"        {m.text or '(пусто)'}\n"
                else:
                    # New author OR same author but with a reply context (needs full block or separator)
                    if m.user_id == last_author_id:
                        # Add a small gap to separate the grouped message with context
                        formatted_block += "\n"
                    
                    header = f"[{time_str}] <{author} ({m.user_id})>:"
                    formatted_block += f"{header}\n{reply_context}        {m.text or '(пусто)'}\n\n"
                    last_author_id = m.user_id
                
                pending_blocks.append(formatted_block)
                pending_count += 1

            if pending_count >= write_batch_size:
                await flush_pending()

            count += 1
            if count % 100 == 0:
                logger.debug(f"Exported {count}/{len(iterable)} messages from DB...")

        await flush_pending()
        await writer.finalize()
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
                    "path": output_path,
                    "elapsed_seconds": round(elapsed_seconds, 3),
                    "writer_write_calls": writer.write_calls,
                    "writer_bytes_written": writer.bytes_written,
                    "writer_rotations": writer.rotation_count,
                    "writer_state_persists": writer.state_persist_count,
                },
            },
        )
        self._persist_export_manifest(
            output_dir,
            user_id,
            {
                "output_path": output_path,
                "part_count": writer.current_part,
                "fingerprint": fingerprint,
            },
        )
        logger.info(f"DB Export complete for {target_author}: {count} messages.")
        return output_path
