# Отчет Stage 5D.4 - Channel Export Mode Matrix Tests

## Статус

Stage 5D.4 завершен.

## Измененные файлы

- `tg_msg_manager/services/channel_export/payload_writer.py`
- `tests/services/channel_export/test_channel_export_included_files_builder.py`
- `tests/services/channel_export/test_channel_export_service.py`
- `docs/architecture/DATASET_CONTRACT_COVERAGE_MATRIX.md`
- `docs/stages/reports/STAGE_5D_4_CHANNEL_EXPORT_MODE_MATRIX_TESTS_REPORT.md`
- `docs/stages/README.md`
- `docs/stages/completed/stage_5d_4_channel_export_mode_matrix_tests.md`
- `docs/stages/active/stage_5d_4_channel_export_mode_matrix_tests.md` moved to completed.

## Matrix rows covered

- Media modes: `none`, `metadata`, `full`.
- Discussion modes: `none`, `metadata`, `full`.
- Output toggles: `include_jsonl=False`, `include_txt=False`.
- Run modes: full, force full, incremental, no-new-posts.

## Tests added or changed

- `tests/services/channel_export/test_channel_export_included_files_builder.py`: добавлены checks для `media_mode="none"` и compact discussion included-files matrix.
- `tests/services/channel_export/test_channel_export_service.py`: добавлены runtime checks для disabled JSONL/TXT payload absence, `media_mode="none"` no-download behavior, и compact run-mode changelog/state matrix.

## Behavior fix

- Owner module: `tg_msg_manager/services/channel_export/payload_writer.py`.
- Fix: payload write session opens only enabled `messages.jsonl` / `messages.txt` payload files, while `media_manifest.jsonl` remains always opened.
- Public CLI behavior не менялся; CLI defaults still keep both payload formats enabled.

## Docs

- `docs/architecture/DATASET_CONTRACT_COVERAGE_MATRIX.md` marks Stage 5D.4 matrix gaps closed.
- `docs/architecture/DATASET_CONTRACT_V1.md` and `docs/architecture/DATASET_FORMAT.md` did not require updates; tests aligned implementation with existing docs.

## Verification

- `python3 -m pytest tests/services/channel_export/test_channel_export_service.py tests/services/channel_export/test_channel_export_included_files_builder.py tests/services/channel_export/test_channel_export_dataset_contracts.py -q`: passed, `47 passed, 6 subtests passed`.
- `python3 -m pytest tests/services/dataset_validation/test_dataset_validation_contracts.py -q`: passed, `38 passed, 2 subtests passed`.
- `python3 -m compileall tg_msg_manager`: passed.
- `ruff check tg_msg_manager tests`: passed.
- `git diff --check`: passed.

## Preserved

- CLI behavior: preserved.
- SQLite behavior and schema: preserved.
- Dataset filenames and JSON key names: preserved.
- Analytics/OSINT/LLM/media analysis boundaries: preserved.

## Lifecycle cleanup

- Active task file moved to `docs/stages/completed/`.
- `docs/stages/README.md` updated.
- Later active stages were not moved.

## Skills

- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`
