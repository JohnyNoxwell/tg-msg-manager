# STAGE 4D.2 — READ-ONLY DATASET DOCTOR REPORT

## Статус

- Stage 4D.2 завершён.
- Добавлен read-only dataset doctor поверх validation findings.
- Export behavior, dataset output formats, state/manifest/JSONL/media files, SQLite schema и существующее поведение `validate-dataset` / `inspect-dataset` без новых flags не менялись.

## Chosen command surface

- Выбрано `inspect-dataset --doctor`.
- Причина: doctor является read-only diagnostic inspection layer после validation, поэтому расширение существующего `inspect-dataset` минимизирует CLI churn и не добавляет новый top-level command.
- Поддержан текущий JSON style: `inspect-dataset --doctor --json`.

## Files changed

- `tg_msg_manager/services/dataset_validation/doctor.py`
- `tg_msg_manager/services/dataset_validation/report_renderer.py`
- `tg_msg_manager/services/dataset_validation/__init__.py`
- `tg_msg_manager/cli_parser.py`
- `tg_msg_manager/cli/commands/dataset.py`
- `tests/services/dataset_validation/test_dataset_validation_contracts.py`
- `COMMANDS.md`
- `README.md`
- `docs/development/CLI_CONTRACT.md`
- `docs/architecture/DATASET_CONTRACT_V1.md`
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_4D_2_READ_ONLY_DATASET_DOCTOR_REPORT.md`
- `docs/stages/completed/stage_4d_2_read_only_dataset_doctor.md`

## Doctor checks implemented

- Doctor reuses `validate_dataset` findings.
- Each finding includes:
  - issue code;
  - severity: `INFO`, `WARNING`, `ERROR`;
  - artifact path when available;
  - message;
  - deterministic suggested next action.
- Healthy datasets produce `dataset_healthy` INFO and no ERROR.
- Missing required files, invalid JSON/JSONL, missing media files, counter drift, duplicate ids, relationship warnings, and unknown extra files receive deterministic actions.

## Read-only guarantee

- Doctor does not write, repair, migrate, fetch, analyze content, OCR/STT, optimize media, or call Telegram.
- Focused tests snapshot fixture files before and after doctor/validate/inspect calls.

## Tests added/updated

- Healthy dataset doctor output has no ERROR.
- Missing required file produces ERROR.
- Optional missing discussion metadata in `discussion none` does not produce ERROR.
- Invalid JSONL produces ERROR.
- Doctor is read-only.
- Doctor Markdown/JSON renderers are deterministic enough for contract assertions.
- CLI parser accepts `inspect-dataset --doctor`.
- CLI handler renders doctor JSON.
- CLI dispatch for `inspect-dataset --doctor` remains read-only/no live context.

## Docs updated

- `COMMANDS.md` documents `inspect-dataset --doctor`.
- `README.md` overview and command examples mention doctor mode.
- `docs/development/CLI_CONTRACT.md` records `--doctor=False`.
- `docs/architecture/DATASET_CONTRACT_V1.md` records doctor boundary.

## Checks

- `ruff check tg_msg_manager tests`: passed.
- `python3 -m compileall tg_msg_manager`: passed.
- `python3 -m pytest tests -q -k "dataset or doctor or validate or inspect"`: passed, 65 passed, 438 deselected, 2 subtests passed.
- `git diff --check`: passed.

## Не выполнялось

- `make test`: not run; stage-required filtered tests passed.
- `stage-completion-auditor`: not run; no such skill/tool is available in this session.
- `architecture-guard`: not run; no such skill/tool is available in this session.

## Completion status

- Doctor functionality exists: yes.
- Doctor is read-only: yes.
- Focused tests cover read-only behavior: yes.
- Docs describe command/flag: yes.
- Export behavior unchanged: yes.
- Required report exists: yes.
- Lifecycle cleanup completed: yes.
