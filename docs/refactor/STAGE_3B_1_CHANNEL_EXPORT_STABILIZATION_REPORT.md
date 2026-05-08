# Stage 3B.1 — Channel Export Stabilization Report

## 1. Summary

Stage 3B.1 is a stabilization/refactor/test pass on top of Stage 3B media download hardening.

This pass focused on:

- checking that Stage 3C logic did not leak into executable channel-export code
- tightening Stage 3B guarantees with extra tests
- reducing `ChannelExportService` responsibility growth by extracting media preparation/progress orchestration into a dedicated helper

No Stage 3C functionality was added.

## 2. Scope

This pass stayed inside:

- `tg_msg_manager/services/channel_export/`
- channel-export tests
- refactor docs

It did not change:

- SQLite schema
- `export`
- `db-export`
- `export-pm`
- Stage 3C discussion/comment scope

## 3. Service stabilization

`ChannelExportService` had absorbed Stage 3B media preparation details:

- media download invocation
- media event routing
- cumulative media progress aggregation

These concerns were extracted into:

- `tg_msg_manager/services/channel_export/media_processor.py`

Result:

- `service.py` remains orchestration-first
- media progress aggregation rules are no longer owned directly by the service facade
- behavior remains stable

## 4. Guarantees re-checked

Confirmed in code/tests:

- `--media full` remains explicit
- default media mode remains `metadata`
- `--max-media-size` and `--media-types` parsing remain active
- old `--media full is not implemented yet` blocking logic is gone
- final `media_manifest.jsonl` rows do not keep `pending`
- final full-media statuses remain:
  - `metadata_only`
  - `downloaded`
  - `already_exists`
  - `skipped_by_size`
  - `skipped_by_type`
  - `failed`
- `downloaded` and `already_exists` carry `sha256`
- `failed` carries `error`
- failed media does not fail the whole export run
- state still persists only after payload + manifest write success
- manifest write failure still does not advance state

## 5. Tests tightened

Added/expanded coverage for:

- missing media reference in full mode -> `failed`
- media progress / downloaded / failed events in full mode
- final manifest rows not ending in `pending` for downloaded media

## 6. Stage 3C leakage check

Search terms reviewed:

- `discussion`
- `comments`
- `linked_chat`
- `linked discussion`
- `discussion_group`
- `comments.jsonl`
- `threads.jsonl`

Result:

- no executable Stage 3C logic was found in channel-export code
- matching terms appeared only in stage/refactor documentation

## 7. Verification

Commands run during this stabilization pass:

- `pytest tests/test_channel_export_*.py`
- `python3 -m compileall tg_msg_manager`
- `ruff check tg_msg_manager/services/channel_export tg_msg_manager/cli_parser.py tg_msg_manager/cli_commands.py tg_msg_manager/cli_io.py tests/test_channel_export_*.py`
- `ruff check tg_msg_manager tests`
- `ruff format --check tg_msg_manager tests`
- `make test`
- `make verify`
- `python3 -m tg_msg_manager.cli export-channel --help`

Results:

- channel-export tests passed
- targeted `ruff check` passed
- full `ruff check` passed
- `ruff format --check` passed
- compileall passed
- `make test` passed (`Ran 285 tests`)
- `make verify` passed
- `export-channel --help` confirms `none`, `metadata`, `full`, `--max-media-size`, and `--media-types`

## 8. Remaining accepted limitations

- channel export still targets broadcast channels only
- channel posts still do not persist into SQLite
- append-only incremental export still does not roll back already appended payload files if a write fails mid-run
- switching an existing metadata-only dataset to `--media full` without `--force` still downloads media only for newly fetched posts in that run

## 9. Status

Stage 3B.1 stabilization pass is complete for the intended scope.

Stage 3C remains not started.
