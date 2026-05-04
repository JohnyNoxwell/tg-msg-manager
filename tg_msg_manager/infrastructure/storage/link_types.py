from typing import Optional

CONTEXT_LINK_TARGET_MESSAGE = "target_message"
CONTEXT_LINK_REPLY_PARENT = "reply_parent"
CONTEXT_LINK_REPLY_CHILD = "reply_child"
CONTEXT_LINK_WINDOW_BEFORE = "window_before"
CONTEXT_LINK_WINDOW_AFTER = "window_after"
CONTEXT_LINK_SAME_THREAD = "same_thread"
CONTEXT_LINK_MENTION = "mention"
CONTEXT_LINK_LEGACY = "legacy"
CONTEXT_LINK_UNKNOWN = "unknown"

VALID_CONTEXT_LINK_TYPES = frozenset(
    {
        CONTEXT_LINK_TARGET_MESSAGE,
        CONTEXT_LINK_REPLY_PARENT,
        CONTEXT_LINK_REPLY_CHILD,
        CONTEXT_LINK_WINDOW_BEFORE,
        CONTEXT_LINK_WINDOW_AFTER,
        CONTEXT_LINK_SAME_THREAD,
        CONTEXT_LINK_MENTION,
        CONTEXT_LINK_LEGACY,
        CONTEXT_LINK_UNKNOWN,
    }
)

CONTEXT_ALGO_LEGACY = "legacy"
CONTEXT_ALGO_REPLY_CONTEXT_V1 = "reply_context_v1"

TARGET_LINK_LEGACY = "legacy"
TARGET_LINK_TARGET_AUTHOR = "target_author"
TARGET_LINK_REPLY_CONTEXT = "reply_context"


def validate_context_link_type(value: str) -> bool:
    return value in VALID_CONTEXT_LINK_TYPES


def normalize_context_link_type(
    value: Optional[str],
    *,
    default: str = CONTEXT_LINK_UNKNOWN,
) -> str:
    normalized = (value or "").strip().lower()
    if validate_context_link_type(normalized):
        return normalized
    return default
