# Stage 4A.8 Discussion Export Policy Hardening Report

## Status

Complete.

## Scope

- Kept `--discussion none` as the default.
- Added/formalized `--discussion metadata` for compact post-level discussion metadata.
- Preserved explicit `--discussion full` behavior for small scoped runs.
- Did not add mass discussion crawling, discussion media download, analytics, profiling, or SQLite schema changes.

## Implementation

- Discussion mode validation now accepts `none`, `metadata`, and `full`.
- Metadata mode writes `discussion_metadata.jsonl` records from mapped post payload data and `raw_payload.replies`.
- Metadata mode does not resolve linked discussion entities and does not fetch comments.
- Post mapping reads nested Telegram reply counts from `raw_payload.replies.replies` when top-level values are missing.
- Manifest/result summaries include metadata counts and metadata file paths when metadata mode is used.
- CLI/menu/docs describe `none`, `metadata`, and `full`, with a visible heavy-mode warning for `full`.

## Verification

- `python3 -m compileall tg_msg_manager`: passed
- `pytest tests/test_channel_discussion*.py tests/test_channel_export*.py tests/test_channel_post_mapper*.py`: failed, no `tests/test_channel_discussion*.py` / `tests/test_channel_post_mapper*.py` paths matched
- `pytest tests/test_channel_export*.py`: passed, 207 tests
- `ruff check tg_msg_manager tests`: passed
- `ruff format --check tg_msg_manager tests`: passed
- `make test`: passed, 434 tests
- `make verify`: passed

## Lifecycle

- Active task moved to `docs/stages/completed/`.
- Stage index updated.
