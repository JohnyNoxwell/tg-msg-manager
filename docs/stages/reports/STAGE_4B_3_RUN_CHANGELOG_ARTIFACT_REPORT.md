# STAGE 4B.3 - RUN CHANGELOG ARTIFACT REPORT

## 1. Область

Stage 4B.3 добавил derived per-run artifact для `export-channel`: `run_changelog.jsonl`.

Не выполнялись: AI chunks, analytics, OSINT/profiling/classification, OCR/STT, media analysis, external services, SQLite schema changes, DB persistence.

## 2. Решение

Текущих artifacts было недостаточно: `manifest.json`, result events и `channel_export_state.json` показывали totals/current cursor, но не давали durable per-run list новых message ids.

Добавлен `run_changelog.jsonl`, append-only JSONL artifact рядом с channel dataset files.

## 3. Schema

Каждая строка содержит:

- `run_id`
- `export_target_type`
- `export_target_id`
- `export_target_name`
- `run_mode`
- `started_at`
- `finished_at`
- `previous_cursor`
- `new_cursor`
- `new_message_count`
- `new_message_ids`
- `first_new_message_id`
- `last_new_message_id`
- `first_new_message_date`
- `last_new_message_date`
- `artifact_paths`
- `warnings`

No-new-posts run пишет строку с `new_message_count: 0` и пустым `new_message_ids`.

## 4. Files changed

- `tg_msg_manager/services/channel_export/run_changelog.py`
- `tg_msg_manager/services/channel_export/service.py`
- `tg_msg_manager/services/channel_export/included_files_builder.py`
- `tg_msg_manager/services/dataset_validation/inspector.py`
- `tests/test_channel_export_service.py`
- `tests/test_channel_export_included_files_builder.py`
- `docs/architecture/DATASET_FORMAT.md`
- `docs/architecture/DATASET_VALIDATION.md`
- `COMMANDS.md`
- `README.md`
- `docs/stages/active/stage_4b_3_run_changelog_artifact.md`
- `docs/stages/README.md`

## 5. Behavior

Preserved:

- canonical `messages.jsonl`, `messages.txt`, `media_manifest.jsonl`, manifest, and state schemas are unchanged except manifest `included_files` now lists `run_changelog.jsonl`;
- CLI names, options, and defaults are unchanged;
- state still advances only after payload, manifest, and changelog writes succeed;
- validation remains read-only.

Changed:

- completed full/force/incremental/no-new channel export runs append one changelog row;
- dataset inspection recognizes `run_changelog.jsonl` as a known file instead of reporting it as unknown.

## 6. Verification

- `pytest tests/test_channel_export_service.py tests/test_channel_export_included_files_builder.py tests/test_channel_export_manifest_coordinator.py` - passed, 35 tests.
- `pytest tests/test_channel_export_*.py` - passed, 208 tests.
- `pytest tests/test_db_export_components.py` - passed, 5 tests.
- `pytest tests/test_dataset_validation_contracts.py` - passed, 27 tests.
- `python3 -m compileall tg_msg_manager` - passed.
- `ruff check tg_msg_manager tests` - passed.
- `ruff format --check tg_msg_manager/services/channel_export tg_msg_manager/services/dataset_validation tests/test_channel_export_service.py tests/test_channel_export_included_files_builder.py tests/test_dataset_validation_contracts.py` - passed.
- `make verify` - failed in existing unrelated format-check baseline:
  - `tests/test_cli_ui_refresh.py`
  - `tg_msg_manager/cli_menu.py`
  - `tg_msg_manager/utils/ui.py`

The failing `make verify` files are outside Stage 4B.3 scope and were not modified.

## 7. SQLite/schema

SQLite schema unchanged. No DB persistence added.

Dataset canonical post schema unchanged. A derived dataset artifact was added and documented.

## 8. Known limitations

- `started_at` and `finished_at` currently reflect changelog-write time, not full Telegram fetch duration.
- `warnings` is present but currently empty; runtime warning capture is not implemented.
- If a failure happens after manifest write and before changelog/state save, state is not advanced, but manifest may already have been replaced, matching existing non-ACID multi-file limitations.

## 9. Completion

Stage 4B.3 implementation, docs, focused verification, report, and lifecycle cleanup are complete. Stage 4B.4 was not started.
