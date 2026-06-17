# STAGE 6A.2 — Runtime Resource Factory Extraction Report

Дата: 2026-06-17
Статус: completed
Тип: implementation

## Выполнено

- Создан `tg_msg_manager/application/resources.py` с `RuntimeResourceFactory`.
- Factory строит `ProcessManager`, `SQLiteStorage` и опциональный `TelethonClientWrapper` из `AppRuntime` и `needs_client`.
- `CLIContext` делегирует resource construction factory, но сохраняет публичные compatibility attributes: `runtime`, `settings`, `paths`, `pm`, `storage`, `client`, `needs_client`, service attributes, `alias_manager`, `active_uid`.
- Session path resolution сохранен: absolute `session_name` используется напрямую, relative `session_name` резолвится под `paths.project_root`.
- No-client режим сохраняет `ctx.client is None` и не создает Telegram client.

## Измененные файлы

- `tg_msg_manager/application/__init__.py`
- `tg_msg_manager/application/resources.py`
- `tg_msg_manager/cli/__init__.py`
- `tests/cli/test_cli.py`
- `docs/stages/reports/STAGE_6A_2_RUNTIME_RESOURCE_FACTORY_EXTRACTION_REPORT.md`
- `docs/stages/completed/stage_6a_2_runtime_resource_factory_extraction.md`
- `docs/stages/README.md`

## Проверки

- `pytest tests/cli/test_cli.py`: passed, 34 passed.
- `pytest tests/architecture`: passed, 19 passed.
- `python3 -m compileall tg_msg_manager`: passed.
- `ruff check tg_msg_manager tests/cli tests/architecture`: passed.
- `git diff --check`: passed.

## Сохранено

- Lifecycle behavior: preserved; lock acquire/release, signal setup, storage start/close, client connect/disconnect, stdout/stderr rendering и login error rendering остались в `CLIContext.initialize`/`shutdown`.
- CLI behavior: preserved; command names, flags, defaults, prompts, output and exit codes не менялись.
- SQLite schema/storage SQL: preserved; schema and SQL не менялись.
- Dataset/export formats: preserved; output layout, state, retry, scheduler, media/discussion behavior не менялись.
- Scope: preserved; protected service facades and compatibility wrappers не менялись.

## Skill notes

- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`

## Architecture guard

- Нарушений нет: новый application module не импортирует CLI modules.
- CLI change is mechanical delegation to application factory.
- Raw SQL, services, storage schema, dataset/export formats and protected files не изменялись.

## Lifecycle

- Stage file перемещен из `docs/stages/active/` в `docs/stages/completed/`.
- `docs/stages/README.md` обновлен: Stage 6A.2 убран из active и добавлена ссылка на report.
