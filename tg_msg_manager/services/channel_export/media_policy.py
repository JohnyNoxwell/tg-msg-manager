from typing import Optional

from .media_filename import (
    extension_from_filename,
    extension_from_mime_type,
    resolve_media_filename,
)
from .media_types import normalize_media_type

MEDIA_MODE_NONE = "none"
MEDIA_MODE_METADATA = "metadata"
MEDIA_MODE_FULL = "full"
ALLOWED_MEDIA_MODES = {
    MEDIA_MODE_NONE,
    MEDIA_MODE_METADATA,
    MEDIA_MODE_FULL,
}

EXTENSION_MEDIA_CATEGORIES = {
    ".jpg": "photos",
    ".jpeg": "photos",
    ".png": "photos",
    ".webp": "photos",
    ".gif": "animations",
    ".mp4": "videos",
    ".mov": "videos",
    ".mp3": "audio",
    ".m4a": "audio",
    ".ogg": "audio",
    ".wav": "audio",
    ".pdf": "documents",
    ".zip": "documents",
    ".rar": "documents",
    ".7z": "documents",
}


def validate_media_mode(value: str) -> str:
    normalized = (value or "").strip().lower()
    if normalized not in ALLOWED_MEDIA_MODES:
        raise ValueError(f"Unsupported media mode: {value!r}")
    return normalized


def media_category(media_type: Optional[str], mime_type: Optional[str]) -> str:
    normalized_media_type = (media_type or "").strip().lower()
    normalized_mime_type = (mime_type or "").strip().lower()

    if "thumbnail" in normalized_media_type or "thumb" in normalized_media_type:
        return "thumbnails"
    if "animation" in normalized_media_type or normalized_mime_type == "image/gif":
        return "animations"
    if "photo" in normalized_media_type:
        return "photos"
    if "voice" in normalized_media_type:
        return "voice"
    if "audio" in normalized_media_type:
        return "audio"
    if "video" in normalized_media_type:
        return "videos"

    if normalized_mime_type.startswith("image/"):
        return "photos"
    if normalized_mime_type.startswith("video/"):
        return "videos"
    if normalized_mime_type.startswith("audio/"):
        return "audio"
    if "document" in normalized_media_type:
        return "documents"
    if normalized_mime_type:
        return "documents"
    return "unknown"


def media_category_for_extension(extension: Optional[str], *, fallback: str) -> str:
    normalized = (extension or "").strip().lower()
    return EXTENSION_MEDIA_CATEGORIES.get(normalized, fallback)


def extension_for_media(
    *,
    media_type: Optional[str],
    mime_type: Optional[str],
    file_name: Optional[str],
) -> str:
    filename_extension = extension_from_filename(file_name)
    if filename_extension:
        return filename_extension

    mime_extension = extension_from_mime_type(mime_type)
    if mime_extension:
        return mime_extension

    if media_type and "photo" in media_type.lower():
        return ".jpg"
    return ".bin"


def build_media_relative_path(
    *,
    message_id: int,
    media_index: int,
    media_type: Optional[str],
    mime_type: Optional[str],
    file_name: Optional[str],
) -> str:
    category = media_category(media_type, mime_type)
    decision = resolve_media_filename(
        message_id=message_id,
        media_index=media_index,
        original_filename=file_name,
        mime_type=mime_type,
    )
    return f"media/{category}/{decision.filename}"


def initial_download_status(media_mode: str) -> str:
    normalized = validate_media_mode(media_mode)
    if normalized == MEDIA_MODE_NONE:
        return "skipped_by_mode"
    if normalized == MEDIA_MODE_FULL:
        return "pending"
    return "metadata_only"


def should_skip_by_size(
    *,
    file_size: Optional[int],
    max_media_size: Optional[int],
) -> bool:
    if file_size is None or max_media_size is None:
        return False
    return int(file_size) > int(max_media_size)


def is_media_type_allowed(
    *,
    media_type: Optional[str],
    mime_type: Optional[str],
    allowed_media_types: Optional[tuple[str, ...]],
) -> bool:
    normalized_media_type = normalize_media_type(media_type, mime_type)
    if normalized_media_type is None:
        return False
    if allowed_media_types is None:
        return True
    return normalized_media_type in allowed_media_types


def full_mode_pre_download_status(
    *,
    media_type: Optional[str],
    mime_type: Optional[str],
    file_size: Optional[int],
    max_media_size: Optional[int],
    allowed_media_types: Optional[tuple[str, ...]],
) -> str:
    if not is_media_type_allowed(
        media_type=media_type,
        mime_type=mime_type,
        allowed_media_types=allowed_media_types,
    ):
        return "skipped_by_type"
    if should_skip_by_size(file_size=file_size, max_media_size=max_media_size):
        return "skipped_by_size"
    return "pending"
