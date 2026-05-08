# Stage 3C.2 — Discussion Resolver And Models Report

## Summary

Stage 3C.2 added the discussion export skeleton without runtime comment export.

Implemented:

- Discussion options and validation.
- Discussion models for options, source resolution, threads, comments, state, and result.
- Conservative linked discussion resolver skeleton.
- `export-channel` CLI flags:
  - `--discussion none|full`
  - `--max-comments-per-post N`
- CLI option passthrough into `ChannelExportOptions`.

## Boundaries Preserved

- No comment fetching implemented.
- No discussion dataset files written.
- No discussion state files written.
- No SQLite changes.
- No migrations.
- No analytics or OSINT logic.
- No changes to `export`, `db-export`, or `export-pm`.
- Stage 3C.3 was not started.

## Verification

Commands run:

- `pytest tests/test_channel_export_discussion_*.py tests/test_channel_export_cli.py` — passed, 31 tests.
- `pytest tests/test_channel_export_*.py` — passed, 99 tests.
- `python3 -m compileall tg_msg_manager` — passed.
- `ruff check tg_msg_manager tests` — passed.
- `ruff format --check tg_msg_manager tests` — passed.
- `python3 -m tg_msg_manager.cli export-channel --help` — passed and shows discussion flags.

## Status

Stage 3C.2: complete.

Stage 3C.3: not started.
