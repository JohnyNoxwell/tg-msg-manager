# Dataset Contract V1

## 1. Scope

Dataset Contract V1 documents the existing filesystem contract for direct channel export datasets produced by:

```bash
python3 -m tg_msg_manager.cli export-channel --channel <channel>
```

This document describes current behavior only. It does not authorize runtime changes, schema changes, new validators, dataset repair, post-processing implementation, analytics, OSINT, profiling, OCR, STT, or LLM-dependent behavior.

Primary dataset type:

```text
direct_channel_export
```

Current manifest schema version:

```text
1.0
```

Primary pipeline boundary:

```text
export -> validate/inspect -> dataset doctor -> post-processing -> optional LLM report
```

Post-processing reads completed datasets. It must not be embedded inside exporter core, channel export workflows, validation, or storage write paths.

## 2. Status Labels

Use these deterministic labels when documenting expected files or validation outcomes:

- `REQUIRED`: must exist for a valid current dataset in the described mode.
- `OPTIONAL`: may exist without making the dataset invalid.
- `CONDITIONAL`: expected only when a specific mode or option is active.
- `NOT_EXPECTED`: current behavior should not create it for the described mode.
- `LEGACY_COMPAT`: accepted for older datasets, but not required for current output.
- `UNKNOWN_NEEDS_CHECK`: not covered by current docs/tests and must not be assumed.

These labels are documentation labels. They are not a new runtime enum.

## 3. Dataset Root

Default channel datasets are written under:

```text
exports/channels/<channel_slug>/
```

The slug is built from channel username, title, or id, plus the numeric channel id. The dataset is filesystem-first. Channel posts and discussion comments are not persisted to SQLite.

## 4. Artifact Contract

### `manifest.json`

- Status: `REQUIRED`.
- Produced by: `export-channel`.
- Write model: overwrite through atomic temp-and-replace.
- Expected on: full, force, incremental, and no-new-posts runs.
- Contains: `dataset_type`, `schema_version`, `exported_at`, `source`, `export`, `discussion`, `status`.
- Notes: `export.included_files` records files included for the completed run shape.

### `messages.jsonl`

- Status: `CONDITIONAL`.
- Expected when `include_jsonl` is true. Current CLI path uses the default true value.
- Produced by: `export-channel`.
- Write model: overwrite for full/force; copy-append-replace for incremental.
- No-new-posts: not appended.
- Top-level record keys:

```text
message_id
channel_id
channel_title
channel_username
timestamp
text
views
forwards
replies_count
reactions
media
raw_payload
```

### `messages.txt`

- Status: `CONDITIONAL`.
- Expected when `include_txt` is true. Current CLI path uses the default true value.
- Produced by: `export-channel`.
- Write model: overwrite for full/force; copy-append-replace for incremental.
- No-new-posts: not appended.
- Notes: TXT is a projection for reading. JSONL/state/manifest remain the structured contract.

### `media_manifest.jsonl`

- Status: `REQUIRED`.
- Produced by: `export-channel`.
- Write model: overwrite for full/force; copy-append-replace for incremental.
- No-new-posts: not appended.
- Record keys include the nested message media keys plus:

```text
error
original_filename
detected_extension
filename_strategy
final_filename
final_path
```

Committed media statuses:

```text
metadata_only
downloaded
already_exists
skipped_by_size
skipped_by_type
failed
```

Committed rows must not use `pending`.

### `media/`

- Status: `CONDITIONAL`.
- Expected when `--media full` is used and included in `manifest.json`.
- Produced by: `export-channel --media full`.
- Write model: media files are written as individual files, not through a multi-file transaction.
- Current subdirectories:

```text
photos
videos
documents
audio
voice
animations
thumbnails
```

Downloaded and already-existing media rows must point inside the dataset root. Skipped or failed rows do not require a local media file.

### `channel_export_state.json`

- Status: `REQUIRED`.
- Produced by: `export-channel`.
- Write model: overwrite through atomic temp-and-replace after payload and manifest success.
- No-new-posts: not advanced.
- Keys:

```text
schema_version
channel_id
channel_username
channel_title
last_exported_message_id
last_exported_at
message_count_total
media_count_total
downloaded_media_count_total
already_existing_media_count_total
skipped_media_count_total
skipped_by_size_count_total
skipped_by_type_count_total
failed_media_count_total
last_run_status
updated_at
date_from
date_to
last_manifest_path
```

### `run_changelog.jsonl`

- Status: `REQUIRED`.
- Produced by: `export-channel`.
- Write model: append-only audit artifact per dataset path.
- Full/force/incremental/no-new-posts: one row is appended for each completed run.
- Force behavior: payload files are overwritten, but changelog history is preserved.
- Keys:

```text
run_id
export_target_type
export_target_id
export_target_name
run_mode
started_at
finished_at
previous_cursor
new_cursor
new_message_count
new_message_ids
first_new_message_id
last_new_message_id
first_new_message_date
last_new_message_date
artifact_paths
warnings
```

### `discussion_metadata.jsonl`

- Status: `CONDITIONAL`.
- Expected only with `--discussion metadata`.
- Produced by: `export-channel --discussion metadata`.
- Write model: overwrite for full/force; copy-append-replace for incremental when current-run posts exist.
- No-new-posts: not written or appended.
- Notes: metadata mode does not resolve linked discussion entities and does not fetch comments.
- Keys:

```text
channel_id
channel_message_id
has_comments
discussion_chat_id
replies_count
comments_exported
source
```

### `discussion_comments.jsonl`

- Status: `CONDITIONAL`.
- Expected only with `--discussion full`.
- Produced by: `export-channel --discussion full`.
- Write model: overwrite for full/force; copy-append-replace for incremental.
- No-new-posts: not appended.
- Notes: discussion comment media is metadata-only; full media download for discussion comments is not implemented.
- Keys:

```text
message_id
discussion_chat_id
channel_id
channel_message_id
discussion_root_message_id
author_id
author_name
username
timestamp
text
reply_to_id
media
reactions
raw_payload
```

### `discussion_comments.txt`

- Status: `CONDITIONAL`.
- Expected only with `--discussion full`.
- Produced by: `export-channel --discussion full`.
- Write model: overwrite for full/force; copy-append-replace for incremental.
- Notes: TXT projection for discussion comments.

### `discussion_threads.jsonl`

- Status: `CONDITIONAL`.
- Expected only with `--discussion full`.
- Produced by: `export-channel --discussion full`.
- Write model: overwrite for full/force; copy-append-replace for incremental.
- Keys:

```text
channel_id
channel_username
channel_message_id
discussion_chat_id
discussion_root_message_id
comments_count
exported_comments_count
status
error
```

Allowed thread statuses:

```text
not_available
not_linked
no_comments
exported
partial
failed
```

### `discussion_export_state.json`

- Status: `CONDITIONAL`.
- Expected only with `--discussion full`.
- Produced by: `export-channel --discussion full`.
- Write model: overwrite through atomic temp-and-replace after discussion payload, manifest, and channel state success.
- No-new-posts: not mutated.
- Keys:

```text
schema_version
channel_id
discussion_chat_id
last_run_at
thread_count_total
comment_count_total
failed_thread_count_total
last_run_status
updated_at
```

## 5. Mode Matrix

### Media modes

- `--media none`: `media_manifest.jsonl` remains part of the dataset contract; media records are not downloaded. `media/` is `NOT_EXPECTED` in manifest included files.
- `--media metadata`: default CLI mode. Media metadata is recorded without downloading files. `media/` is `NOT_EXPECTED` in manifest included files.
- `--media full`: media download is attempted with size/type guardrails. `media/` is `CONDITIONAL` and included in manifest. Final statuses record downloaded, existing, skipped, or failed outcomes.

### Discussion modes

- `--discussion none`: default CLI mode. Discussion resolver does not run; discussion files are `NOT_EXPECTED`.
- `--discussion metadata`: writes `discussion_metadata.jsonl`; comment/thread/state files are `NOT_EXPECTED`.
- `--discussion full`: writes comments, comments TXT, threads, and discussion state. It exports comments only for channel posts fetched in the current run.

### Run modes

- Full: creates a dataset checkpoint from posts fetched in that run.
- Force full: ignores existing channel state and overwrites channel payload files; with `--discussion full`, discussion files/state are also rebuilt from posts fetched in that force run.
- Incremental: reads `channel_export_state.json`, fetches posts newer than `last_exported_message_id`, and appends payload rows through copy-append-replace.
- No-new-posts: refreshes manifest/changelog facts, does not advance channel state, does not resolve/fetch discussion data, and does not mutate discussion files/state.

### `include_jsonl` / `include_txt`

- Current CLI path uses both defaults as true.
- If a non-CLI caller disables one format, the matching payload file is `NOT_EXPECTED` for that run and omitted from `manifest.json` included files.
- This is an existing service option, not a public CLI contract.

## 6. Partial Failure Contract

- Payload write failure must not advance channel state.
- Discussion payload failure must not advance discussion state.
- Manifest write failure must not advance channel or discussion state.
- Failed per-thread discussion records may be committed as dataset facts; when committed, discussion state reflects committed files and failure counters.
- Failed media rows may be committed with `download_status: "failed"` and an error field.
- The write model is not a full ACID transaction across all dataset files.
- Downloaded media files already written under `media/` are not rolled back as part of a multi-file transaction.

## 7. Validation Boundary

`validate-dataset` checks deterministic structure and consistency for local datasets. It may report `ok`, `warnings`, or `errors`.

It checks current concerns such as:

- required base files;
- parseable JSON/JSONL;
- duplicate post ids and message id gaps;
- reply references where exported fields are available;
- manifest/state counter sanity;
- included files where feasible;
- media ids, statuses, local paths, and message linkage;
- optional discussion comments, threads, and discussion state.

`inspect-dataset` summarizes detected files, message counts, media status counts, discussion presence/counts, manifest facts, state cursor, and validation note counts.

`inspect-dataset --doctor` is a read-only diagnostic layer over validation findings. It adds severity, artifact path, message, and suggested next action, but must not repair or rewrite dataset files.

Neither command performs:

- Telegram network access;
- dataset repair or migration;
- exporter rewrite;
- SQLite schema changes;
- analytics, OSINT, profiling, sentiment, OCR, STT, media optimization, or LLM analysis.

## 8. Other Dataset Families

Group/user `export`, `db-export`, and `export-pm` produce existing local artifacts, but Dataset Contract V1 is anchored on direct channel export because that is the current filesystem dataset with documented manifest/state/validation behavior.

Status for non-channel dataset families in this contract:

- group/user `export`: `UNKNOWN_NEEDS_CHECK` for Dataset Contract V1.
- `db-export`: `UNKNOWN_NEEDS_CHECK` for Dataset Contract V1.
- `export-pm`: `UNKNOWN_NEEDS_CHECK` for Dataset Contract V1.

Future stages may define separate contracts for those families only from existing behavior and tests.
