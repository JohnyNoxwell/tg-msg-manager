DISCUSSION_MODE_NONE = "none"
DISCUSSION_MODE_FULL = "full"
ALLOWED_DISCUSSION_MODES = frozenset(
    {
        DISCUSSION_MODE_NONE,
        DISCUSSION_MODE_FULL,
    }
)
DEFAULT_MAX_COMMENTS_PER_POST = 100


def validate_discussion_mode(value: str) -> str:
    normalized = str(value).strip().lower()
    if normalized not in ALLOWED_DISCUSSION_MODES:
        allowed = ", ".join(sorted(ALLOWED_DISCUSSION_MODES))
        raise ValueError(f"Unsupported discussion mode {value!r}; expected {allowed}")
    return normalized


def validate_max_comments_per_post(value: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("max comments per post must be a positive integer") from exc
    if parsed <= 0:
        raise ValueError("max comments per post must be a positive integer")
    return parsed
