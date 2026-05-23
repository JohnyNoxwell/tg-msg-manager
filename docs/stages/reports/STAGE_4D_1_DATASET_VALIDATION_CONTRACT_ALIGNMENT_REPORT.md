# STAGE 4D.1 — DATASET VALIDATION CONTRACT ALIGNMENT REPORT

## Статус

- Stage 4D.1 завершён.
- `validate-dataset` и `inspect-dataset` усилены в рамках `DATASET_CONTRACT_V1`.
- Validation/inspection остаются read-only.
- Export behavior, channel export behavior, media/discussion export behavior, dataset output formats, manifest/state formats, SQLite schema, CLI names/flags/defaults не менялись.

## Validators changed

- Добавлен `tg_msg_manager/services/dataset_validation/contract_validator.py`.
- Обновлён `tg_msg_manager/services/dataset_validation/discussion_validator.py`.
- Обновлён `tg_msg_manager/services/dataset_validation/inspector.py`.
- Обновлена модель `DiscussionSummary` в `tg_msg_manager/services/dataset_validation/models.py`.

## Checks added

- `run_changelog.jsonl` теперь проверяется как required contract artifact.
- `discussion_metadata.jsonl` добавлен в known dataset files и валидируется как JSONL.
- Discussion metadata rows проверяются на `channel_message_id`, `replies_count` и связь с `messages.jsonl`.
- Manifest discussion mode теперь проверяется против mode-specific artifacts:
  - `none`: discussion files are unexpected warnings;
  - `metadata`: `discussion_metadata.jsonl` required;
  - `full`: comments JSONL/TXT, threads JSONL, discussion state required.
- Manifest `dataset_type` и `schema_version` проверяются против V1 как warnings on drift.
- Inspection summary now includes `metadata_count` in `discussions`.

## Tests added/updated

- Added tests for missing `run_changelog.jsonl`.
- Added tests for `--discussion metadata` artifact requirement and valid metadata summary.
- Added read-only regression for validate/inspect over a copied fixture.
- Updated valid fixtures with `run_changelog.jsonl`.
- Updated partial discussion fixture expectation to contract error when full-mode discussion state is absent.

## Docs

- `COMMANDS.md` updated for user-visible validation scope.
- `docs/architecture/DATASET_VALIDATION.md` updated with new checks/codes.
- `docs/architecture/DATASET_CONTRACT_V1.md` did not need correction.

## Checks

- `python3 -m compileall tg_msg_manager`: passed.
- `ruff check tg_msg_manager tests`: passed.
- `python3 -m pytest tests -q -k "dataset_validation or validate_dataset or inspect_dataset"`: passed, 30 passed, 465 deselected, 2 subtests passed.

## Не выполнялось

- `make test`: not run; focused command required by stage passed.
- `stage-completion-auditor`: not run; no such skill/tool is available in this session.
- `architecture-guard`: not run; no such skill/tool is available in this session.

## Completion status

- validate/inspect behavior aligns with `DATASET_CONTRACT_V1`: yes.
- read-only behavior preserved: yes.
- export behavior unchanged: yes.
- focused tests exist: yes.
- required docs updated: yes.
- required report exists: yes.
- lifecycle cleanup completed: yes.
