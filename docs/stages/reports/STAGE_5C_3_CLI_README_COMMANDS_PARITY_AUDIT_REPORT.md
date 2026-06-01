# STAGE 5C.3 — CLI / README / COMMANDS PARITY AUDIT REPORT

## Итог

Stage 5C.3 завершен. CLI runtime не менялся; исправлена фактическая drift в `docs/development/CLI_CONTRACT.md`.

## Проверенные команды и flags

- Root help: `export`, `update`, `retry`, `report`, `clean`, `export-pm`, `delete`, `schedule`, `setup`, `db-export`, `validate-dataset`, `inspect-dataset`, `export-channel`.
- `export-channel`: `--channel`, `--limit`, `--media`, `--max-media-size`, `--media-types`, `--discussion`, `--max-comments-per-post`, `--output-dir`, `--force`.
- `validate-dataset`: `--path`, `--json`.
- `inspect-dataset`: `--path`, `--json`, `--doctor`.
- `db-export`: `--user-id`, `--json`, `--txt-profile`.

## Проверенные файлы

- `AGENTS.md`
- `docs/stages/active/stage_5c_3_cli_readme_commands_parity_audit.md`
- `tg_msg_manager/cli_parser.py`
- `tg_msg_manager/cli/__init__.py`
- `tg_msg_manager/cli/commands/channel_export.py`
- `tg_msg_manager/cli/commands/dataset.py`
- `README.md`
- `COMMANDS.md`
- `docs/development/CLI_CONTRACT.md`
- `tests/cli/test_cli.py`
- `tests/cli/test_channel_export_cli.py`
- `tests/services/dataset_validation/test_dataset_validation_contracts.py`

## Docs drift

- `docs/development/CLI_CONTRACT.md` did not list `export-channel`.
- `docs/development/CLI_CONTRACT.md` listed `db-export` without `--txt-profile=context-readable`.
- `docs/development/CLI_CONTRACT.md` had an outdated verification date and incomplete contract-test references.
- `README.md` and `COMMANDS.md` matched the audited parser surface closely enough; no changes needed.

## Измененные docs

- `docs/development/CLI_CONTRACT.md`
- `docs/stages/reports/STAGE_5C_3_CLI_README_COMMANDS_PARITY_AUDIT_REPORT.md`
- `docs/stages/README.md`
- `docs/stages/completed/stage_5c_3_cli_readme_commands_parity_audit.md`

## Проверки

- `python3 -m tg_msg_manager.cli --help` — passed.
- `python3 -m tg_msg_manager.cli export-channel --help` — passed.
- `python3 -m tg_msg_manager.cli validate-dataset --help` — passed.
- `python3 -m tg_msg_manager.cli inspect-dataset --help` — passed.
- `python3 -m pytest tests/cli/test_cli.py tests/cli/test_channel_export_cli.py tests/services/dataset_validation/test_dataset_validation_contracts.py -q` — passed; 98 passed, 4 subtests passed.
- `python3 -m compileall tg_msg_manager` — passed.
- `git diff --check` — passed.

## Подтверждения

- CLI runtime behavior не изменялось.
- Command names, flags, defaults, parser behavior, output formats, exit codes и handlers не изменялись.
- Services, storage, dataset formats и SQLite schema не изменялись.

## Навыки

- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`

## Lifecycle

- Финальный отчет создан.
- Stage-файл перенесен из `docs/stages/active/` в `docs/stages/completed/`.
- `docs/stages/README.md` обновлен.
