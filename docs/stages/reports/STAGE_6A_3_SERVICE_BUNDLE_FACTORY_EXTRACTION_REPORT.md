# STAGE 6A.3 — Service Bundle Factory Extraction Report

Дата: 2026-06-17
Статус: completed
Тип: implementation

## Выполнено

- Создан `tg_msg_manager/application/services.py` с `ServiceBundle` и `create_service_bundle`.
- Service bundle содержит `exporter`, `cleaner`, `db_exporter`, `private_archive`, `channel_exporter`, `retry_worker`, `alias_manager`.
- `CLIContext` больше не импортирует и не конструирует service classes напрямую; он создает bundle через application factory.
- Compatibility attributes `CLIContext.exporter`, `cleaner`, `db_exporter`, `private_archive`, `channel_exporter`, `retry_worker`, `alias_manager` сохранены.

## Измененные файлы

- `tg_msg_manager/application/__init__.py`
- `tg_msg_manager/application/services.py`
- `tg_msg_manager/cli/__init__.py`
- `tests/cli/test_cli.py`
- `tests/architecture/test_static_boundaries.py`
- `docs/stages/reports/STAGE_6A_3_SERVICE_BUNDLE_FACTORY_EXTRACTION_REPORT.md`
- `docs/stages/completed/stage_6a_3_service_bundle_factory_extraction.md`
- `docs/stages/README.md`

## Проверки

- `pytest tests/cli/test_cli.py`: passed, 35 passed.
- `pytest tests/architecture`: passed, 20 passed.
- `python3 -m compileall tg_msg_manager`: passed.
- `ruff check tg_msg_manager tests/cli tests/architecture`: passed.
- `git diff --check`: passed.

## Сохранено

- Service constructor arguments: preserved; tests verify output dirs, base dirs, client/storage, event sink, cleaner lists/artifact roots, retry dependencies, alias paths.
- CLI behavior: preserved; command names, flags, defaults, prompts, output and exit codes не менялись.
- Lifecycle behavior: preserved; lock, storage start/close, Telegram connect/disconnect and login error rendering остаются в `CLIContext`.
- SQLite schema/storage SQL: preserved; schema and SQL не менялись.
- Dataset/export formats: preserved; output layout, state, retry, media/discussion behavior не менялись.
- Scope: preserved; protected service facades and compatibility wrappers не менялись.

## Skill notes

- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`

## Architecture guard

- Нарушений нет: application module imports services/core only and does not import CLI modules.
- CLI change is mechanical delegation to application service bundle factory.
- Raw SQL, storage schema, dataset/export formats and protected service facades не изменялись.

## Lifecycle

- Stage file перемещен из `docs/stages/active/` в `docs/stages/completed/`.
- `docs/stages/README.md` обновлен: Stage 6A.3 убран из active и добавлена ссылка на report.
