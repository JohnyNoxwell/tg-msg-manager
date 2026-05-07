import mimetypes
from pathlib import Path
from typing import Optional

MEDIA_MODE_NONE = "none"
MEDIA_MODE_METADATA = "metadata"
MEDIA_MODE_FULL = "full"
ALLOWED_MEDIA_MODES = {
    MEDIA_MODE_NONE,
    MEDIA_MODE_METADATA,
    MEDIA_MODE_FULL,
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
    if "document" in normalized_media_type:
        return "documents"

    if normalized_mime_type.startswith("image/"):
        return "photos"
    if normalized_mime_type.startswith("video/"):
        return "videos"
    if normalized_mime_type.startswith("audio/"):
        return "audio"
    if normalized_mime_type:
        return "documents"
    return "unknown"


def _safe_extension(value: str) -> Optional[str]:
    normalized = (value or "").strip().lower()
    if not normalized.startswith("."):
        return None
    suffix = normalized[1:]
    if not suffix or len(suffix) > 10:
        return None
    if not suffix.replace("+", "").isalnum():
        return None
    return normalized


def extension_for_media(
    *,
    media_type: Optional[str],
    mime_type: Optional[str],
    file_name: Optional[str],
) -> str:
    if file_name:
        extension = _safe_extension(Path(file_name).suffix)
        if extension:
            return extension

    guessed = mimetypes.guess_extension((mime_type or "").strip().lower(), strict=False)
    safe_guessed = _safe_extension(guessed or "")
    if safe_guessed:
        return safe_guessed

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
    extension = extension_for_media(
        media_type=media_type,
        mime_type=mime_type,
        file_name=file_name,
    )
    return f"media/{category}/{message_id:010d}_{media_index:02d}{extension}"


def initial_download_status(media_mode: str) -> str:
    normalized = validate_media_mode(media_mode)
    if normalized == MEDIA_MODE_NONE:
        return "skipped_by_mode"
    if normalized == MEDIA_MODE_FULL:
        return "pending"
    return "metadata_only"
