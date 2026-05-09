# Stage 4A.7 DB Export TXT Profile Parity Report

## Status

Complete.

## Scope

- Added DB export TXT profile selection for direct CLI and interactive menu.
- Reused the existing shared TXT rendering profile dispatcher.
- Preserved JSONL behavior and SQLite schema.
- Did not change context extraction, reply resolution, channel export, media handling, analytics, or LLM behavior.

## Implementation

- `db-export` now accepts `--txt-profile context-readable|legacy`.
- DB TXT export defaults to `context-readable` through CLI/menu/service entrypoints.
- Interactive DB export prompts for TXT profile only when TXT output is selected.
- `legacy` still uses the old flat-log TXT renderer.
- `context-readable` uses the context-block TXT renderer.

## Tests

- Parser coverage for DB TXT profile acceptance, rejection, and defaults.
- Direct command handler coverage for default and explicit legacy profile plumbing.
- Interactive menu coverage for empty, explicit, invalid, and JSON-only flows.
- DB export rendering coverage for legacy flat-log output and context-readable markers.

## Verification

- `pytest tests/test_txt_profile_cli.py tests/test_cli.py tests/test_db_exporter.py`: passed
- `python3 -m compileall tg_msg_manager`: passed
- `pytest tests`: passed, 476 tests
- `ruff check tg_msg_manager tests`: passed
- `ruff format --check tg_msg_manager tests`: passed
- `make test`: passed, 443 tests
- `make verify`: passed

## Lifecycle

- Active task moved to `docs/stages/completed/`.
- Stage index updated.
