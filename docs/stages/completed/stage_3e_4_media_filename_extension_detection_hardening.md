# STAGE 3E.4 — MEDIA FILENAME / EXTENSION DETECTION HARDENING

## 0. CODEX ENTRY PROMPT

```text
Read AGENTS.md first.

You are working on tg-msg-manager.

This task is Stage 3E.4 — Media Filename / Extension Detection Hardening.

This is a media export hardening task, not a new analytics feature.

Follow this file exactly.
Do not change public CLI behavior unless explicitly required here.
Do not change SQLite schema.
Do not add analytics, OSINT, OCR, STT, or media content analysis.
```

---

## 1. PURPOSE

Current problem:

```text
Some Telegram document/video media are downloaded as files with `.bin` extension even when their actual content is MP4/MOV/etc.
```

Observed example:

```text
0000058947_01.bin: MP4 v2
0000058948_01.bin: MP4 v2
0000058991_01.bin: Apple QuickTime movie (.MOV/QT)
```

Goal:

```text
Improve media filename and extension detection so downloaded media uses correct safe filenames and extensions whenever possible.
```

Expected result:

```text
MP4-like media should be saved as `.mp4`.
QuickTime media should be saved as `.mov`.
Known document/image/audio/video types should not fall back to `.bin` unless type is genuinely unknown.
```

---

## 2. HARD PROHIBITIONS

Do not implement:

```text
- media analysis
- OCR
- speech-to-text
- video/audio/image recognition
- thumbnail generation
- transcoding
- ffmpeg processing
- content classification
- analytics
- OSINT interpretation
- SQLite schema changes
- migrations
- DB persistence changes
- discussion media full download
- new dashboard/UI
```

Do not change behavior of unrelated commands:

```text
export
db-export
export-pm
retry
report
clean
delete
schedule
setup
```

Protected files:

```text
tg_msg_manager/services/export/service.py
tg_msg_manager/services/db_export/service.py
tg_msg_manager/services/private_archive/service.py
tg_msg_manager/services/context/engine.py
tg_msg_manager/services/channel_export/service.py
```

Rules:

```text
- Do not add feature logic to protected files.
- Keep ChannelExportService orchestration-only.
- Media filename logic must live under tg_msg_manager/services/channel_export/.
```

---

## 3. SCOPE

Allowed:

```text
- improve media filename construction
- improve extension detection
- use Telegram-provided filename when safe
- use Telegram MIME type when available
- use lightweight magic-byte detection when MIME/filename is missing or generic
- update media manifest fields if already extensible
- add tests
- update docs
- create stage report
```

Forbidden:

```text
- changing dataset meaning
- changing media download mode defaults
- changing --media metadata/full behavior
- changing media status names
- changing state schemas
- changing SQLite schema
- downloading additional media types by default
- rewriting media downloader architecture broadly
```

---

## 4. CURRENT EXPECTED BEHAVIOR TO PRESERVE

Preserve existing media statuses:

```text
metadata_only
downloaded
already_exists
skipped_by_size
skipped_by_type
failed
```

Preserve:

```text
- --media metadata default
- --media full explicit mode
- --max-media-size behavior
- --media-types allowlist behavior
- failed media does not fail entire channel export
- sha256 behavior
- media_manifest.jsonl writing
- incremental behavior
```

---

## 5. TARGET DESIGN

Add a focused filename/extension resolver.

Suggested module:

```text
tg_msg_manager/services/channel_export/media_filename.py
```

Suggested responsibilities:

```text
- sanitize Telegram-provided original filenames
- extract extension from original filename if safe
- infer extension from MIME type
- infer extension from lightweight file signature / magic bytes
- choose final filename
- preserve deterministic fallback naming
```

Do not put this logic into:

```text
ChannelExportService
cli_parser.py
cli_commands.py
```

---

## 6. DETECTION PRIORITY

Use this priority order:

```text
1. Telegram original filename if present and safe
2. MIME type from Telegram media metadata
3. Lightweight magic-byte / file signature detection
4. fallback `.bin`
```

### 6.1 Original filename rules

If Telegram provides a filename:

```text
- preserve extension when safe
- sanitize path separators
- remove control characters
- prevent path traversal
- prevent absolute paths
- keep deterministic fallback if filename is empty after sanitization
```

Examples:

```text
"video.mp4" -> "video.mp4"
"../video.mp4" -> "video.mp4" or sanitized safe equivalent
"/tmp/video.mp4" -> "video.mp4" or sanitized safe equivalent
"bad/name.mov" -> "bad_name.mov" or safe equivalent
```

### 6.2 MIME type rules

Map common MIME types:

```text
video/mp4 -> .mp4
video/quicktime -> .mov
image/jpeg -> .jpg
image/png -> .png
image/webp -> .webp
image/gif -> .gif
application/pdf -> .pdf
audio/mpeg -> .mp3
audio/mp4 -> .m4a
audio/ogg -> .ogg
audio/wav -> .wav
application/zip -> .zip
application/x-rar-compressed -> .rar
application/x-7z-compressed -> .7z
```

Use Python stdlib `mimetypes` where useful, but add explicit overrides for Telegram/media cases if needed.

### 6.3 Magic-byte rules

Add lightweight signature detection for downloaded temp/file bytes.

Minimum required signatures:

```text
MP4 / ISO Base Media:
  bytes 4..8 == b"ftyp" -> .mp4

QuickTime MOV:
  bytes 4..8 == b"ftyp" and brand indicates qt -> .mov
  or known QuickTime compatible brands if present

JPEG:
  startswith FF D8 FF -> .jpg

PNG:
  startswith 89 50 4E 47 0D 0A 1A 0A -> .png

GIF:
  startswith GIF87a or GIF89a -> .gif

PDF:
  startswith %PDF -> .pdf

ZIP:
  startswith PK\x03\x04 -> .zip
```

Do not use heavy external dependencies unless already present in the project.

Do not call shell `file`.

Do not invoke ffmpeg.

---

## 7. FILENAME FORMAT

If no safe original filename exists, preserve deterministic project naming:

```text
<message_id>_<media_index><extension>
```

Example:

```text
0000058947_01.mp4
0000058991_01.mov
0000059019_01.pdf
0000059036_01.bin
```

If original filename exists, avoid collisions.

Collision behavior:

```text
- if final filename already exists for a different media item, append deterministic suffix
- do not overwrite unrelated files
- preserve already_exists behavior when same expected file exists
```

Suggested collision patterns:

```text
filename.mp4
filename_02.mp4
filename_03.mp4
```

or deterministic ID-prefixed name:

```text
0000058947_01_filename.mp4
```

Choose the least invasive pattern compatible with current project conventions.

---

## 8. MEDIA MANIFEST UPDATES

Inspect current `media_manifest.jsonl` schema before changing.

If manifest already supports additional fields, add:

```text
original_filename
mime_type
detected_extension
filename_strategy
final_filename
final_path
```

If adding new fields would violate strict schema tests or current compatibility policy, then:

```text
- preserve existing schema
- add only fields that current contract allows
- document why richer manifest fields are deferred
```

Preferred behavior:

```text
media_manifest.jsonl should make it clear why a file got `.mp4`, `.mov`, `.pdf`, or `.bin`.
```

Potential `filename_strategy` values:

```text
original_filename
mime_type
magic_bytes
fallback_bin
```

Do not remove existing fields.

Do not rename existing fields unless explicitly required and covered by migration/docs.

---

## 9. TASKS

### A. Baseline inspection

- [ ] Read `AGENTS.md`.
- [ ] Inspect current media downloader:
  ```text
  tg_msg_manager/services/channel_export/media_downloader.py
  ```
- [ ] Inspect media policy/types:
  ```text
  tg_msg_manager/services/channel_export/media_policy.py
  tg_msg_manager/services/channel_export/media_types.py
  ```
- [ ] Inspect media manifest writer:
  ```text
  tg_msg_manager/services/channel_export/media_manifest_writer.py
  ```
- [ ] Inspect media-related models:
  ```text
  tg_msg_manager/services/channel_export/models.py
  ```
- [ ] Inspect tests:
  ```text
  tests/test_channel_export_media_downloader.py
  tests/test_channel_export_service.py
  tests/test_channel_export_*.py
  ```

### B. Identify current filename behavior

- [ ] Find where filenames are generated.
- [ ] Find where `.bin` fallback is assigned.
- [ ] Find whether MIME type is available before download.
- [ ] Find whether original filename is available in media metadata.
- [ ] Find whether final path is written before file content is downloaded.
- [ ] Record current behavior in the stage report.

### C. Create media filename resolver

Create:

```text
tg_msg_manager/services/channel_export/media_filename.py
```

Implement focused functions/classes, for example:

```python
@dataclass(frozen=True)
class MediaFilenameDecision:
    filename: str
    extension: str
    strategy: str
    original_filename: str | None
    mime_type: str | None
```

Suggested functions:

```python
sanitize_original_filename(value: str | None) -> str | None
extension_from_filename(filename: str | None) -> str | None
extension_from_mime_type(mime_type: str | None) -> str | None
extension_from_magic_bytes(header: bytes) -> str | None
build_fallback_filename(message_id: int, media_index: int, extension: str) -> str
resolve_media_filename(...) -> MediaFilenameDecision
```

Keep functions pure where possible.

### D. Add magic-byte detection

Implement lightweight detection.

Required tests:

- [ ] MP4 `ftypisom` -> `.mp4`
- [ ] MP4 `ftypmp42` -> `.mp4`
- [ ] QuickTime `ftypqt  ` -> `.mov`
- [ ] JPEG -> `.jpg`
- [ ] PNG -> `.png`
- [ ] GIF -> `.gif`
- [ ] PDF -> `.pdf`
- [ ] ZIP -> `.zip`
- [ ] unknown bytes -> `None`

### E. Integrate resolver into media downloader

Update media downloader so:

- [ ] if original filename is safe, use it or a deterministic safe variant
- [ ] if no filename, use MIME-derived extension
- [ ] if MIME is missing/generic, use magic-byte detection after download/header read
- [ ] if magic-byte detection changes extension from `.bin` to known type, final file path uses detected extension
- [ ] `.bin` remains fallback only when type unknown
- [ ] sha256 still computed for final file
- [ ] already_exists still works with the resolved final path
- [ ] failed download behavior unchanged

Important:

```text
If final filename requires magic-byte detection after download, write to temp path first, detect extension, then commit/rename to final path.
```

If Stage 3E.1 atomic writer exists, integrate with it. If not, keep change minimal and safe.

### F. Manifest integration

Update manifest/media record if appropriate:

- [ ] preserve existing fields
- [ ] add `original_filename` if safe
- [ ] add `mime_type` if available
- [ ] add `detected_extension` if available
- [ ] add `filename_strategy` if useful
- [ ] update tests/docs accordingly

If not adding manifest fields:

- [ ] explain why in report
- [ ] still ensure final filenames use correct extensions

### G. Tests

Add or update tests for:

- [ ] original filename with extension preserved
- [ ] unsafe filename sanitized
- [ ] path traversal blocked
- [ ] MIME `video/mp4` -> `.mp4`
- [ ] MIME `video/quicktime` -> `.mov`
- [ ] generic/unknown MIME + MP4 magic bytes -> `.mp4`
- [ ] generic/unknown MIME + QuickTime magic bytes -> `.mov`
- [ ] unknown content -> `.bin`
- [ ] already existing resolved `.mp4` file -> `already_exists`
- [ ] sha256 computed after final naming
- [ ] media_manifest references final path, not old `.bin`
- [ ] no final `.bin` for known MP4/MOV signatures
- [ ] no public CLI behavior change

Do not weaken existing media tests.

### H. Docs

Update relevant docs:

```text
README.md
COMMANDS.md
docs/architecture/MEDIA_HANDLING.md
docs/architecture/DATASET_FORMAT.md
docs/stages/reports/
```

If these files do not exist, update the closest equivalent.

Docs must state:

```text
- media filenames are resolved from original filename, MIME type, then magic bytes
- .bin is fallback only for unknown types
- no media content analysis/transcoding is performed
- media manifest records final paths
```

### I. Report

Create:

```text
docs/stages/reports/STAGE_3E_4_MEDIA_FILENAME_EXTENSION_DETECTION_HARDENING_REPORT.md
```

Required sections:

```text
# Stage 3E.4 — Media Filename / Extension Detection Hardening Report

## 1. Summary
## 2. Problem
## 3. Detection priority
## 4. Files/modules changed
## 5. Filename safety rules
## 6. MIME mapping
## 7. Magic-byte detection
## 8. Manifest changes
## 9. Tests
## 10. Verification results
## 11. Runtime behavior statement
## 12. Remaining limitations
## 13. Status
```

Must state:

```text
No CLI behavior changed.
No media mode default changed.
No SQLite schema changed.
No analytics/OCR/STT/transcoding added.
No product feature outside media filename hardening was added.
```

---

## 10. VERIFICATION

Run:

```bash
pytest tests/test_channel_export_media_downloader.py
pytest tests/test_channel_export_*.py
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
ruff format --check tg_msg_manager tests
python3 -m tg_msg_manager.cli export-channel --help
```

If practical:

```bash
make test
make verify
```

Do not claim unrun commands passed.

---

## 11. COMPLETION CRITERIA

Complete only if:

- [ ] `.bin` fallback no longer used for detected MP4/MOV media.
- [ ] original safe filenames are preserved or safely normalized.
- [ ] MIME-based extension detection works.
- [ ] magic-byte detection works.
- [ ] `.bin` remains fallback for genuinely unknown media.
- [ ] media manifest references final filenames.
- [ ] tests cover MP4/MOV fallback cases.
- [ ] docs updated.
- [ ] stage report created.
- [ ] no CLI behavior changed.
- [ ] no SQLite schema changed.
- [ ] no analytics/transcoding added.

---

## 12. FINAL CLEANUP

After this stage is complete and report exists:

- [ ] Move this task file from `docs/stages/active/` to `docs/stages/completed/`.
- [ ] Update `docs/stages/README.md`.
- [ ] Ensure `docs/stages/active/` contains only unfinished or next active work.

---

## 13. FINAL RESPONSE FORMAT

```text
## Summary
- media filename/extension detection hardened
- known MP4/MOV files no longer saved as .bin

## Files changed
- path
- path

## Verification
- command: result

## Behavior
- CLI unchanged
- media mode defaults unchanged
- dataset schema unchanged unless stated
- SQLite unchanged
- no analytics/OCR/STT/transcoding added

## Remaining limitations
- item
- item

## Stage status
Stage 3E.4: complete / partial / blocked
```
