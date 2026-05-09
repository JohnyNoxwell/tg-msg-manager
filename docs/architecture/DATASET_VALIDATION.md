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
- duplicate or missing channel post `message_id`;
- manifest and state counter sanity;
- manifest included files where feasible;
- media statuses in `media_manifest.jsonl`;
- downloaded or already-existing media paths exist and stay inside the dataset root;
- optional discussion JSONL files when present;
- discussion comments and threads link to known channel post ids where the current schema provides those fields;
- optional discussion state consistency when present.

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
- Inspection reports summarize deterministic counts and statuses only; they are not analytics reports.
