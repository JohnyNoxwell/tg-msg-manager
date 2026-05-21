# STAGE 4C.0 — STRUCTURAL DECOMPOSITION REPORT

## Статус

- Stage 4C.0 был слишком крупным для одного безопасного прохода.
- Исходный active task декомпозирован на `stage_4c_0b_channel_export_workflow_split.md` и `stage_4c_0c_test_layout_grouping.md`.
- Unit A завершён.
- Unit B завершён отдельным follow-up report: `STAGE_4C_0B_CHANNEL_EXPORT_WORKFLOW_SPLIT_REPORT.md`.
- Unit C завершён отдельным follow-up report: `STAGE_4C_0C_TEST_LAYOUT_GROUPING_REPORT.md`.
- Stage 4C.0 overall: complete.

## Переносы Unit A

- `tg_msg_manager/cli.py` -> `tg_msg_manager/cli/__init__.py`
- `python -m tg_msg_manager.cli` entrypoint -> `tg_msg_manager/cli/__main__.py`
- `tg_msg_manager/cli_commands.py` handlers -> `tg_msg_manager/cli/commands/setup.py`
- `tg_msg_manager/cli_commands.py` handlers -> `tg_msg_manager/cli/commands/export.py`
- `tg_msg_manager/cli_commands.py` handlers -> `tg_msg_manager/cli/commands/db_export.py`
- `tg_msg_manager/cli_commands.py` handlers -> `tg_msg_manager/cli/commands/channel_export.py`
- `tg_msg_manager/cli_commands.py` handlers -> `tg_msg_manager/cli/commands/dataset.py`
- `tg_msg_manager/cli_commands.py` handlers -> `tg_msg_manager/cli/commands/maintenance.py`
- `tg_msg_manager/cli_commands.py` handlers -> `tg_msg_manager/cli/commands/retry.py`
- `tg_msg_manager/cli_commands.py` handlers -> `tg_msg_manager/cli/commands/report.py`
- `tg_msg_manager/cli_commands.py` remains compatibility re-export.

## Изменённые файлы

- `tg_msg_manager/cli/__init__.py`
- `tg_msg_manager/cli/__main__.py`
- `tg_msg_manager/cli/commands/__init__.py`
- `tg_msg_manager/cli/commands/setup.py`
- `tg_msg_manager/cli/commands/export.py`
- `tg_msg_manager/cli/commands/db_export.py`
- `tg_msg_manager/cli/commands/channel_export.py`
- `tg_msg_manager/cli/commands/dataset.py`
- `tg_msg_manager/cli/commands/maintenance.py`
- `tg_msg_manager/cli/commands/retry.py`
- `tg_msg_manager/cli/commands/report.py`
- `tg_msg_manager/cli_commands.py`
- `tests/test_cli.py`
- `docs/architecture/PROJECT_ARCHITECTURE_OVERVIEW.md`
- `docs/architecture/DB_EXPORT_ENTRYPOINT_AUDIT.md`
- `docs/architecture/PRIVATE_ARCHIVE_ENTRYPOINT_AUDIT.md`
- `docs/stages/active/stage_4c_0b_channel_export_workflow_split.md`
- `docs/stages/active/stage_4c_0c_test_layout_grouping.md`
- `docs/stages/README.md`

## Проверки

- `python3 -m compileall tg_msg_manager`: passed
- `ruff check tg_msg_manager tests`: passed
- `pytest tests -q -k "cli or command or menu"`: passed, 84 passed, 407 deselected, 2 subtests passed
- `python3 -m tg_msg_manager.cli --help`: passed
- `python3 -c "from tg_msg_manager.cli import main; from tg_msg_manager.cli_commands import _handle_export_command; print(callable(main), callable(_handle_export_command))"`: passed
- `ruff format --check tg_msg_manager tests`: failed, existing formatting drift in `tests/test_cli_ui_refresh.py`, `tg_msg_manager/cli_menu.py`, `tg_msg_manager/utils/ui.py`; these files were not changed by Unit A.

## Сохранено

- Public import `tg_msg_manager.cli`: yes
- `python3 -m tg_msg_manager.cli`: yes
- Console entrypoint target `tg_msg_manager.cli:main`: yes
- `tg_msg_manager.cli_commands` handler imports: yes
- CLI commands, flags, defaults, and output contracts: yes
- SQLite schema: yes
- Dataset formats: yes

## Не выполнялось

- Full `pytest tests -q`: not run; Unit A required focused CLI verification only.

## Завершение

- Unit A complete.
- Unit B complete.
- Unit C complete.
- Stage 4C.0 complete.
