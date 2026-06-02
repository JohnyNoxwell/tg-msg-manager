# Отчет Stage 5M.3 - Schedule / Limit / Entrypoint UX Audit

## Статус

Stage 5M.3 завершен.

## Итоговый вывод

SCHEDULE_LIMIT_ENTRYPOINT_DOCS_UPDATED

## Навыки

- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`

## Проверенные файлы

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `README.md`
- `COMMANDS.md`
- `docs/user/QUICKSTART.md`
- `docs/development/RELEASE_CANDIDATE_DECISION.md`
- `pyproject.toml`
- `run.py`
- `tg_msg_manager/cli_parser.py`
- `tg_msg_manager/cli/__init__.py`
- `tg_msg_manager/cli/__main__.py`
- `tg_msg_manager/__init__.py`
- `tg_msg_manager/services/scheduler.py`
- `tests/cli/test_cli.py`
- `tests/cli/test_channel_export_cli.py`
- `tests/services/scheduler/test_scheduler.py`
- `docs/stages/reports/STAGE_5M_0_EXTERNAL_RISK_AUDIT_VERIFICATION_REPORT.md`
- `docs/stages/README.md`

## Ответы аудита

- `schedule` является public subcommand в parser; реализация пишет macOS LaunchAgent и вызывает `launchctl`.
- README уже указывал macOS `launchd`, но `COMMANDS.md` не имел отдельной секции с non-macOS caveat.
- `export --limit` передается в `sync_chat`; при multi-dialog user export лимит применяется отдельно к каждому dialog.
- `export-channel --limit` является лимитом постов одного channel export run; `retry --limit` ограничивает retry tasks.
- `run.py`, `python3 -m tg_msg_manager.cli` и `tg-msg-manager` делегируют к одному CLI main; divergence не найден.

## Измененные docs

- `COMMANDS.md`: добавлены clarification для `export --limit`, отдельная секция `schedule` и entrypoint equivalence.

## Follow-up tests

- Отдельные follow-up tests не требуются для docs-only уточнений; существующие parser/scheduler tests уже подтверждают command presence, default parsing и launchctl path.

## Проверки

- `git diff --check`: passed.

## Подтверждения

- CLI/parser/runtime behavior не менялся.
- Entrypoints, tests, fixtures, output formats, SQLite schema, package metadata, release state и version не менялись.

## Lifecycle

- Финальный отчет создан.
- Stage-файл перенесен из `docs/stages/active/` в `docs/stages/completed/`.
- `docs/stages/README.md` обновляется в рамках серии Stage 5M.
