# STAGE 5O.7 - CLI Option Boundary Report

## Статус

Завершено.

`stage-reviewer`: applied from `.skills/stage-reviewer/SKILL.md`
`architecture-guard`: applied from `.skills/architecture-guard/SKILL.md`
`stage-completion-auditor`: applied from `.skills/stage-completion-auditor/SKILL.md`

## Измененные файлы

- `tg_msg_manager/cli/channel_export_options.py`
- `tg_msg_manager/cli/commands/channel_export.py`
- `tg_msg_manager/cli_menu.py`
- `tests/cli/test_channel_export_cli.py`
- `docs/stages/reports/STAGE_5O_7_CLI_OPTION_BOUNDARY_REPORT.md`
- `docs/stages/active/stage_5o_7_cli_option_boundary.md`
- `docs/stages/completed/stage_5o_7_cli_option_boundary.md`
- `docs/stages/README.md`

## Убранное дублирование

- Для `export-channel` добавлен общий CLI-only объект `ChannelExportCommandOptions`.
- Меню больше не собирает ad hoc `argparse.Namespace` для channel export.
- Command-handler и menu path используют общий builder и общий перевод CLI-опций в `ChannelExportOptions`.

## Подтверждение сохранения контракта

- Имена команд, флаги, значения по умолчанию, help text, вывод handler-а и exit/error wrapping не менялись.
- `CLIContext` и правило `export-channel` requires client не менялись.
- SQLite schema, dataset/export/storage поведение и service facade не менялись.
- Добавлен focused parity-тест: argparse path и menu path строят одинаковые service options для выбранного channel export сценария.

## Проверки

- `pytest tests/cli/test_channel_export_cli.py`: passed, 30 passed.
- `pytest tests/cli`: passed, 87 passed.
- `python3 -m compileall tg_msg_manager`: passed.
- `ruff check tg_msg_manager/cli tg_msg_manager/cli_parser.py tg_msg_manager/cli_menu.py tests/cli`: passed.

## Оставлено без изменений

- Остальные CLI/menu команды не менялись.
- Парсер `export-channel` оставлен с текущими флагами, choices, default и type validators.
- Local-only команды и обход full `CLIContext` initialization сохранены существующей логикой.

## Lifecycle cleanup

- `docs/stages/active/stage_5o_7_cli_option_boundary.md` перемещен в `docs/stages/completed/stage_5o_7_cli_option_boundary.md`.
- `docs/stages/README.md` обновлен: Stage 5O.7 убран из active и добавлен как completed с отчетом.
