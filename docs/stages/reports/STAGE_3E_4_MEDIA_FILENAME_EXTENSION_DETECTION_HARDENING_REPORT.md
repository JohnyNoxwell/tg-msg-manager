# Stage 3E.4 — Media Filename / Extension Detection Hardening Report

## 1. Summary

Stage 3E.4 hardened direct channel export media filename and extension resolution.

Known MP4/MOV media no longer falls back to `.bin` when Telegram MIME metadata or lightweight file signatures identify the content. `.bin` remains the fallback for genuinely unknown media.

## 2. Problem

Baseline inspection found that channel media filenames were built before download in `tg_msg_manager/services/channel_export/media_policy.py`. The old path used the original filename extension or `mimetypes.guess_extension()`, then fell back to `.bin`. Generic Telegram document media could therefore remain `.bin` even when downloaded bytes were MP4/QuickTime.

The downloader used the precomputed `ChannelMediaRecord.local_path` and computed `sha256` from that path after download. `media_manifest.jsonl` then recorded the old local path.

## 3. Detection priority

Media filenames now use this priority:

1. Safe Telegram original filename.
2. Telegram MIME type.
3. Lightweight magic-byte detection after download.
4. `.bin` fallback.

## 4. Files/modules changed

- `tg_msg_manager/services/channel_export/media_filename.py`
- `tg_msg_manager/services/channel_export/media_policy.py`
- `tg_msg_manager/services/channel_export/post_mapper.py`
- `tg_msg_manager/services/channel_export/media_downloader.py`
- `tg_msg_manager/services/channel_export/media_manifest_writer.py`
- `tg_msg_manager/services/channel_export/models.py`
- `tests/test_channel_export_media_filename.py`
- `tests/test_channel_export_media_downloader.py`
- `tests/test_channel_export_media_policy.py`
- `tests/test_channel_export_post_mapper.py`
- `tests/test_channel_export_renderers.py`
- `tests/test_channel_export_service.py`
- `README.md`
- `COMMANDS.md`
- `docs/architecture/README.md`
- `docs/architecture/MEDIA_HANDLING.md`

## 5. Filename safety rules

The resolver sanitizes Telegram-provided filenames by removing control characters, replacing path separators, removing traversal segments, rejecting absolute paths, and falling back when the safe filename becomes empty.

Original filenames are preserved as safe deterministic variants prefixed with message id and media index, for example `0000058947_01_video.mp4`. If no safe original filename exists, fallback naming remains `<message_id>_<media_index><extension>`.

## 6. MIME mapping

Explicit mappings were added for:

- `video/mp4` -> `.mp4`
- `video/quicktime` -> `.mov`
- `image/jpeg` -> `.jpg`
- `image/png` -> `.png`
- `image/webp` -> `.webp`
- `image/gif` -> `.gif`
- `application/pdf` -> `.pdf`
- `audio/mpeg` -> `.mp3`
- `audio/mp4` -> `.m4a`
- `audio/ogg` -> `.ogg`
- `audio/wav` -> `.wav`
- `application/zip` -> `.zip`
- `application/x-rar-compressed` -> `.rar`
- `application/x-7z-compressed` -> `.7z`

Stdlib `mimetypes` remains a secondary MIME fallback for safe extensions.

## 7. Magic-byte detection

Lightweight detection was added for:

- ISO Base Media / MP4 `ftyp` headers -> `.mp4`
- QuickTime `ftypqt` headers -> `.mov`
- JPEG -> `.jpg`
- PNG -> `.png`
- GIF87a/GIF89a -> `.gif`
- PDF -> `.pdf`
- ZIP -> `.zip`

No shell `file` invocation, ffmpeg processing, heavy dependency, content analysis, OCR, speech-to-text, transcoding, or classification was added.

## 8. Manifest changes

`media_manifest.jsonl` keeps all existing fields and now also records:

- `original_filename`
- `detected_extension`
- `filename_strategy`
- `final_filename`
- `final_path`

The manifest references the final resolved filename/path after magic-byte correction, not the old `.bin` path.

## 9. Tests

Tests were added or updated for:

- original filename extension preservation
- unsafe filename sanitization
- path traversal blocking
- required MIME extension mappings
- MP4 and QuickTime magic-byte detection
- JPEG, PNG, GIF, PDF, and ZIP magic-byte detection
- unknown content fallback to `.bin`
- already existing resolved `.mp4` media
- sha256 computation from the final resolved path
- media manifest final path references
- no final `.bin` for detected MP4 signatures

Existing media status behavior and public CLI command coverage were preserved.

## 10. Verification results

- `pytest tests/test_channel_export_media_downloader.py`: passed, 8 tests.
- `pytest tests/test_channel_export_*.py`: passed, 142 tests and 25 subtests.
- `python3 -m compileall tg_msg_manager`: passed.
- `ruff check tg_msg_manager tests`: passed.
- `ruff format --check tg_msg_manager tests`: passed.
- `python3 -m tg_msg_manager.cli export-channel --help`: passed.
- `make test`: passed, 348 tests.
- `make verify`: passed; compileall, ruff check, ruff format check, and unittest suite completed successfully.

## 11. Runtime behavior statement

No CLI behavior changed.

No media mode default changed.

No SQLite schema changed.

No analytics/OCR/STT/transcoding added.

No product feature outside media filename hardening was added.

Discussion media full download was not added.

## 12. Remaining limitations

Magic-byte detection is intentionally lightweight and limited to the signatures scoped for this stage. Rich container inspection, codec inspection, thumbnail generation, OCR, speech-to-text, transcoding, and media classification remain out of scope.

Historical metadata-only rows are not backfilled unless those posts are exported again in a run that processes their media records.

## 13. Status

Stage 3E.4 is complete.
