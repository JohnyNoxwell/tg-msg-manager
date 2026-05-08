from typing import Optional, Tuple

SUPPORTED_MEDIA_TYPES: Tuple[str, ...] = (
    "photo",
    "video",
    "document",
    "audio",
    "voice",
    "animation",
)


def normalize_media_type(
    value: Optional[str], mime_type: Optional[str] = None
) -> Optional[str]:
    normalized = (value or "").strip().lower()
    normalized_mime_type = (mime_type or "").strip().lower()

    if "thumbnail" in normalized or "thumb" in normalized:
        return None
    if "animation" in normalized or normalized_mime_type == "image/gif":
        return "animation"
    if "photo" in normalized:
        return "photo"
    if "voice" in normalized:
        return "voice"
    if "audio" in normalized:
        return "audio"
    if "video" in normalized:
        return "video"
    if "document" in normalized:
        return "document"

    if normalized_mime_type.startswith("image/"):
        return "photo"
    if normalized_mime_type.startswith("video/"):
        return "video"
    if normalized_mime_type.startswith("audio/ogg"):
        return "voice"
    if normalized_mime_type.startswith("audio/"):
        return "audio"
    if normalized_mime_type:
        return "document"
    return None


def parse_media_types(value: Optional[str]) -> Optional[Tuple[str, ...]]:
    if value is None:
        return None

    parts = [part.strip().lower() for part in str(value).split(",")]
    normalized = tuple(part for part in parts if part)
    if not normalized:
        raise ValueError("Media types list must not be empty")

    invalid = [part for part in normalized if part not in SUPPORTED_MEDIA_TYPES]
    if invalid:
        supported = ", ".join(SUPPORTED_MEDIA_TYPES)
        invalid_values = ", ".join(invalid)
        raise ValueError(
            f"Unsupported media types: {invalid_values}. Supported values: {supported}"
        )

    deduplicated = tuple(dict.fromkeys(normalized))
    return deduplicated
