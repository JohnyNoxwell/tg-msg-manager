import json
from typing import Any, Dict, List, Optional

from ...core.models.message import MessageData
from ...infrastructure.storage.records import UserExportRow


def serialize_json_message(
    message: MessageData,
    *,
    profile: str = "ai",
) -> str:
    if profile == "full":
        return json.dumps(message.to_dict(), ensure_ascii=False, separators=(",", ":"))
    if profile != "ai":
        raise ValueError(f"Unsupported JSON profile: {profile}")
    payload = serialize_ai_payload(
        message_id=message.message_id,
        chat_id=message.chat_id,
        user_id=message.user_id,
        author_name=message.author_name,
        timestamp=int(message.timestamp.timestamp()),
        text=message.text,
        reply_to_id=message.reply_to_id,
        media_type=message.media_type,
        fwd_from_id=message.fwd_from_id,
        context_group_id=message.context_group_id,
        is_service=message.is_service,
        raw=message.raw_payload if isinstance(message.raw_payload, dict) else {},
    )
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def serialize_row_as_ai_jsonl(row: UserExportRow) -> str:
    raw_payload = row.raw_payload
    if isinstance(raw_payload, str):
        try:
            raw = json.loads(raw_payload)
        except Exception:
            raw = {}
    elif isinstance(raw_payload, dict):
        raw = raw_payload
    else:
        raw = {}

    payload = serialize_ai_payload(
        message_id=row.message_id,
        chat_id=row.chat_id,
        user_id=row.user_id,
        author_name=row.author_name,
        timestamp=row.timestamp,
        text=row.text,
        reply_to_id=row.reply_to_id,
        media_type=row.media_type,
        fwd_from_id=row.fwd_from_id,
        context_group_id=row.context_group_id,
        is_service=row.is_service,
        raw=raw,
    )
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def serialize_ai_payload(
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
        "reactions": extract_reaction_summary(raw),
    }
    return {k: v for k, v in payload.items() if v not in (None, "", [])}


def extract_reaction_summary(raw: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    reactions = raw.get("reactions")
    if not isinstance(reactions, dict):
        return None

    summary: List[Dict[str, Any]] = []
    for item in reactions.get("results") or []:
        if not isinstance(item, dict):
            continue
        reaction = item.get("reaction")
        count = item.get("count")
        emoji = reaction_label(reaction)
        if emoji is None or count is None:
            continue
        summary.append({"emoji": emoji, "count": count})

    return summary or None


def reaction_label(reaction: Any) -> Optional[str]:
    if not isinstance(reaction, dict):
        return None
    emoticon = reaction.get("emoticon")
    if emoticon:
        return emoticon
    if reaction.get("_") == "ReactionCustomEmoji":
        document_id = reaction.get("document_id")
        return f"custom:{document_id}" if document_id is not None else "custom"
    return reaction.get("_")
