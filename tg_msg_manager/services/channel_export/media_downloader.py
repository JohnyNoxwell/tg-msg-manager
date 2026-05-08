import hashlib
import os
from dataclasses import replace
from pathlib import Path
from typing import Any, Optional

from .media_filename import (
    FILENAME_STRATEGY_FALLBACK,
    FILENAME_STRATEGY_MAGIC,
    resolve_media_filename,
)
from .media_policy import full_mode_pre_download_status, media_category_for_extension
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
            existing_record = self._record_with_detected_path(
                record=record,
                output_dir=output_dir,
                downloaded_path=target_path,
            )
            existing_path = self._resolve_target_path(
                output_dir=output_dir,
                record=existing_record,
            )
            if existing_path != target_path:
                if existing_path.exists() and existing_path.is_file():
                    return replace(
                        existing_record,
                        download_status="already_exists",
                        sha256=compute_file_sha256(existing_path),
                        error=None,
                    )
                if existing_path.exists() and not existing_path.is_file():
                    return replace(
                        existing_record,
                        download_status="failed",
                        sha256=None,
                        error=f"Target path is not a file: {existing_path}",
                    )
                existing_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.replace(existing_path)
            return replace(
                existing_record,
                download_status="already_exists",
                sha256=compute_file_sha256(existing_path),
                error=None,
            )

        if target_path.exists() and not target_path.is_file():
            return replace(
                record,
                download_status="failed",
                sha256=None,
                error=f"Target path is not a file: {target_path}",
            )

        temp_path = self._temporary_download_path(target_path)

        try:
            result_path = await self.client.download_media(
                media_ref,
                file=os.fspath(temp_path),
            )
            if result_path is None:
                self._cleanup_partial_file(temp_path)
                return replace(
                    record,
                    download_status="failed",
                    sha256=None,
                    error="Telegram client returned no downloaded file path",
                )
            resolved_path = Path(result_path)
            if not resolved_path.exists() or not resolved_path.is_file():
                self._cleanup_partial_file(temp_path)
                return replace(
                    record,
                    download_status="failed",
                    sha256=None,
                    error=f"Downloaded file is missing: {resolved_path}",
                )
            final_record = self._record_with_detected_path(
                record=record,
                output_dir=output_dir,
                downloaded_path=resolved_path,
            )
            final_path = self._resolve_target_path(
                output_dir=output_dir,
                record=final_record,
            )
            final_path.parent.mkdir(parents=True, exist_ok=True)

            if final_path.exists() and final_path.is_file():
                self._cleanup_partial_file(resolved_path)
                return replace(
                    final_record,
                    download_status="already_exists",
                    sha256=compute_file_sha256(final_path),
                    error=None,
                )
            if final_path.exists() and not final_path.is_file():
                self._cleanup_partial_file(resolved_path)
                return replace(
                    final_record,
                    download_status="failed",
                    sha256=None,
                    error=f"Target path is not a file: {final_path}",
                )

            if resolved_path != final_path:
                resolved_path.replace(final_path)

            return replace(
                final_record,
                download_status="downloaded",
                sha256=compute_file_sha256(final_path),
                error=None,
            )
        except Exception as exc:
            self._cleanup_partial_file(temp_path)
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
    def _temporary_download_path(target_path: Path) -> Path:
        return target_path.with_name(f".{target_path.name}.download")

    @staticmethod
    def _read_header(path: Path) -> bytes:
        with Path(path).open("rb") as handle:
            return handle.read(64)

    def _record_with_detected_path(
        self,
        *,
        record: ChannelMediaRecord,
        output_dir: Path,
        downloaded_path: Path,
    ) -> ChannelMediaRecord:
        current_strategy = record.filename_strategy or FILENAME_STRATEGY_FALLBACK
        if current_strategy != FILENAME_STRATEGY_FALLBACK:
            final_path = self._resolve_target_path(output_dir=output_dir, record=record)
            return replace(
                record,
                final_filename=final_path.name,
                final_path=record.local_path,
            )

        header = self._read_header(downloaded_path)
        decision = resolve_media_filename(
            message_id=record.message_id,
            media_index=record.media_index,
            original_filename=record.file_name,
            mime_type=record.mime_type,
            header=header,
        )
        if decision.strategy != FILENAME_STRATEGY_MAGIC:
            return replace(
                record,
                original_filename=decision.original_filename,
                detected_extension=decision.extension,
                filename_strategy=decision.strategy,
                final_filename=Path(record.local_path or decision.filename).name,
                final_path=record.local_path,
            )

        original_parent = Path(record.local_path or "").parent
        fallback_category = original_parent.name or "unknown"
        category = media_category_for_extension(
            decision.extension,
            fallback=fallback_category,
        )
        relative_path = (Path("media") / category / decision.filename).as_posix()
        return replace(
            record,
            local_path=relative_path,
            original_filename=decision.original_filename,
            detected_extension=decision.extension,
            filename_strategy=decision.strategy,
            final_filename=decision.filename,
            final_path=relative_path,
        )

    @staticmethod
    def _cleanup_partial_file(path: Path) -> None:
        if Path(path).exists() and Path(path).is_file():
            Path(path).unlink()
