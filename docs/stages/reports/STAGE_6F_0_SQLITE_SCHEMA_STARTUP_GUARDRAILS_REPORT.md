# Stage 6F.0 — SQLite schema startup guardrails report

Статус: complete.

## Что изменено

- Добавлен `tests/infrastructure/storage/test_sqlite_schema_contract.py`.
- Добавлены контрактные тесты свежего SQLite bootstrap: `PRAGMA user_version = 14`, обязательные таблицы, ключевые колонки, составные primary keys и репрезентативные индексы.
- Добавлены legacy startup сценарии для `PRAGMA user_version` 0, 5, 9, 10, 12 и 13 с проверкой финальной версии 14 и сохранения данных.
- Добавлена проверка идемпотентности повторного открытия той же базы: версия, схема и количества строк не меняются.

## Runtime

- Runtime-код не менялся.
- Новых таблиц, колонок, индексов, миграций или версий схемы не добавлено.
- Startup-регрессий, требующих исправления runtime-кода, не выявлено.

## Сохранено

- SQLite schema behavior: сохранено.
- `PRAGMA user_version`: сохранен текущий финальный уровень 14.
- CLI behavior: сохранено, CLI не менялся.
- Services behavior: сохранено, services не менялись.
- Dataset behavior: сохранено, dataset/export code не менялся.

## Проверки

- `python3 -m pytest tests/infrastructure/storage/test_storage_sqlite.py -q`: passed, 45 passed.
- `python3 -m pytest tests/infrastructure/storage/test_sqlite_schema_contract.py -q`: passed, 3 passed.
- `python3 -m compileall tg_msg_manager`: passed.
- `ruff check tg_msg_manager tests`: passed.
- `ruff format --check tg_msg_manager tests`: passed.
- `git diff --check`: passed.
- `make pre-commit`: passed; внутри выполнен `make verify`, 562 unittest passed.
- `make verify`: passed, 562 unittest passed.

## Skills

- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`
