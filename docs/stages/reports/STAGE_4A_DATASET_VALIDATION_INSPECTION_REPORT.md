# Stage 4A — Dataset Validation / Inspection Report

## 1. Summary

Stage 4A added read-only validation and inspection commands for direct channel export datasets.

The implementation validates deterministic dataset structure and relationships only. It does not fetch from Telegram, repair datasets, migrate schemas, analyze content, process media, or write SQLite data.

## 2. Commands added

- `python3 -m tg_msg_manager.cli validate-dataset --path exports/channels/example`
- `python3 -m tg_msg_manager.cli validate-dataset --path exports/channels/example --json`
- `python3 -m tg_msg_manager.cli inspect-dataset --path exports/channels/example`
- `python3 -m tg_msg_manager.cli inspect-dataset --path exports/channels/example --json`

## 3. Modules added

- `tg_msg_manager/services/dataset_validation/__init__.py`
- `tg_msg_manager/services/dataset_validation/options.py`
- `tg_msg_manager/services/dataset_validation/models.py`
- `tg_msg_manager/services/dataset_validation/jsonl_validator.py`
- `tg_msg_manager/services/dataset_validation/manifest_validator.py`
- `tg_msg_manager/services/dataset_validation/state_validator.py`
- `tg_msg_manager/services/dataset_validation/media_validator.py`
- `tg_msg_manager/services/dataset_validation/discussion_validator.py`
- `tg_msg_manager/services/dataset_validation/inspector.py`
- `tg_msg_manager/services/dataset_validation/report_renderer.py`

## 4. Validation coverage

- Required base file presence.
- JSON and JSONL parseability.
- Message `message_id` presence and duplicate detection.
- Manifest shape, included-file, and count sanity checks.
- Channel and discussion state parseability and counter sanity checks.
- Media manifest status counts.
- Missing downloaded / already-existing media files.
- Media path traversal outside the dataset root.
- Optional discussion comments, threads, discussion text projection, and discussion state.
- Discussion comment/thread linkage to known channel post ids where current schema fields exist.

## 5. Inspection coverage

- Dataset path.
- Detected file existence and sizes.
- Message count and min/max message id.
- Media record count and status counts.
- Discussion presence, comment count, and thread count.
- Manifest summary.
- State cursor and aggregate counters.
- Validation status/error/warning notes.

## 6. Files changed

- `tg_msg_manager/cli.py`
- `tg_msg_manager/cli_commands.py`
- `tg_msg_manager/cli_parser.py`
- `tg_msg_manager/services/dataset_validation/`
- `tests/test_cli.py`
- `tests/test_dataset_validation_contracts.py`
- `tests/fixtures/dataset_validation/`
- `docs/architecture/DATASET_VALIDATION.md`
- `docs/architecture/README.md`
- `docs/development/CLI_CONTRACT.md`
- `docs/README.md`
- `README.md`
- `COMMANDS.md`
- `CHANGELOG.md`
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_4A_DATASET_VALIDATION_INSPECTION_REPORT.md`

## 7. Tests

- Added fixture-based dataset validation contract coverage.
- Added CLI parser/dispatch coverage for `validate-dataset` and `inspect-dataset`.
- Added renderer JSON/Markdown coverage.
- Added media relationship coverage for downloaded, failed, skipped, unknown status, and path traversal records.
- Added discussion relationship coverage for absent, valid, invalid JSONL, unlinked, partial, and duplicate-comment datasets.
- Updated the existing CLI command inventory test for the new public commands.

## 8. Verification results

- `pytest tests/test_dataset_validation_*.py`: passed, 20 tests.
- `pytest tests/test_dataset_validation_*.py tests/test_cli.py`: passed, 43 tests.
- `pytest tests/test_channel_export_*.py`: passed, 186 tests.
- `python3 -m compileall tg_msg_manager`: passed.
- `ruff check tg_msg_manager tests`: passed.
- `ruff format --check tg_msg_manager tests`: passed.
- `python3 -m tg_msg_manager.cli validate-dataset --help`: passed.
- `python3 -m tg_msg_manager.cli inspect-dataset --help`: passed.
- `make test`: passed on sequential rerun, 412 unittest tests.
- `make verify`: passed on sequential rerun, including compile, ruff check, format check, and 412 unittest tests.

Note: an earlier parallel `make test` / `make verify` attempt failed because both commands ran the same SQLite-heavy unittest suite concurrently. The commands were rerun sequentially and passed.

## 9. Runtime behavior statement

No Telegram fetching behavior changed.
No channel export behavior changed.
No dataset schema changed.
No state schema changed.
No SQLite schema changed.
No analytics/OCR/STT/media optimization added.

## 10. Remaining limitations

- SHA-256 media verification is not implemented by default.
- Count mismatches are warnings in most cases to tolerate older dataset drift.
- Discussion relationship validation is limited to current schema fields.
- Inspection reports deterministic counts/statuses only and do not interpret content.

## 11. Status

Stage 4A complete.
