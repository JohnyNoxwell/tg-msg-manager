from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class PrivateArchiveStartedPayload:
    target_name: str
    user_id: int
    user_dir: str
    last_id: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "target_name": self.target_name,
            "user_id": self.user_id,
            "user_dir": self.user_dir,
            "last_id": self.last_id,
        }

    @classmethod
    def coerce(cls, value: Any) -> "PrivateArchiveStartedPayload":
        if isinstance(value, cls):
            return value
        if isinstance(value, Mapping):
            return cls(
                target_name=str(value.get("target_name") or ""),
                user_id=int(value.get("user_id", 0) or 0),
                user_dir=str(value.get("user_dir") or ""),
                last_id=int(value.get("last_id", 0) or 0),
            )
        raise TypeError(f"Unsupported private archive started payload: {type(value)!r}")


@dataclass()
class PrivateArchiveMediaStats:
    photo: int = 0
    video: int = 0
    voice: int = 0
    document: int = 0

    @classmethod
    def coerce(cls, value: Any) -> "PrivateArchiveMediaStats":
        if isinstance(value, cls):
            return value
        if isinstance(value, Mapping):
            return cls(
                photo=int(value.get("photo", value.get("Photo", 0)) or 0),
                video=int(value.get("video", value.get("Video", 0)) or 0),
                voice=int(value.get("voice", value.get("Voice", 0)) or 0),
                document=int(value.get("document", value.get("Document", 0)) or 0),
            )
        raise TypeError(f"Unsupported private archive media stats: {type(value)!r}")

    @property
    def total(self) -> int:
        return self.photo + self.video + self.voice + self.document

    def increment(self, media_type: Optional[str]) -> None:
        if not media_type:
            return
        if media_type == "Photo":
            self.photo += 1
        elif media_type == "Video":
            self.video += 1
        elif media_type == "Voice":
            self.voice += 1
        else:
            self.document += 1

    def as_dict(self) -> dict[str, int]:
        return {
            "Photo": self.photo,
            "Video": self.video,
            "Voice": self.voice,
            "Document": self.document,
        }

    def __getitem__(self, key: str) -> int:
        if key == "Photo":
            return self.photo
        if key == "Video":
            return self.video
        if key == "Voice":
            return self.voice
        if key == "Document":
            return self.document
        raise KeyError(key)

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default

    def values(self):
        return self.as_dict().values()


@dataclass()
class PrivateArchiveTransferStats:
    downloaded: int = 0
    skipped: int = 0

    @classmethod
    def coerce(cls, value: Any) -> "PrivateArchiveTransferStats":
        if isinstance(value, cls):
            return value
        if isinstance(value, Mapping):
            return cls(
                downloaded=int(value.get("downloaded", 0) or 0),
                skipped=int(value.get("skipped", 0) or 0),
            )
        raise TypeError(f"Unsupported private archive transfer stats: {type(value)!r}")

    def as_dict(self) -> dict[str, int]:
        return {
            "downloaded": self.downloaded,
            "skipped": self.skipped,
        }

    def __getitem__(self, key: str) -> int:
        if key == "downloaded":
            return self.downloaded
        if key == "skipped":
            return self.skipped
        raise KeyError(key)

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default


@dataclass(frozen=True)
class PrivateArchiveProgressPayload:
    count: int
    stats: PrivateArchiveMediaStats
    archive_stats: PrivateArchiveTransferStats

    def as_dict(self) -> dict[str, Any]:
        return {
            "count": self.count,
            "stats": self.stats.as_dict(),
            "archive_stats": self.archive_stats.as_dict(),
        }

    @classmethod
    def coerce(cls, value: Any) -> "PrivateArchiveProgressPayload":
        if isinstance(value, cls):
            return value
        if isinstance(value, Mapping):
            return cls(
                count=int(value.get("count", 0) or 0),
                stats=PrivateArchiveMediaStats.coerce(value.get("stats") or {}),
                archive_stats=PrivateArchiveTransferStats.coerce(
                    value.get("archive_stats") or {}
                ),
            )
        raise TypeError(
            f"Unsupported private archive progress payload: {type(value)!r}"
        )


@dataclass(frozen=True)
class PrivateArchiveMediaSavedPayload:
    filename: str
    path: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "filename": self.filename,
            "path": self.path,
        }

    @classmethod
    def coerce(cls, value: Any) -> "PrivateArchiveMediaSavedPayload":
        if isinstance(value, cls):
            return value
        if isinstance(value, Mapping):
            return cls(
                filename=str(value.get("filename") or ""),
                path=str(value.get("path") or ""),
            )
        raise TypeError(
            f"Unsupported private archive media-saved payload: {type(value)!r}"
        )


@dataclass(frozen=True)
class PrivateArchiveCompletedPayload:
    target_name: str
    count: int
    stats: PrivateArchiveMediaStats
    archive_stats: PrivateArchiveTransferStats

    def as_dict(self) -> dict[str, Any]:
        return {
            "target_name": self.target_name,
            "count": self.count,
            "stats": self.stats.as_dict(),
            "archive_stats": self.archive_stats.as_dict(),
        }

    @classmethod
    def coerce(cls, value: Any) -> "PrivateArchiveCompletedPayload":
        if isinstance(value, cls):
            return value
        if isinstance(value, Mapping):
            return cls(
                target_name=str(value.get("target_name") or ""),
                count=int(value.get("count", 0) or 0),
                stats=PrivateArchiveMediaStats.coerce(value.get("stats") or {}),
                archive_stats=PrivateArchiveTransferStats.coerce(
                    value.get("archive_stats") or {}
                ),
            )
        raise TypeError(
            f"Unsupported private archive completed payload: {type(value)!r}"
        )
