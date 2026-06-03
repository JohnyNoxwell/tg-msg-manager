# Stage 5N.1 Report — Target Names History CLI

## Статус

COMPLETED

## Измененные файлы

Добавлены:

- `tg_msg_manager/cli/commands/target_names.py`
- `tg_msg_manager/services/target_names/renderers.py`
- `tests/cli/test_target_names_cli.py`
- `tests/services/target_names/test_target_names_renderers.py`

Изменены:

- `COMMANDS.md`
- `docs/development/CLI_CONTRACT.md`
- `docs/user/QUICKSTART.md`
- `tg_msg_manager/cli/__init__.py`
- `tg_msg_manager/cli/commands/__init__.py`
- `tg_msg_manager/cli_parser.py`
- `tg_msg_manager/cli_commands.py`
- `tg_msg_manager/services/target_names/__init__.py`
- `tests/cli/test_cli.py`

Удалены: нет.

## CLI contract

- Добавлена команда `target names <target>`.
- Defaults: `--field all`, `--format text`.
- `--field`: `all`, `username`, `display_name`, `title`.
- `--format`: `text`, `json`.
- Команда добавлена в local-only command set и не требует Telegram client initialization.

## Output contract

- Text output содержит `Target`, `Type`, optional `Current`, и `<Field> history`.
- Missing old values в text выводятся как `-`.
- JSON output содержит deterministic top-level keys: `target`, `target_type`, `current`, `history`.
- JSON missing values выводятся как `null`.
- Username в renderer выводится как handle с `@`.

## Errors

- Unknown target: controlled `target_not_found`, exit code `1`.
- Ambiguous target: controlled `ambiguous_target`, exit code `1`.
- Invalid `--field` / `--format`: argparse validation.
- JSON errors пишутся в stderr как JSON-only payload.

## Docs updated

- `COMMANDS.md`: команда, аргументы, local-only limitation, title-history limitation.
- `docs/user/QUICKSTART.md`: навигация к local target name history.
- `docs/development/CLI_CONTRACT.md`: command surface row.

## Tests

Добавлены:

- CLI tests для parser defaults/validation, local-only context, JSON success, unknown/ambiguous errors.
- Renderer tests для text all/default, field filtering, JSON output, empty history, null old values, JSON error.

## Verification

- `python3 -m unittest tests.cli.test_target_names_cli -q`: passed.
- `python3 -m unittest tests.services.target_names.test_target_names_renderers -q`: passed.
- `python3 -m unittest discover tests -p '*target*names*.py'`: passed.
- `python3 -m unittest discover tests -p '*target*history*.py'`: passed.
- `python3 -m unittest tests.cli.test_cli -q`: passed.
- `python3 -m unittest tests.cli.test_non_channel_contract_cli -q`: passed.
- `git diff --check`: passed.

Не запускались:

- `make test`: deferred; focused stage checks passed.
- `make verify`: deferred; focused stage checks passed.

## Границы

- SQLite schema changed: no.
- Telegram calls added: no.
- Export formats changed: no.
- Existing command defaults changed: no.
- Title-history limitation: current SQLite schema has current chat title only, no title history.
- Release/tag/package actions: no.

## Skills

- stage-reviewer: applied from .skills/stage-reviewer/SKILL.md
- architecture-guard: applied from .skills/architecture-guard/SKILL.md
- stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md
