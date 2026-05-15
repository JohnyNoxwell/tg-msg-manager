# STAGE 4B.2 - DATASET VALIDATION HARDENING REPORT

## 1. Область

Stage 4B.2 выполнен как validation hardening. Изменения ограничены read-only dataset validation, focused tests и документацией.

Не выполнялись: changelog artifact, AI chunks, analytics, OSINT/profiling/classification, OCR/STT, media analysis, external services, DB persistence.

## 2. Вход из Stage 4B.1

Использованы findings из `STAGE_4B_1_DATASET_INTEGRITY_AUDIT_REPORT.md`:

- отсутствовала message-id gap validation;
- reply-link validation была частичной;
- media validation не проверяла duplicate media ids и связи manifest/message media;
- stable validation codes требовали документации.

## 3. Реализованные проверки

- Message-id gaps: warning-level `message_id_gap_detected`.
- Channel reply links:
  - `invalid_reply_to_id` error;
  - `reply_parent_outside_export_scope` warning;
  - `reply_parent_missing` warning.
- Discussion reply links:
  - `discussion_reply_parent_outside_export_scope` warning;
  - `discussion_reply_parent_missing` warning.
- Media links:
  - `duplicate_media_id` error;
  - `invalid_media_id` error;
  - `invalid_media_message_id` error;
  - `media_message_unlinked` warning;
  - `media_manifest_without_message_media` warning;
  - `message_media_missing_manifest` warning.

Gap and missing-reply findings remain warnings because Telegram deletions, unavailable parents, and scoped exports can produce the same local dataset shape.

## 4. Files changed

- `tg_msg_manager/services/dataset_validation/jsonl_validator.py`
- `tg_msg_manager/services/dataset_validation/media_validator.py`
- `tg_msg_manager/services/dataset_validation/discussion_validator.py`
- `tg_msg_manager/services/dataset_validation/inspector.py`
- `tests/test_dataset_validation_contracts.py`
- `docs/architecture/DATASET_VALIDATION.md`
- `COMMANDS.md`
- `README.md`
- `docs/stages/active/stage_4b_2_dataset_validation_hardening.md`
- `docs/stages/README.md`

## 5. Fixtures

Новые standalone fixture directories не добавлялись. Focused tests reuse existing dataset fixtures and mutate temporary copies to cover every new warning/error code without increasing fixture duplication.

## 6. Verification

- `pytest tests/test_dataset_validation_contracts.py` - passed, 27 tests.
- `pytest tests/test_channel_export_*.py` - passed, 208 tests.
- `python3 -m compileall tg_msg_manager` - passed.
- `ruff check tg_msg_manager tests` - passed.
- `ruff format --check tg_msg_manager/services/dataset_validation tests/test_dataset_validation_contracts.py` - passed.
- `make verify` - failed in existing unrelated format-check baseline:
  - `tests/test_cli_ui_refresh.py`
  - `tg_msg_manager/cli_menu.py`
  - `tg_msg_manager/utils/ui.py`

The failing `make verify` files are outside Stage 4B.2 scope and were not modified.

## 7. Behavior

Preserved:

- validation remains read-only;
- CLI names, defaults, and exit semantics are unchanged;
- canonical dataset JSONL schema is unchanged;
- SQLite schema is unchanged.

Changed:

- `validate-dataset` and `inspect-dataset` can now report additional warning/error codes for deterministic gaps, replies, and media relationships.

## 8. Known limitations

- Gap warnings do not prove exporter data loss.
- Reply validation only uses exported fields currently present in local records.
- Discussion root replies are treated as valid root references when `reply_to_id == discussion_root_message_id`.
- SHA-256 media verification remains out of scope.

## 9. Completion

Stage 4B.2 implementation, docs, focused verification, report, and lifecycle cleanup are complete. Do not start Stage 4B.3 until this report and cleanup are reviewed.
