import os
import re
import glob
import logging
from datetime import datetime
from typing import List, Optional
from .file_writer import FileRotateWriter
from ..infrastructure.storage.interface import BaseStorage
from ..core.models.message import MessageData
from ..utils.ui import UI

logger = logging.getLogger(__name__)

class DBExportService:
    """
    Service responsible for exporting cached messages from the database into files.
    """
    def __init__(self, storage: BaseStorage):
        self.storage = storage

    def format_message(self, m: MessageData, as_json: bool = False) -> str:
        """Formats a MessageData object into a string for file output."""
        if as_json:
            import json
            return json.dumps(m.to_dict(), ensure_ascii=False)
        
        # Human-readable text format
        dt_str = m.timestamp.strftime("%Y-%m-%d][%H:%M:%S")
        reply_str = f" (в ответ на {m.reply_to_id})" if m.reply_to_id else ""
        fwd_str = f" [FWD from {m.fwd_from_id}]" if m.fwd_from_id else ""
        media_str = f" [{m.media_type}]" if m.media_type else ""
        
        # We use a placeholder for user_name if we have it in MessageData (I added it recently)
        author = m.author_name or f"User_{m.user_id}"
        header = f"[{dt_str}] <{author} ({m.user_id})>{reply_str}{fwd_str}{media_str}:"
        
        return f"{header}\n{m.text or '(пусто)'}"

    async def export_user_messages(self, user_id: int, output_dir: str = "DB_EXPORTS", as_json: bool = False, include_date: bool = False) -> str:
        """
        Fetches all messages for a user from storage and writes them to parts using FileRotateWriter.
        Returns the base output path.
        """
        messages = self.storage.get_user_messages(user_id)
        if not messages:
            logger.warning(f"No messages found in DB for user {user_id}")
            return ""

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Find the correct author name for the filename
        target_author = "Unknown"
        db_user = self.storage.get_user(user_id)
        if db_user:
            target_author = UI.format_name(db_user)
        
        if target_author == "Unknown" and messages:
            for m in messages:
                if m.user_id == user_id and m.author_name:
                    target_author = m.author_name
                    break
        
        if target_author == "Unknown":
            target_author = f"User_{user_id}"

        if target_author.startswith("ID:"):
            target_author = target_author[3:] # Remove "ID:" prefix for cleaner filenames
            
        safe_name = re.sub(r'[^\w\s-]', '', target_author).strip()
        safe_name = re.sub(r'[-\s]+', '_', safe_name)
        
        date_suffix = f"_date({datetime.now().strftime('%m-%d')})" if include_date else ""
        ext = ".jsonl" if as_json else ".txt"
        filename = f"{safe_name}_{user_id}{date_suffix}{ext}"
        output_path = os.path.join(output_dir, filename)

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

        # Sort messages by date to ensure chronological chat flow
        messages.sort(key=lambda x: x.timestamp)
        
        # Message lookup for resolving replies (only for TXT format)
        msg_lookup = {m.message_id: m for m in messages} if not as_json else {}

        writer = FileRotateWriter(output_path, as_json=as_json, overwrite=True)
        
        last_date = None
        last_author_id = None
        
        count = 0
        for m in messages:
            if as_json:
                block = self.format_message(m, as_json=True)
                await writer.write_block(block + "\n", 1)
            else:
                # Chat-like TXT formatting
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
                
                await writer.write_block(formatted_block, 1)

            count += 1
            if count % 100 == 0:
                logger.debug(f"Exported {count}/{len(messages)} messages from DB...")

        logger.info(f"DB Export complete for {target_author}: {count} messages.")
        return output_path
