# Stage 3B — Media Download Hardening Report

## 1. Summary

Stage 3B adds controlled full-media download to `export-channel` without changing the default dataset-projection behavior.

Implemented in this stage:

- dedicated `media_downloader.py` under `services/channel_export/`
- explicit `--media full`
- `--max-media-size`
- `--media-types`
- `sha256` for downloaded and reused files
- `already_exists` reuse path for existing files
- final media statuses in `media_manifest.jsonl`
- media progress events and CLI rendering

## 2. Baseline

Stage 3A created the direct channel export surface.

Stage 3A.1 added:

- `channel_export_state.json`
- append-only incremental updates
- `--force` full re-export behavior
- progress events
- safe state persistence after successful payload + manifest writes

That baseline is documented in:

- `docs/refactor/STAGE_3A_1_CHANNEL_EXPORT_OPERATIONAL_HARDENING_REPORT.md`

## 3. Implemented media modes

- `--media none`
  - no media rows are downloaded
- `--media metadata`
  - media metadata is exported without downloading files
- `--media full`
  - downloads are attempted only when explicitly requested
  - `50MB` is used as the default max media size unless overridden

## 4. CLI changes

`export-channel` now supports:

- `--media full`
- `--max-media-size`
- `--media-types`

The default remains:

- `--media metadata`

## 5. Media status model

Final `media_manifest.jsonl` rows now use:

- `metadata_only`
- `downloaded`
- `already_exists`
- `skipped_by_size`
- `skipped_by_type`
- `failed`

For downloaded or reused files:

- `sha256` is recorded

For failures:

- `error` is recorded

## 6. Download safety

Stage 3B keeps media logic inside `tg_msg_manager/services/channel_export/`.

Safety properties:

- no SQLite changes
- no analytics/OCR/video analysis
- no changes to `export`, `db-export`, or `export-pm`
- existing media files are reused instead of re-downloaded
- one failed media item is recorded without failing the whole export run
- channel export state is still written only after successful payload + manifest write completion

## 7. Progress/events

Added media-specific events:

- `channel_export.media_progress`
- `channel_export.media_downloaded`
- `channel_export.media_skipped`
- `channel_export.media_failed`

CLI now renders media progress summaries during `--media full` runs.

## 8. Tests added/updated

Added:

- `tests/test_channel_export_media_downloader.py`

Updated:

- `tests/test_channel_export_cli.py`
- `tests/test_channel_export_manifest.py`
- `tests/test_channel_export_media_policy.py`
- `tests/test_channel_export_payload_writer.py`
- `tests/test_channel_export_post_mapper.py`
- `tests/test_channel_export_service.py`
- `tests/test_channel_export_state_manager.py`

Covered cases:

- metadata mode does not download
- full mode downloads files
- existing files become `already_exists`
- `sha256` is computed
- size/type guardrails skip correctly
- download failures become `failed`
- one media failure does not fail the whole export
- final media statuses are written into `media_manifest.jsonl`

## 9. Verification results

Commands run for this stage:

- `pytest tests/test_channel_export_*.py`
- `python3 -m compileall tg_msg_manager`
- `ruff check tg_msg_manager/services/channel_export tg_msg_manager/cli_parser.py tg_msg_manager/cli_commands.py tg_msg_manager/cli_io.py tests/test_channel_export_*.py`
- `ruff check tg_msg_manager tests`
- `ruff format --check tg_msg_manager tests`
- `make test`
- `make verify`
- `python3 -m tg_msg_manager.cli export-channel --help`

Results at implementation time:

- channel-export tests passed
- targeted `ruff check` passed
- full `ruff check` passed
- `ruff format --check` passed
- compileall passed
- `make test` passed (`Ran 283 tests`)
- `make verify` passed
- `export-channel --help` shows `--media full`, `--max-media-size`, and `--media-types`

## 10. Remaining limitations

- channel export still targets broadcast channels only
- channel posts still do not persist into SQLite
- append-only incremental export still does not roll back already appended payload files if a write fails mid-run
- switching an existing metadata-only dataset to `--media full` without `--force` downloads media only for newly fetched posts in that run

## 11. Deferred to Stage 3C

Still deferred:

- discussion group export
- comments export
- post-to-discussion mapping
- reply-chain export under channel posts

## 12. Ready for Stage 3C?

Yes for scope handoff.

Stage 3B is complete for controlled media download hardening, and Stage 3C remains intentionally out of scope here.
