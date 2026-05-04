from typing import Any, Dict, Optional

from ...core.models.message import MessageData


def format_txt_export_block(
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
