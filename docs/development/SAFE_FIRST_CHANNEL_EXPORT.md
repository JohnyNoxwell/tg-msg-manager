# Safe First Channel Export

## Purpose

Use this guide for a small first `export-channel` run that avoids media downloads, skips discussion comment export, validates the produced dataset, and keeps private artifacts local.

The examples use only synthetic placeholders. Replace `@example` and `exports/channels/example_dataset` with your own channel reference and the dataset directory created by the command.

A minimal synthetic Dataset Contract V1 example is available at
[`../examples/channel_dataset_minimal/`](../examples/channel_dataset_minimal/).

## First Run

Run a small metadata-only export first:

```bash
python3 -m tg_msg_manager.cli export-channel --channel @example --limit 20 --media metadata --discussion none
```

Then validate and inspect the local dataset:

```bash
python3 -m tg_msg_manager.cli validate-dataset --path exports/channels/example_dataset
python3 -m tg_msg_manager.cli inspect-dataset --path exports/channels/example_dataset
```

If validation reports warnings or errors, use the read-only doctor output:

```bash
python3 -m tg_msg_manager.cli inspect-dataset --path exports/channels/example_dataset --doctor
```

Synthetic healthy, warning, and error doctor examples are documented in
[`../user/DATASET_DOCTOR_EXAMPLES.md`](../user/DATASET_DOCTOR_EXAMPLES.md).

## Safe Defaults

The first run should stay small and metadata-only:

- `--limit 20` scopes the first dataset to a small number of channel posts.
- `--media metadata` records media metadata without downloading media files.
- `--discussion none` avoids discussion resolver work and does not fetch comments.
- `validate-dataset` and `inspect-dataset` work from local files only and do not require Telegram credentials.
- `inspect-dataset --doctor` is read-only; it does not repair, migrate, fetch, rewrite, or analyze content.

## When To Expand

Consider broader modes only after the small run validates:

- Use `--media full` only when you need local media files. Keep size and type guardrails such as `--max-media-size` and `--media-types`.
- Use `--discussion metadata` when post-level discussion metadata is enough and you do not need comment records.
- Use `--discussion full` only for scoped runs where you need discussion comments. It can produce very large datasets and does not download full media for discussion comments.
- Use `--force` when you intentionally want to ignore existing channel state and rebuild the dataset, such as after changing export mode for an existing dataset.

## Privacy Boundary

Channel datasets can contain message text, channel metadata, media metadata, local paths, state files, and validation findings. Keep export directories local by default.

Do not paste real channel names, message text, user ids, local database rows, session files, media, logs, or private export excerpts into docs, reports, issues, prompts, or screenshots.

This project exports and validates datasets. It does not perform analytics, OSINT interpretation, profiling, OCR, speech-to-text, media recognition, or LLM reporting inside the exporter, validator, inspector, or doctor.
