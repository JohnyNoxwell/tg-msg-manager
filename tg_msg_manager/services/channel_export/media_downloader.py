import hashlib
import os
from dataclasses import replace
from pathlib import Path
from typing import Any, Optional

from .media_policy import full_mode_pre_download_status
from .models import ChannelMediaRecord


def compute_file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


class ChannelMediaDownloader:
    def __init__(self, client: Any):
        self.client = client

    async def download(
        self,
        *,
        record: ChannelMediaRecord,
        media_ref: Any,
        output_dir: Path,
        max_media_size: Optional[int],
        allowed_media_types: Optional[tuple[str, ...]],
    ) -> ChannelMediaRecord:
        status = full_mode_pre_download_status(
            media_type=record.media_type,
            mime_type=record.mime_type,
            file_size=record.file_size,
            max_media_size=max_media_size,
            allowed_media_types=allowed_media_types,
        )
        if status != "pending":
            return replace(record, download_status=status, sha256=None, error=None)

        if media_ref is None:
            return replace(
                record,
                download_status="failed",
                sha256=None,
                error="Media reference is unavailable for download",
            )

        target_path = self._resolve_target_path(output_dir=output_dir, record=record)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if target_path.exists() and target_path.is_file():
            return replace(
                record,
                download_status="already_exists",
                sha256=compute_file_sha256(target_path),
                error=None,
            )

        if target_path.exists() and not target_path.is_file():
            return replace(
                record,
                download_status="failed",
                sha256=None,
                error=f"Target path is not a file: {target_path}",
            )

        try:
            result_path = await self.client.download_media(
                media_ref,
                file=os.fspath(target_path),
            )
            if result_path is None:
                self._cleanup_partial_file(target_path)
                return replace(
                    record,
                    download_status="failed",
                    sha256=None,
                    error="Telegram client returned no downloaded file path",
                )
            resolved_path = Path(result_path)
            if not resolved_path.exists() or not resolved_path.is_file():
                self._cleanup_partial_file(target_path)
                return replace(
                    record,
                    download_status="failed",
                    sha256=None,
                    error=f"Downloaded file is missing: {resolved_path}",
                )
            return replace(
                record,
                download_status="downloaded",
                sha256=compute_file_sha256(resolved_path),
                error=None,
            )
        except Exception as exc:
            self._cleanup_partial_file(target_path)
            return replace(
                record,
                download_status="failed",
                sha256=None,
                error=str(exc),
            )

    @staticmethod
    def _resolve_target_path(output_dir: Path, record: ChannelMediaRecord) -> Path:
        if not record.local_path:
            raise ValueError("Channel media record is missing local_path")
        return Path(output_dir) / record.local_path

    @staticmethod
    def _cleanup_partial_file(path: Path) -> None:
        if Path(path).exists() and Path(path).is_file():
            Path(path).unlink()
