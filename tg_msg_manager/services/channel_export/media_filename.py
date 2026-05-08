import mimetypes
import re
from dataclasses import dataclass
from pathlib import PurePosixPath, PureWindowsPath
from typing import Optional


FILENAME_STRATEGY_ORIGINAL = "original_filename"
FILENAME_STRATEGY_MIME = "mime_type"
FILENAME_STRATEGY_MAGIC = "magic_bytes"
FILENAME_STRATEGY_FALLBACK = "fallback_bin"

GENERIC_MIME_TYPES = {
    "application/octet-stream",
    "binary/octet-stream",
    "application/x-binary",
}

MIME_EXTENSION_OVERRIDES = {
    "video/mp4": ".mp4",
    "video/quicktime": ".mov",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "application/pdf": ".pdf",
    "audio/mpeg": ".mp3",
    "audio/mp4": ".m4a",
    "audio/ogg": ".ogg",
    "audio/wav": ".wav",
    "audio/wave": ".wav",
    "audio/x-wav": ".wav",
    "application/zip": ".zip",
    "application/x-rar-compressed": ".rar",
    "application/vnd.rar": ".rar",
    "application/x-7z-compressed": ".7z",
}


@dataclass(frozen=True)
class MediaFilenameDecision:
    filename: str
    extension: str
    strategy: str
    original_filename: Optional[str]
    mime_type: Optional[str]


def _safe_extension(value: Optional[str]) -> Optional[str]:
    normalized = (value or "").strip().lower()
    if not normalized.startswith("."):
        return None
    suffix = normalized[1:]
    if not suffix or len(suffix) > 10:
        return None
    if not suffix.replace("+", "").isalnum():
        return None
    return normalized


def _normalize_mime_type(value: Optional[str]) -> Optional[str]:
    normalized = (value or "").split(";", 1)[0].strip().lower()
    return normalized or None


def sanitize_original_filename(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None

    without_controls = "".join(
        char for char in str(value) if char >= " " and char != "\x7f"
    ).strip()
    if not without_controls:
        return None

    normalized = without_controls.replace("\\", "/")
    parts = [
        part.strip()
        for part in normalized.split("/")
        if part.strip() and part.strip() not in {".", ".."}
    ]
    if not parts:
        return None

    filename = "_".join(parts)
    filename = re.sub(r"[\x00-\x1f\x7f]", "", filename).strip()
    filename = filename.replace("/", "_").replace("\\", "_")
    filename = filename.strip(" .")
    if not filename:
        return None
    if filename in {".", ".."}:
        return None
    if PurePosixPath(filename).is_absolute() or PureWindowsPath(filename).is_absolute():
        return None
    if "/" in filename or "\\" in filename:
        return None
    return filename


def extension_from_filename(filename: Optional[str]) -> Optional[str]:
    sanitized = sanitize_original_filename(filename)
    if not sanitized:
        return None
    return _safe_extension(PurePosixPath(sanitized).suffix)


def extension_from_mime_type(mime_type: Optional[str]) -> Optional[str]:
    normalized = _normalize_mime_type(mime_type)
    if not normalized or normalized in GENERIC_MIME_TYPES:
        return None
    override = MIME_EXTENSION_OVERRIDES.get(normalized)
    if override:
        return override
    guessed = mimetypes.guess_extension(normalized, strict=False)
    return _safe_extension(guessed)


def extension_from_magic_bytes(header: bytes) -> Optional[str]:
    if header.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if header.startswith((b"GIF87a", b"GIF89a")):
        return ".gif"
    if header.startswith(b"%PDF"):
        return ".pdf"
    if header.startswith(b"PK\x03\x04"):
        return ".zip"
    if len(header) >= 12 and header[4:8] == b"ftyp":
        major_brand = header[8:12].lower()
        compatible_brands = header[16:64].lower()
        if major_brand.startswith(b"qt") or b"qt  " in compatible_brands:
            return ".mov"
        return ".mp4"
    return None


def build_fallback_filename(
    *,
    message_id: int,
    media_index: int,
    extension: str,
) -> str:
    safe_extension = _safe_extension(extension) or ".bin"
    return f"{message_id:010d}_{media_index:02d}{safe_extension}"


def build_original_filename(
    *,
    message_id: int,
    media_index: int,
    original_filename: str,
    extension: str,
) -> str:
    safe_original = sanitize_original_filename(original_filename)
    if not safe_original:
        return build_fallback_filename(
            message_id=message_id,
            media_index=media_index,
            extension=extension,
        )

    safe_extension = _safe_extension(extension) or ".bin"
    current_extension = extension_from_filename(safe_original)
    if current_extension:
        stem = safe_original[: -len(current_extension)]
        safe_extension = current_extension
    else:
        stem = safe_original
    stem = stem.strip(" ._") or "media"
    return f"{message_id:010d}_{media_index:02d}_{stem}{safe_extension}"


def resolve_media_filename(
    *,
    message_id: int,
    media_index: int,
    original_filename: Optional[str],
    mime_type: Optional[str],
    header: Optional[bytes] = None,
) -> MediaFilenameDecision:
    safe_original = sanitize_original_filename(original_filename)
    original_extension = extension_from_filename(safe_original)
    normalized_mime_type = _normalize_mime_type(mime_type)

    if safe_original and original_extension:
        return MediaFilenameDecision(
            filename=build_original_filename(
                message_id=message_id,
                media_index=media_index,
                original_filename=safe_original,
                extension=original_extension,
            ),
            extension=original_extension,
            strategy=FILENAME_STRATEGY_ORIGINAL,
            original_filename=safe_original,
            mime_type=normalized_mime_type,
        )

    mime_extension = extension_from_mime_type(normalized_mime_type)
    if mime_extension:
        filename = (
            build_original_filename(
                message_id=message_id,
                media_index=media_index,
                original_filename=safe_original,
                extension=mime_extension,
            )
            if safe_original
            else build_fallback_filename(
                message_id=message_id,
                media_index=media_index,
                extension=mime_extension,
            )
        )
        return MediaFilenameDecision(
            filename=filename,
            extension=mime_extension,
            strategy=FILENAME_STRATEGY_MIME,
            original_filename=safe_original,
            mime_type=normalized_mime_type,
        )

    magic_extension = extension_from_magic_bytes(header or b"") if header else None
    if magic_extension:
        filename = (
            build_original_filename(
                message_id=message_id,
                media_index=media_index,
                original_filename=safe_original,
                extension=magic_extension,
            )
            if safe_original
            else build_fallback_filename(
                message_id=message_id,
                media_index=media_index,
                extension=magic_extension,
            )
        )
        return MediaFilenameDecision(
            filename=filename,
            extension=magic_extension,
            strategy=FILENAME_STRATEGY_MAGIC,
            original_filename=safe_original,
            mime_type=normalized_mime_type,
        )

    return MediaFilenameDecision(
        filename=build_fallback_filename(
            message_id=message_id,
            media_index=media_index,
            extension=".bin",
        ),
        extension=".bin",
        strategy=FILENAME_STRATEGY_FALLBACK,
        original_filename=safe_original,
        mime_type=normalized_mime_type,
    )
