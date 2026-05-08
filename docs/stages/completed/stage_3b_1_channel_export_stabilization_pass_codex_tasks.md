# STAGE 3B.1 — CHANNEL EXPORT STABILIZATION PASS BEFORE STAGE 3C

Status: completed
Stage: 3B.1
Scope: historical task instructions

## 0. PURPOSE

This file is a Codex task specification for a short stabilization pass after Stage 3B Media Download Hardening and before Stage 3C Channel Discussion Context Export.

Goal:

```text
Stabilize the completed Stage 3B implementation before starting Stage 3C.
```

This is not a feature stage.

This pass must reduce risk, protect architectural boundaries, and ensure `export-channel` remains maintainable before discussion/comment export is added.

---

## 1. CURRENT CONTEXT

The repository already has:

```text
Stage 3A   — Direct Channel Export / Dataset Projection
Stage 3A.1 — Channel Export Operational Hardening
Stage 3B   — Media Download Hardening
```

Stage 3B introduced:

```text
--media full
--max-media-size
--media-types
services/channel_export/media_downloader.py
sha256 for downloaded/reused files
media_manifest.jsonl final statuses
media progress events
media summary counters
Stage 3B report/docs/tests
```

Known acceptable limitations after Stage 3B:

```text
1. Switching an existing metadata-only dataset to --media full without --force downloads only newly fetched posts.
2. Append-only incremental export still does not rollback already appended payload files if a run fails mid-run.
3. Stage 3C discussion export is not implemented yet.
```

This stabilization pass must not attempt to solve all future problems. It should only harden boundaries and reduce complexity before Stage 3C.

---

## 2. ABSOLUTE SCOPE

Allowed scope:

```text
- refactor-only improvements inside services/channel_export/
- test additions or test tightening
- documentation corrections
- architecture guardrails
- small naming/contract cleanup if behavior stays stable
- CLI help/docs consistency checks
- boundary checks to prevent Stage 3C leakage into Stage 3B code
```

Forbidden scope:

```text
- no Stage 3C implementation
- no discussion group export
- no comments export
- no reply-chain export
- no linked discussion group detection
- no post-to-discussion mapping
- no SQLite schema changes
- no analytics
- no OCR
- no image/video/audio analysis
- no speech-to-text
- no political/narrative classification
- no dashboard
- no GUI
- no SaaS/monitoring features
- no source discovery
- no Threads adapter
- no changes to export/db-export/export-pm behavior
- no changes to private archive media behavior unless tests prove a shared helper must be fixed
```

---

## 3. ARCHITECTURAL RULES

### 3.1. Hot-path files are protected

Do not add new feature logic to:

```text
tg_msg_manager/services/export/service.py
tg_msg_manager/services/db_export/service.py
tg_msg_manager/services/private_archive/service.py
tg_msg_manager/services/context/engine.py
```

These files are out of scope unless a test import breaks and the fix is purely mechanical.

### 3.2. CLI must remain thin

CLI may only:

```text
- parse arguments
- validate/normalize simple CLI values
- build ChannelExportOptions
- call ChannelExportService
- print result summary
```

CLI must not:

```text
- call Telegram API directly
- download media
- compute sha256
- decide media statuses
- render JSONL/TXT/media_manifest payloads
- manage channel_export_state.json
- perform Stage 3C logic
```

### 3.3. ChannelExportService must remain orchestration-only

`ChannelExportService` may orchestrate:

```text
resolve source
build plan
load state
fetch posts
map posts
prepare media records
write payload
write manifest
save state
emit service events
return result
```

`ChannelExportService` must not become the owner of:

```text
media policy details
download path rules
sha256 calculation
media status classification
media summary aggregation rules
discussion export
comment mapping
rendering details
```

If existing service logic has grown too much, extract it into small components under:

```text
tg_msg_manager/services/channel_export/
```

Allowed examples:

```text
media_processor.py
media_result_counter.py
record_preparer.py
```

Only create these if they reduce complexity. Do not split files for cosmetic reasons.

### 3.4. Dataset-first boundary

The project remains:

```text
Local Telegram dataset export pipeline
```

It is not:

```text
OSINT analytics platform
SaaS monitoring system
content analysis engine
```

Do not add interpretation logic.

---

## 4. MAIN RISKS TO CHECK

Before making changes, inspect these specific risks:

```text
1. ChannelExportService grew during Stage 3B.
2. Media status counting may be duplicated across writer/state/manifest/result.
3. media_manifest.jsonl and messages.jsonl may diverge in media fields.
4. Incremental/full/force behavior may have hidden edge cases with --media full.
5. CLI docs/help may not match implementation.
6. Stage 3C may be tempting to start prematurely.
```

---

## 5. PRE-EDIT INSPECTION CHECKLIST

Before editing any code, inspect:

```text
AGENTS.md
README.md
COMMANDS.md
CHANGELOG.md
docs/testing/LIVE_SMOKE_CHECKLIST.md
docs/refactor/STAGE_3B_MEDIA_DOWNLOAD_HARDENING_REPORT.md

tg_msg_manager/cli_parser.py
tg_msg_manager/cli_commands.py
tg_msg_manager/cli_io.py

tg_msg_manager/services/channel_export/__init__.py
tg_msg_manager/services/channel_export/service.py
tg_msg_manager/services/channel_export/models.py
tg_msg_manager/services/channel_export/media_downloader.py
tg_msg_manager/services/channel_export/media_policy.py
tg_msg_manager/services/channel_export/media_types.py
tg_msg_manager/services/channel_export/size_parser.py
tg_msg_manager/services/channel_export/payload_writer.py
tg_msg_manager/services/channel_export/media_manifest_writer.py
tg_msg_manager/services/channel_export/manifest_writer.py
tg_msg_manager/services/channel_export/post_mapper.py
tg_msg_manager/services/channel_export/state_manager.py
tg_msg_manager/services/channel_export/event_emitter.py
```

Then inspect tests:

```text
tests/test_channel_export_*.py
```

After inspection, write a short plan in 8–12 lines before editing.

The plan must state:

```text
- whether service extraction is needed
- which files will be edited
- which tests will be added or adjusted
- what behavior must remain unchanged
```

---

# 6. TASK BLOCK A — BASELINE VERIFICATION

## A.1. Verify current Stage 3B surface

- [ ] Run or inspect current `export-channel --help`.
- [ ] Confirm `--media` supports:
  - [ ] `none`
  - [ ] `metadata`
  - [ ] `full`
- [ ] Confirm default media mode is still:
  - [ ] `metadata`
- [ ] Confirm `--max-media-size` exists.
- [ ] Confirm `--media-types` exists.
- [ ] Confirm `--media full` is not blocked by CLI.
- [ ] Confirm old error text is removed:
  - [ ] `--media full is not implemented yet`

## A.2. Verify Stage 3B files exist

- [ ] Confirm file exists:
  - [ ] `tg_msg_manager/services/channel_export/media_downloader.py`
- [ ] Confirm file exists:
  - [ ] `tg_msg_manager/services/channel_export/media_types.py`
- [ ] Confirm file exists:
  - [ ] `tg_msg_manager/services/channel_export/size_parser.py`
- [ ] Confirm report exists:
  - [ ] `docs/refactor/STAGE_3B_MEDIA_DOWNLOAD_HARDENING_REPORT.md`

## A.3. Verify no Stage 3C files were added accidentally

Search for Stage 3C leakage.

- [ ] Search codebase for:
  - [ ] `discussion`
  - [ ] `comments`
  - [ ] `linked_chat`
  - [ ] `linked discussion`
  - [ ] `discussion_group`
  - [ ] `threads.jsonl`
  - [ ] `comments.jsonl`
- [ ] If these appear only in docs/future roadmap, leave them.
- [ ] If executable Stage 3C logic exists, stop and report it.
- [ ] Do not implement or repair Stage 3C in this pass.

---

# 7. TASK BLOCK B — SERVICE COMPLEXITY REVIEW

## B.1. Measure ChannelExportService responsibility

Inspect:

```text
tg_msg_manager/services/channel_export/service.py
```

Identify whether it directly owns too many details in these areas:

- [ ] media download status classification
- [ ] media progress aggregation
- [ ] media event payload construction
- [ ] media record preparation
- [ ] options normalization
- [ ] manifest summary wiring
- [ ] result summary wiring

## B.2. Decide whether extraction is necessary

Extraction is allowed only if it clearly improves maintainability.

Extraction is recommended if:

```text
ChannelExportService contains low-level media details that can be moved without changing public behavior.
```

Extraction is not recommended if:

```text
The change would only rename methods or scatter logic across more files without reducing responsibility.
```

## B.3. Optional extraction target: media processing

If extraction is justified, create:

```text
tg_msg_manager/services/channel_export/media_processor.py
```

It may own:

```text
- preparing full-mode media records
- calling ChannelMediaDownloader
- emitting media events through a supplied emitter
- tracking media progress totals
```

It must not own:

```text
- fetching posts
- writing JSONL/TXT
- writing channel_export_state.json
- writing manifest.json
- deciding run mode
- Stage 3C discussion logic
```

Atomic steps:

- [ ] Create `media_processor.py`.
- [ ] Add a small class, for example:
  - [ ] `ChannelMediaProcessor`
- [ ] Move full-mode media preparation logic out of `ChannelExportService._prepare_record`.
- [ ] Keep `ChannelExportService` calling one high-level method, for example:
  - [ ] `prepare_record(...)`
- [ ] Keep constructor dependency injection possible.
- [ ] Keep tests using fake clients/downloader possible.
- [ ] Do not change output schema.
- [ ] Do not change CLI behavior.
- [ ] Do not change media statuses.

## B.4. Optional extraction target: media counters

If media status counting is duplicated or fragile, create a small helper:

```text
tg_msg_manager/services/channel_export/media_counters.py
```

It may own:

```text
- counting downloaded
- counting already_exists
- counting skipped_by_size
- counting skipped_by_type
- counting failed
- calculating skipped_media_count
```

Atomic steps:

- [ ] Create constants or helper functions for status names if useful.
- [ ] Replace duplicated string checks only where safe.
- [ ] Keep `ChannelExportRunStats` fields unchanged.
- [ ] Keep manifest fields unchanged.
- [ ] Keep state fields unchanged.
- [ ] Add tests if counting behavior changes location.

Do not over-engineer this. If current duplication is acceptable, skip.

---

# 8. TASK BLOCK C — MEDIA STATUS CONTRACT HARDENING

## C.1. Define accepted final statuses

Ensure final media statuses are exactly:

```text
metadata_only
downloaded
already_exists
skipped_by_size
skipped_by_type
failed
```

Existing internal/transient statuses may include:

```text
pending
skipped_by_mode
```

But final `media_manifest.jsonl` for `--media full` must not contain `pending`.

Atomic checks:

- [ ] Confirm metadata mode writes `metadata_only`.
- [ ] Confirm full mode writes one of:
  - [ ] `downloaded`
  - [ ] `already_exists`
  - [ ] `skipped_by_size`
  - [ ] `skipped_by_type`
  - [ ] `failed`
- [ ] Confirm full mode does not write `pending`.
- [ ] Confirm failed rows include `error`.
- [ ] Confirm downloaded rows include `sha256`.
- [ ] Confirm already_exists rows include `sha256`.
- [ ] Confirm skipped rows do not require `sha256`.

## C.2. Add or tighten tests for final statuses

Add tests if missing.

Required tests:

- [ ] `--media metadata` produces `metadata_only`.
- [ ] `--media full` successful download produces `downloaded`.
- [ ] `--media full` existing file produces `already_exists`.
- [ ] `--media full` oversized file produces `skipped_by_size`.
- [ ] `--media full` disallowed type produces `skipped_by_type`.
- [ ] `--media full` failed download produces `failed`.
- [ ] `--media full` never writes `pending` to `media_manifest.jsonl`.

---

# 9. TASK BLOCK D — STATE SAFETY REVIEW

## D.1. Verify state write ordering

Inspect current order in `ChannelExportService`.

Expected safe order:

```text
1. fetch/map/prepare records
2. write payload files
3. finish write session
4. build completed state
5. write manifest
6. save state
7. return result
```

Atomic checks:

- [ ] Confirm state is not saved before payload write completion.
- [ ] Confirm state is not saved before manifest write completion.
- [ ] Confirm failed media item does not throw by default.
- [ ] Confirm critical manifest write failure does not advance state.
- [ ] Confirm critical payload write failure does not advance state.
- [ ] Confirm state validation still rejects mismatched channel state.

## D.2. Add or tighten tests

Required tests if not already present:

- [ ] Manifest write failure leaves previous state unchanged.
- [ ] Payload write failure leaves previous state unchanged.
- [ ] Media item failure does not fail whole export.
- [ ] Downloader critical bug may fail export, but state must not advance.
- [ ] Incremental no-new-posts keeps state unchanged.

Do not implement a rollback/staging system in this pass.

Only document the limitation if needed.

---

# 10. TASK BLOCK E — INCREMENTAL + FULL MEDIA EDGE CASES

## E.1. Metadata-to-full behavior

The current acceptable behavior:

```text
If a dataset was created with --media metadata, then later run with --media full without --force, only newly fetched posts are processed for full media download.
```

Atomic tasks:

- [ ] Confirm this behavior is documented.
- [ ] Confirm this behavior is tested or explicitly left as limitation.
- [ ] Do not implement historical media backfill in this pass.
- [ ] Do not create a new `backfill-media` command.
- [ ] Do not change incremental semantics.

## E.2. Force behavior with full media

Atomic tasks:

- [ ] Confirm `--force --media full` performs full re-export.
- [ ] Confirm existing media files become `already_exists` where paths already exist.
- [ ] Confirm payload files are overwritten on force.
- [ ] Confirm duplicate payload rows are not created by force.
- [ ] Confirm state totals are rebuilt, not appended, during force.

## E.3. Incremental behavior with full media

Atomic tasks:

- [ ] Confirm incremental full media export processes only posts newer than `last_exported_message_id`.
- [ ] Confirm media records for new posts are appended.
- [ ] Confirm old media records are not duplicated.
- [ ] Confirm state totals increase only by current run stats.
- [ ] Confirm manifest totals reflect cumulative state.

---

# 11. TASK BLOCK F — CLI CONTRACT HARDENING

## F.1. Validate argument parsing

Atomic tasks:

- [ ] Confirm `--max-media-size 50MB` parses.
- [ ] Confirm `--max-media-size 1GB` parses.
- [ ] Confirm `--max-media-size 1024` parses as bytes.
- [ ] Confirm invalid size fails cleanly:
  - [ ] `0`
  - [ ] `-1`
  - [ ] `abc`
  - [ ] `10XB`
- [ ] Confirm `--media-types photo` parses.
- [ ] Confirm `--media-types photo,video` parses.
- [ ] Confirm duplicate media types are deduplicated or handled deterministically.
- [ ] Confirm invalid media type fails cleanly.

## F.2. Validate CLI output

Atomic tasks:

- [ ] Confirm summary prints:
  - [ ] posts exported this run
  - [ ] total known posts
  - [ ] media records added this run
  - [ ] total known media records
  - [ ] downloaded media this run
  - [ ] already existing media this run
  - [ ] skipped by size this run
  - [ ] skipped by type this run
  - [ ] failed media this run
  - [ ] manifest path
  - [ ] media manifest path
  - [ ] state path
- [ ] Confirm metadata mode does not print misleading “downloaded” claims.
- [ ] Confirm failed media count does not make the command exit non-zero by itself.

---

# 12. TASK BLOCK G — MANIFEST AND JSONL CONTRACT REVIEW

## G.1. Manifest contract

Inspect:

```text
tg_msg_manager/services/channel_export/manifest_writer.py
```

Atomic tasks:

- [ ] Confirm manifest includes media mode.
- [ ] Confirm manifest includes max media size.
- [ ] Confirm manifest includes media types.
- [ ] Confirm manifest includes media totals:
  - [ ] media_count
  - [ ] downloaded_media_count
  - [ ] already_existing_media_count
  - [ ] skipped_media_count
  - [ ] skipped_by_size_count
  - [ ] skipped_by_type_count
  - [ ] failed_media_count
- [ ] Confirm `included_files` includes `media/` only for `--media full`.
- [ ] Confirm default metadata export does not imply full media files exist.

## G.2. media_manifest.jsonl contract

Atomic tasks:

- [ ] Confirm each media row includes:
  - [ ] media_id
  - [ ] message_id
  - [ ] media_index
  - [ ] media_type
  - [ ] mime_type
  - [ ] file_name
  - [ ] file_size
  - [ ] local_path
  - [ ] sha256
  - [ ] download_status
  - [ ] error
- [ ] Confirm `error` is null unless status is `failed`.
- [ ] Confirm `sha256` is present for `downloaded`.
- [ ] Confirm `sha256` is present for `already_exists`.

## G.3. messages.jsonl media contract

Atomic tasks:

- [ ] Confirm messages JSONL media records include enough fields for downstream AI workflows.
- [ ] Decide whether `error` should also be included in messages JSONL media records.
- [ ] If adding `error` to messages JSONL:
  - [ ] update tests
  - [ ] document the field
  - [ ] keep backward compatibility acceptable
- [ ] If not adding `error`, document that `media_manifest.jsonl` is the authoritative media audit file.

Do not break existing JSONL consumers casually.

---

# 13. TASK BLOCK H — DOCUMENTATION CONSISTENCY

## H.1. README

Atomic tasks:

- [ ] Confirm README no longer says `--media full` is not implemented.
- [ ] Confirm README documents:
  - [ ] `--media metadata` default
  - [ ] `--media full`
  - [ ] `--max-media-size`
  - [ ] `--media-types`
  - [ ] media statuses
  - [ ] known limitation about metadata-to-full incremental behavior
- [ ] Keep product positioning as dataset pipeline, not analytics platform.

## H.2. COMMANDS.md

Atomic tasks:

- [ ] Confirm `export-channel` section documents:
  - [ ] `--media`
  - [ ] `--max-media-size`
  - [ ] `--media-types`
  - [ ] `--force`
  - [ ] incremental behavior
  - [ ] full media behavior
- [ ] Confirm examples are safe and small:
  - [ ] use `--limit`
  - [ ] use `--max-media-size`
  - [ ] avoid unbounded full-media command as first example

## H.3. LIVE_SMOKE_CHECKLIST

Atomic tasks:

- [ ] Confirm smoke checklist has metadata-mode channel export.
- [ ] Confirm smoke checklist has full-media small test.
- [ ] Confirm smoke checklist has type/size guardrail test.
- [ ] Confirm expected failures are described clearly.

## H.4. CHANGELOG

Atomic tasks:

- [ ] Confirm Stage 3B entry exists.
- [ ] Confirm stabilization pass entry is added after changes.
- [ ] Do not exaggerate new features.
- [ ] Mark this pass as stabilization/refactor/tests/docs only.

## H.5. Stage report

If this pass changes code or tests, create:

```text
docs/refactor/STAGE_3B_1_CHANNEL_EXPORT_STABILIZATION_REPORT.md
```

Report must include:

```text
- summary
- files changed
- behavior preserved
- tests added/updated
- verification commands
- known limitations
- explicit statement that Stage 3C was not started
```

---

# 14. TASK BLOCK I — TEST REQUIREMENTS

## I.1. Required test groups

Ensure coverage across:

```text
tests/test_channel_export_cli.py
tests/test_channel_export_media_downloader.py
tests/test_channel_export_media_policy.py
tests/test_channel_export_manifest.py
tests/test_channel_export_payload_writer.py
tests/test_channel_export_post_mapper.py
tests/test_channel_export_service.py
tests/test_channel_export_state_manager.py
```

Do not create massive integration tests if unit/service tests cover the behavior.

## I.2. Add guard tests if missing

Required guard tests:

- [ ] `--media full` is accepted by parser.
- [ ] `--max-media-size` parser accepts valid values.
- [ ] `--max-media-size` parser rejects invalid values.
- [ ] `--media-types` parser accepts valid values.
- [ ] `--media-types` parser rejects invalid values.
- [ ] Metadata mode does not call downloader.
- [ ] Full mode calls downloader for eligible media.
- [ ] Failed media does not fail export.
- [ ] Final media manifest does not contain `pending`.
- [ ] State does not advance on manifest write failure.
- [ ] Force full media does not append duplicate payload rows.
- [ ] Stage 3C artifacts are absent from executable code.

---

# 15. TASK BLOCK J — VERIFICATION COMMANDS

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

If a command fails:

- [ ] capture exact command
- [ ] capture exact failure
- [ ] determine whether failure is caused by this pass
- [ ] fix if caused by this pass
- [ ] if unrelated baseline failure exists, document it clearly

Do not claim verification passed unless it actually passed.

---

# 16. COMPLETION CRITERIA

This pass is complete only if:

```text
1. Stage 3B behavior remains intact.
2. Default --media metadata remains unchanged.
3. --media full remains explicit.
4. No Stage 3C logic is added.
5. No SQLite schema change occurs.
6. No old export/db-export/export-pm behavior changes.
7. ChannelExportService is not made worse.
8. Media status contract is tested.
9. State write ordering is tested or preserved.
10. Docs match implementation.
11. Verification commands are run and reported.
12. A Stage 3B.1 stabilization report is created if code/tests/docs changed.
```

---

# 17. FINAL RESPONSE FORMAT FOR CODEX

Return:

```text
## Summary
- What was stabilized
- Whether any extraction was done
- Whether Stage 3C was avoided

## Files changed
- path
- path

## Behavior preserved
- default media mode
- full media explicit
- state safety
- no SQLite changes
- no legacy command changes

## Tests
- command: result
- command: result

## Known limitations
- remaining accepted limitations

## Stage status
Stage 3B.1 stabilization pass: complete / partial / blocked
Stage 3C: not started
```

---

# 18. NON-NEGOTIABLE FINAL NOTE

Do not start Stage 3C in this pass.

Stage 3C begins only after this stabilization pass is complete and reviewed.
