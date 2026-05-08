# STAGE 3B — MEDIA DOWNLOAD HARDENING — CODEX TASK FILE

Status: completed
Stage: 3B
Scope: historical task instructions

## 0. PURPOSE

This file is intended for Codex / AI coding agent.

Stage 3B extends the already implemented `export-channel` pipeline with safe, resumable, controlled full media download.

This is not an analytics stage.

Stage 3B must reuse the Stage 3A / 3A.1 architecture:
- `services/channel_export/`
- `channel_export_state.json`
- append/update pattern
- progress events
- CLI progress rendering
- `manifest.json`
- `messages.jsonl`
- `messages.txt`
- `media_manifest.jsonl`
- `media/`

---

# 1. COPY-PASTE PROMPT FOR CODEX

```text
Read AGENTS.md first.

Then read:
- docs/stages/stage_3a_direct_channel_export_backlog.md
- docs/stages/stage_3a_direct_channel_export_agent_tasks.md
- docs/refactor/STAGE_3A_DIRECT_CHANNEL_EXPORT_REPORT.md
- docs/refactor/STAGE_3A_1_CHANNEL_EXPORT_OPERATIONAL_HARDENING_REPORT.md if present

Inspect:
- tg_msg_manager/services/channel_export/
- tg_msg_manager/services/private_archive/media_downloader.py
- tg_msg_manager/services/private_archive/media_policy.py
- tg_msg_manager/core/telegram/interface.py
- tests/test_channel_export_*.py

Implement Stage 3B — Media Download Hardening for `export-channel`.

Goal:
Enable safe full media download for direct channel export while preserving metadata mode as default.

Strict rules:
- Do not change existing behavior of export, db-export, export-pm, update, retry, report, clean, delete, schedule, setup.
- Do not change SQLite schema.
- Do not add analytics, scoring, OCR, video analysis, NLP, embeddings, semantic search, political analysis, government-affiliation detection, or dashboard logic.
- Do not implement channel discussion export.
- Do not implement group source extraction.
- Do not put media download logic into ExportService, DBExportService, PrivateArchiveService, or ContextEngine.
- Keep channel media logic under tg_msg_manager/services/channel_export/.
- Reuse private_archive media download patterns where useful, but do not directly couple channel export to private archive domain classes if semantics differ.
- Default media mode must remain metadata.
- Full media download must require explicit --media full.
- Media failures must not corrupt state.
- Media failures must be recorded in media_manifest.jsonl and summary/report.
- Existing metadata mode must keep working.

Implementation requirements:
1. Add or complete ChannelMediaDownloader under services/channel_export/.
2. Implement --media full.
3. Preserve --media metadata default.
4. Add --max-media-size.
5. Add --media-types allowlist.
6. Skip existing files.
7. Compute sha256 for downloaded files.
8. Record download statuses: metadata_only, downloaded, already_exists, skipped_by_size, skipped_by_type, failed.
9. Update media_manifest.jsonl with final statuses.
10. Add media download progress events.
11. Add CLI progress display for media download.
12. Keep export state consistent.
13. Add tests.
14. Update docs, smoke checklist, changelog.
15. Create Stage 3B report.

Before editing:
1. Verify whether Stage 3A.1 report exists.
2. If Stage 3A.1 report is missing but code exists, create a short Stage 3A.1 acceptance note first.
3. Inspect current media metadata fields.
4. Inspect Telegram client download_media interface.
5. Summarize plan in 10–15 lines.
6. Then implement.

Final verification:
- python3 -m compileall tg_msg_manager
- ruff check tg_msg_manager tests
- ruff format --check tg_msg_manager tests
- pytest tests/test_channel_export_*.py
- make test
- make verify
- python3 -m tg_msg_manager.cli export-channel --help

Return:
- files changed
- tests run
- results
- known limitations
- whether Stage 3B is complete
```

---

# 2. STAGE DEFINITION

## 2.1. Stage name

`Stage 3B — Media Download Hardening`

## 2.2. Goal

Make `export-channel --media full` usable and safe.

Stage 3A exported channel posts and media metadata.

Stage 3A.1 added operational hardening: state, incremental update, append mode, progress.

Stage 3B must add controlled full media download.

## 2.3. Expected user-facing behavior

Metadata mode remains default:

```bash
python3 -m tg_msg_manager.cli export-channel --channel @example --limit 100
```

Explicit full media mode:

```bash
python3 -m tg_msg_manager.cli export-channel --channel @example --limit 100 --media full
```

Controlled full media mode:

```bash
python3 -m tg_msg_manager.cli export-channel --channel @example --limit 100 --media full --media-types photo,video --max-media-size 50MB
```

---

# 3. NON-NEGOTIABLE CONSTRAINTS

## 3.1. No analytics

Do not implement:
- OCR
- image recognition
- face detection
- video analysis
- speech-to-text
- sentiment
- narrative analysis
- propaganda detection
- political scoring
- government-affiliation detection

Stage 3B only downloads and indexes media files.

## 3.2. No Stage 3C work

Do not implement:
- discussion group export
- comments export
- post-to-discussion mapping
- reply chains under channel posts

## 3.3. No SQLite changes

Do not add media tables.

Do not persist channel media in SQLite.

Filesystem dataset remains the source of truth:
- manifest.json
- messages.jsonl
- messages.txt
- media_manifest.jsonl
- channel_export_state.json
- media/

## 3.4. No hot-path growth

Do not place channel media logic into:
- services/export/
- services/db_export/
- services/private_archive/
- services/context/

Only inspect private-archive patterns. Do not merge domains.

## 3.5. No default full download

Default must remain:

`--media metadata`

`--media full` must be explicit.

---

# 4. TARGET OUTPUT LAYOUT

For one channel:

```text
exports/channels/@channel__123456789/
  manifest.json
  channel_export_state.json
  messages.jsonl
  messages.txt
  media_manifest.jsonl
  export.log
  media/
    photos/
      0000012345_01.jpg
    videos/
      0000012400_01.mp4
    documents/
      0000012500_01.pdf
    audio/
    voice/
    animations/
    thumbnails/
```

Do not use message text/caption in file names.

Required naming pattern:

`<zero_padded_message_id>_<media_index>.<extension>`

Example:

`0000012345_01.jpg`

---

# 5. MEDIA STATUS MODEL

## 5.1. Required statuses

Use these statuses in `media_manifest.jsonl`:
- metadata_only
- downloaded
- already_exists
- skipped_by_size
- skipped_by_type
- failed

Optional internal transient status:
- pending

Do not leave final manifest rows with `pending`.

## 5.2. Status rules

metadata mode:
- metadata_only

full mode + file downloaded:
- downloaded

full mode + target file already exists and is valid enough:
- already_exists

full mode + file_size > max_media_size:
- skipped_by_size

full mode + media_type not in allowlist:
- skipped_by_type

full mode + download exception:
- failed

## 5.3. Required media manifest fields

Each media row should include:

```json
{
  "media_id": "12345_01",
  "message_id": 12345,
  "media_index": 1,
  "media_type": "photo",
  "mime_type": "image/jpeg",
  "file_name": null,
  "file_size": 245991,
  "width": 1280,
  "height": 720,
  "duration": null,
  "local_path": "media/photos/0000012345_01.jpg",
  "sha256": "optional-after-download",
  "download_status": "downloaded",
  "error": null
}
```

---

# 6. CLI REQUIREMENTS

## 6.1. Existing option

`--media` should support:
- none
- metadata
- full

`full` must become implemented in Stage 3B.

## 6.2. New option: max media size

Add:

`--max-media-size`

Accepted examples:
- 50MB
- 500MB
- 1GB
- 10485760

Rules:
- If omitted, use a safe default or no limit.
- Prefer safe default for first implementation, e.g. 50MB or 100MB.
- Document the chosen default.

If implementing parser is too large, accept integer bytes only in MVP and document it.

## 6.3. New option: media types

Add:

`--media-types`

Examples:

```bash
--media-types photo,video
--media-types document
--media-types photo,video,document,audio,voice,animation
```

If omitted:
- download all supported media types

Supported values:
- photo
- video
- document
- audio
- voice
- animation

## 6.4. Do not add analysis flags

Do not add:
- --ocr
- --transcribe
- --analyze
- --classify
- --detect-faces

---

# 7. ARCHITECTURE TARGET

Create or complete:

`tg_msg_manager/services/channel_export/media_downloader.py`

Expected responsibilities:
- download one media object
- skip existing file
- enforce max size
- enforce media type allowlist
- compute sha256
- return updated ChannelMediaRecord
- record failure without crashing whole export unless strict mode is later added

Do not put this logic in:
- service.py
- post_mapper.py
- media_policy.py
- payload_writer.py
- cli_commands.py

`service.py` may orchestrate.

---

# 8. ATOMIC TODO LIST

## 8.1. Pre-flight analysis

- [ ] Read AGENTS.md.
- [ ] Inspect services/channel_export/.
- [ ] Inspect services/channel_export/media_policy.py.
- [ ] Inspect services/channel_export/media_manifest_writer.py.
- [ ] Inspect services/channel_export/post_mapper.py.
- [ ] Inspect services/channel_export/payload_writer.py.
- [ ] Inspect services/channel_export/service.py.
- [ ] Inspect services/channel_export/state_manager.py.
- [ ] Inspect core/telegram/interface.py.
- [ ] Inspect private archive media downloader/policy.
- [ ] Inspect current CLI parser for export-channel.
- [ ] Inspect channel export tests.
- [ ] Verify whether Stage 3A.1 docs/report exist.
- [ ] Write 10–15 line implementation plan before editing.

## 8.2. Stage 3A.1 acceptance note if missing

If `docs/refactor/STAGE_3A_1_CHANNEL_EXPORT_OPERATIONAL_HARDENING_REPORT.md` is missing:

- [ ] Create a short report or acceptance note.
- [ ] List implemented operational pieces:
  - state_manager.py
  - state_path
  - run modes
  - append writer
  - progress callback
  - incremental path
- [ ] List remaining limitations.
- [ ] Do not fake verification results.
- [ ] Only record commands that were actually run.

## 8.3. Models update

File: `tg_msg_manager/services/channel_export/models.py`

- [ ] Add `error: Optional[str] = None` to `ChannelMediaRecord` if not present.
- [ ] Add fields needed for downloader result if absent:
  - sha256
  - download_status
  - local_path
- [ ] Add `max_media_size` to `ChannelExportOptions` if needed.
- [ ] Add `media_types` allowlist to `ChannelExportOptions` if needed.
- [ ] Add downloaded/skipped/failed counts to run stats if absent.
- [ ] Keep models pure.
- [ ] No Telegram imports.
- [ ] No filesystem writes.

## 8.4. CLI parser update

File: `tg_msg_manager/cli_parser.py`

- [ ] Ensure `--media full` is allowed.
- [ ] Add `--max-media-size`.
- [ ] Add `--media-types`.
- [ ] Keep `--media metadata` default.
- [ ] Update help text.
- [ ] Add parser tests.
- [ ] Ensure invalid `--media-types` fail clearly or are validated later.
- [ ] Ensure invalid `--max-media-size` fails clearly or is validated later.

## 8.5. CLI command handler update

File: `tg_msg_manager/cli_commands.py`

- [ ] Remove explicit block that rejects `--media full`.
- [ ] Parse `--max-media-size`.
- [ ] Parse `--media-types`.
- [ ] Pass parsed values into `ChannelExportOptions`.
- [ ] Render media download summary:
  - downloaded
  - already_exists
  - skipped_by_size
  - skipped_by_type
  - failed
- [ ] Do not download media in CLI.
- [ ] Do not import Telethon in CLI.
- [ ] Do not print from service.

## 8.6. Size parser

Create if needed:

`tg_msg_manager/services/channel_export/size_parser.py`

- [ ] Parse integer bytes.
- [ ] Parse KB, MB, GB.
- [ ] Be case-insensitive.
- [ ] Reject invalid values.
- [ ] Add tests.

## 8.7. Media type allowlist parser

Create if needed:

`tg_msg_manager/services/channel_export/media_types.py`

- [ ] Parse comma-separated string.
- [ ] Strip whitespace.
- [ ] Normalize lowercase.
- [ ] Validate against supported set.
- [ ] Return None or full set when omitted.
- [ ] Add tests.

## 8.8. Media policy update

File: `tg_msg_manager/services/channel_export/media_policy.py`

- [ ] Add allowlist decision.
- [ ] Add max-size decision.
- [ ] Add `should_download(record, options)` or equivalent.
- [ ] Preserve metadata mode behavior.
- [ ] Preserve none mode behavior.
- [ ] Add status decision:
  - metadata_only
  - skipped_by_size
  - skipped_by_type
  - pending/downloadable
- [ ] Add tests.

## 8.9. Media downloader creation

Create:

`tg_msg_manager/services/channel_export/media_downloader.py`

- [ ] Define `ChannelMediaDownloader`.
- [ ] Accept Telegram client in constructor.
- [ ] Accept optional semaphore/concurrency if project style supports it.
- [ ] Implement `download(record, message_or_media, destination_path)`.
- [ ] Use existing client `download_media` interface.
- [ ] Create parent directories.
- [ ] Skip if file already exists.
- [ ] Compute sha256 if downloaded or already exists.
- [ ] Return updated `ChannelMediaRecord`.
- [ ] On recoverable failure, return record with `download_status="failed"` and `error`.
- [ ] Do not raise for one failed media unless project already has strict mode.
- [ ] Do not write media manifest here.
- [ ] Do not update state here.
- [ ] Add tests with fake client.

## 8.10. SHA256 helper

Create inside downloader or utility:

- [ ] Read file in chunks.
- [ ] Return hex digest.
- [ ] Test with known content.

## 8.11. Post mapper update

File: `tg_msg_manager/services/channel_export/post_mapper.py`

- [ ] Ensure media records preserve enough information for downloader.
- [ ] Ensure local_path is relative.
- [ ] Ensure media type/category is stable.
- [ ] Ensure file_size is captured if available.
- [ ] Do not download media here.
- [ ] Do not compute sha256 here.
- [ ] Add tests.

If current MessageData does not expose enough media object info:
- [ ] Use raw_payload defensively.
- [ ] If impossible, document limitation.
- [ ] Do not break existing metadata mode.

## 8.12. Payload writer update

File: `tg_msg_manager/services/channel_export/payload_writer.py`

- [ ] Ensure media manifest writes final statuses, not stale metadata-only status in full mode.
- [ ] If downloader runs before writing record, writer can remain simple.
- [ ] If downloader runs after record mapping, ensure updated media records are passed to writer.
- [ ] Preserve append behavior.
- [ ] Preserve progress callback.
- [ ] Add tests for final statuses.

## 8.13. Service orchestration update

File: `tg_msg_manager/services/channel_export/service.py`

- [ ] Initialize `ChannelMediaDownloader`.
- [ ] In metadata mode, do not download.
- [ ] In full mode, run media download before writing media manifest row.
- [ ] Enforce max media size.
- [ ] Enforce media type allowlist.
- [ ] Track counts:
  - downloaded
  - already_exists
  - skipped_by_size
  - skipped_by_type
  - failed
- [ ] Emit media progress events.
- [ ] Preserve state update after successful run.
- [ ] Ensure media failure does not falsely mark whole export failed unless severe.
- [ ] Ensure failed media rows are present in media_manifest.
- [ ] Keep service orchestration-only.
- [ ] Do not add analytics.

## 8.14. Event emitter update

File: `tg_msg_manager/services/channel_export/event_emitter.py`

- [ ] Add events:
  - channel_export.media_progress
  - channel_export.media_downloaded
  - channel_export.media_skipped
  - channel_export.media_failed
- [ ] Keep payloads plain dicts.
- [ ] Include message_id, media_id, status, local_path, counts if available.
- [ ] Add tests if event emitter has tests.

## 8.15. CLI progress rendering update

Files:
- `tg_msg_manager/cli_commands.py`
- `tg_msg_manager/cli.py`

- [ ] Render media download progress.
- [ ] Render skipped by size/type.
- [ ] Render failed media count.
- [ ] Final summary must include media counts.
- [ ] Avoid noisy per-file output unless verbose mode exists.
- [ ] Prefer periodic summaries.

Example:

```text
Posts processed: 1200 | Media: downloaded=93 skipped=12 failed=2
```

## 8.16. Manifest update

File: `tg_msg_manager/services/channel_export/manifest_writer.py`

- [ ] Add media download summary to manifest:
  - media_mode
  - media_types
  - max_media_size
  - downloaded_media_count
  - already_existing_media_count
  - skipped_by_size_count
  - skipped_by_type_count
  - failed_media_count
- [ ] Preserve existing fields.
- [ ] Add tests.

## 8.17. Tests

Add/update tests:

- [ ] tests/test_channel_export_media_downloader.py
- [ ] tests/test_channel_export_media_policy.py
- [ ] tests/test_channel_export_payload_writer.py
- [ ] tests/test_channel_export_service.py
- [ ] tests/test_channel_export_cli.py
- [ ] tests/test_channel_export_manifest.py

Required cases:

- [ ] metadata mode does not download.
- [ ] full mode downloads.
- [ ] existing file is skipped/marked already_exists.
- [ ] sha256 is computed.
- [ ] max size skips oversized media.
- [ ] media type allowlist skips disallowed media.
- [ ] download failure records failed status.
- [ ] failed one media does not fail whole export.
- [ ] media_manifest contains final statuses.
- [ ] manifest contains media summary.
- [ ] CLI accepts `--media full`.
- [ ] CLI accepts `--max-media-size`.
- [ ] CLI accepts `--media-types`.
- [ ] invalid media type is rejected.
- [ ] invalid max size is rejected.
- [ ] incremental export with full media does not redownload existing files.
- [ ] force full export handles existing files safely.

## 8.18. Documentation

Update:

- [ ] README.md
- [ ] COMMANDS.md
- [ ] docs/testing/LIVE_SMOKE_CHECKLIST.md
- [ ] CHANGELOG.md
- [ ] PROJECT_ARCHITECTURE_OVERVIEW.md

README:
- [ ] Remove statement that `--media full` is not implemented.
- [ ] Document metadata default.
- [ ] Document full mode.
- [ ] Document max media size.
- [ ] Document media types.
- [ ] Document failure behavior.

COMMANDS.md:
- [ ] Add examples for full media.
- [ ] Add examples for type filtering.
- [ ] Add examples for max size.

LIVE_SMOKE_CHECKLIST:
- [ ] Add metadata smoke.
- [ ] Add full media smoke marked non-routine.
- [ ] Add max-size smoke.
- [ ] Add already-existing file/resume smoke if practical.

CHANGELOG:
- [ ] Add Stage 3B entry.
- [ ] Do not claim OCR/analytics.

PROJECT_ARCHITECTURE_OVERVIEW:
- [ ] Add note that channel export now supports controlled full media download.
- [ ] Keep dataset projection boundary.

## 8.19. Stage report

Create:

`docs/refactor/STAGE_3B_MEDIA_DOWNLOAD_HARDENING_REPORT.md`

Required sections:

```markdown
# Stage 3B — Media Download Hardening Report

## 1. Summary
## 2. Baseline
## 3. Implemented media modes
## 4. CLI changes
## 5. Media status model
## 6. Download safety
## 7. Progress/events
## 8. Tests added/updated
## 9. Verification results
## 10. Remaining limitations
## 11. Deferred to Stage 3C
## 12. Ready for Stage 3C?
```

---

# 9. STOP CONDITIONS

Stop if:

- Telegram client interface cannot provide downloadable media object.
- Implementing full media requires breaking MessageData or existing export flows.
- State would be advanced despite failed file writes.
- Media full implementation requires SQLite schema changes.
- Media download logic starts leaking into private_archive or DB export services.
- Tests show duplicated media rows on incremental run.
- CLI behavior for existing commands changes.

Report the blocker instead of hacking around it.

---

# 10. VERIFICATION COMMANDS

Run:

```bash
pytest tests/test_channel_export_*.py
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
ruff format --check tg_msg_manager tests
make test
make verify
python3 -m tg_msg_manager.cli export-channel --help
```

Optional live smoke:

```bash
python3 -m tg_msg_manager.cli export-channel --channel "$TEST_CHANNEL" --limit 1 --media metadata
python3 -m tg_msg_manager.cli export-channel --channel "$TEST_CHANNEL" --limit 1 --media full --max-media-size 50MB
```

---

# 11. FINAL DEFINITION OF DONE

Stage 3B is complete only if:

- [ ] `--media metadata` remains default.
- [ ] `--media full` is implemented.
- [ ] `--max-media-size` exists.
- [ ] `--media-types` exists.
- [ ] full media downloads files into `media/`.
- [ ] existing files are skipped or marked `already_exists`.
- [ ] sha256 is computed.
- [ ] oversized files are skipped.
- [ ] disallowed media types are skipped.
- [ ] failures are recorded in media_manifest.
- [ ] one failed media does not fail whole export unless severe.
- [ ] media progress events are emitted.
- [ ] CLI shows media summary.
- [ ] manifest includes media download summary.
- [ ] incremental run does not redownload existing media unnecessarily.
- [ ] no SQLite schema changes.
- [ ] no analytics added.
- [ ] no Stage 3C features added.
- [ ] tests pass.
- [ ] make verify passes.
- [ ] docs updated.
- [ ] live smoke checklist updated.
- [ ] changelog updated.
- [ ] Stage 3B report created.

---

# 12. NEXT STAGE

Only after Stage 3B is complete:

```text
Stage 3C — Channel Discussion Context Export
```

Do not implement Stage 3C here.
