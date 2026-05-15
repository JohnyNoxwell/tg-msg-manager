# Dataset Validation / Inspection

## Purpose

Stage 4A adds read-only validation and inspection for channel export datasets.

The exporter writes datasets. The validator checks dataset structure and deterministic relationships. The inspector summarizes dataset facts. This stage does not interpret message or comment content.

## Commands

```bash
python3 -m tg_msg_manager.cli validate-dataset --path exports/channels/example
python3 -m tg_msg_manager.cli validate-dataset --path exports/channels/example --json
python3 -m tg_msg_manager.cli inspect-dataset --path exports/channels/example
python3 -m tg_msg_manager.cli inspect-dataset --path exports/channels/example --json
```

Both commands work from local filesystem state and do not require Telegram credentials or a Telegram client connection.

## Read-only boundary

Dataset validation and inspection are read-only:

- no Telegram network calls;
- no dataset repair or migration;
- no exporter rewrite;
- no dataset, state, or SQLite schema changes;
- no content analytics, OSINT, profiling, sentiment analysis, OCR, STT, or media optimization.

Implementation lives under `tg_msg_manager/services/dataset_validation/`. CLI changes are limited to parser and dispatch wiring.

## Validation status

Validation reports use three statuses:

- `ok` means no errors or warnings were found.
- `warnings` means the dataset is parseable but has optional drift or non-fatal issues.
- `errors` means required structure is corrupt or missing.

`validate-dataset` exits with status code `1` when validation status is `errors`. Warnings do not make the command fail.

## What is checked

Validation checks deterministic dataset structure and relationships:

- required base files: `manifest.json`, `messages.jsonl`, `messages.txt`, `media_manifest.jsonl`, `channel_export_state.json`;
- parseable JSON and JSONL;
- duplicate, invalid, or gapped channel post `message_id`;
- channel post reply references where `reply_to_id` is available directly or through `raw_payload.reply_to.reply_to_msg_id`;
- manifest and state counter sanity;
- manifest included files where feasible;
- optional `run_changelog.jsonl` file presence in inspection summaries;
- duplicate media ids and media records linked to missing channel post ids;
- media statuses in `media_manifest.jsonl`;
- downloaded or already-existing media paths exist and stay inside the dataset root;
- media records present in `messages.jsonl` but absent from `media_manifest.jsonl`;
- optional discussion JSONL files when present;
- discussion comments and threads link to known channel post ids where the current schema provides those fields;
- discussion comment reply links where the current exported comment records provide enough information;
- optional discussion state consistency when present.

## Validation codes

Additional Stage 4B.2 relationship checks use these stable codes:

- `message_id_gap_detected` warning: one or more channel message ids are absent between observed min/max ids. Telegram deletions or unavailable messages can cause this, so validation does not treat it as data loss by itself.
- `invalid_reply_to_id` error: a channel post reply id is present but is not a non-negative integer.
- `reply_parent_outside_export_scope` warning: a channel post replies to an id outside the exported message id range.
- `reply_parent_missing` warning: a channel post replies to an id inside the exported range, but that parent row is absent.
- `duplicate_media_id` error: `media_manifest.jsonl` repeats a media id.
- `invalid_media_id` error: a media record id is present but not usable.
- `invalid_media_message_id` error: a media record message id is present but not an integer.
- `media_message_unlinked` warning: a media manifest row references a channel post id missing from `messages.jsonl`.
- `media_manifest_without_message_media` warning: a media manifest row is absent from the nested `messages.jsonl` media list when message media records are available.
- `message_media_missing_manifest` warning: a nested `messages.jsonl` media record is absent from `media_manifest.jsonl`.
- `discussion_reply_parent_outside_export_scope` warning: a discussion comment replies to an id outside the exported discussion comment id range and not to the discussion root.
- `discussion_reply_parent_missing` warning: a discussion comment replies to an id inside the exported discussion comment id range, but that parent comment row is absent.

## What is not checked

Stage 4A does not:

- analyze text meaning;
- classify topics, sentiment, users, or bots;
- rebuild reply trees;
- hash media by default;
- decode images, audio, or video;
- download missing Telegram content;
- repair, rewrite, or migrate datasets.

## Known limitations

- SHA-256 verification is not performed by default.
- Count mismatches are usually warnings because older datasets may have schema drift.
- Discussion linkage checks only run where current schema fields are present.
- Gap and missing-reply warnings do not prove exporter data loss because Telegram deletions, limits, and scoped exports can remove parent records from the local dataset.
- Inspection reports summarize deterministic counts and statuses only; they are not analytics reports.
