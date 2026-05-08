import re
from typing import Optional

DEFAULT_MAX_MEDIA_SIZE_BYTES = 50 * 1024 * 1024

_SIZE_RE = re.compile(r"^\s*(\d+)\s*([kmgt]?b)?\s*$", re.IGNORECASE)
_SIZE_MULTIPLIERS = {
    None: 1,
    "b": 1,
    "kb": 1024,
    "mb": 1024 * 1024,
    "gb": 1024 * 1024 * 1024,
    "tb": 1024 * 1024 * 1024 * 1024,
}


def parse_media_size(value: Optional[object]) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, int):
        if value <= 0:
            raise ValueError("Media size must be a positive integer")
        return value

    match = _SIZE_RE.match(str(value))
    if match is None:
        raise ValueError(f"Invalid media size: {value!r}")

    amount = int(match.group(1))
    if amount <= 0:
        raise ValueError("Media size must be a positive integer")

    unit = (match.group(2) or "").strip().lower() or None
    multiplier = _SIZE_MULTIPLIERS.get(unit)
    if multiplier is None:
        raise ValueError(f"Unsupported media size unit: {unit!r}")
    return amount * multiplier
