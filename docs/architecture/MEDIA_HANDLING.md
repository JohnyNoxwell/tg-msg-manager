# Media Handling

Last updated: 2026-05-08

## Direct Channel Export Media

`export-channel` is a filesystem-first dataset export path. Channel media download logic lives under `tg_msg_manager/services/channel_export/`; `ChannelExportService` remains orchestration-only.

Media filename resolution is handled by `tg_msg_manager/services/channel_export/media_filename.py` using this priority:

1. Safe Telegram original filename.
2. Telegram MIME type.
3. Lightweight magic-byte detection from downloaded bytes.
4. `.bin` fallback for genuinely unknown content.

The resolver sanitizes path separators and control characters, prevents traversal or absolute paths, and uses deterministic message/id-prefixed filenames to avoid collisions. Known MP4/MOV, image, audio, PDF, ZIP, RAR, and 7z MIME types should not fall back to `.bin`. Generic/unknown MIME types can be corrected after download using lightweight signatures such as ISO Base Media `ftyp`, QuickTime `qt`, JPEG, PNG, GIF, PDF, and ZIP headers. When a generic Telegram document is corrected to a concrete media type, the final path uses the matching media subdirectory, for example `media/videos/` for MP4/MOV.

`media_manifest.jsonl` preserves existing status fields and records final media paths. No SQLite persistence, schema migration, OCR, speech-to-text, media recognition, transcoding, thumbnail generation, ffmpeg processing, analytics, or OSINT interpretation belongs in this media filename path.
