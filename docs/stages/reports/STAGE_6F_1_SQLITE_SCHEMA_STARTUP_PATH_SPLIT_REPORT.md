# Stage 6F.1 — SQLite schema startup path split report

Статус: complete.

## Что изменено

- Добавлен `tg_msg_manager/infrastructure/storage/schema/startup.py`.
- Введены явные startup-фазы:
  - current schema creation;
  - compatibility column ensures;
  - index creation;
  - legacy migration execution;
  - final commit.
- `SQLiteSchemaMixin._init_db()` оставлен оркестрацией: он только передает фазы в `run_startup_phases()` и пишет прежний лог завершения.
- Добавлен тест порядка startup-фаз в `tests/infrastructure/storage/test_storage_sqlite.py`.
- Обновлена карта владения `docs/architecture/SQLITE_SCHEMA_SPLIT_MAP.md`.

## Сохранено

- SQLite schema behavior: сохранено.
- SQL semantics: сохранены; SQL-строки не менялись.
- `PRAGMA user_version`: переходы не менялись.
- Таблицы, колонки, индексы, миграции, backup tables и schema versions: не менялись.
- CLI, services, dataset/export behavior: не менялись.

## Проверки

- `python3 -m pytest tests/infrastructure/storage/test_storage_sqlite.py -q`: passed, 46 passed.
- `python3 -m pytest tests/infrastructure/storage/test_sqlite_schema_contract.py -q`: passed, 3 passed.
- `python3 -m compileall tg_msg_manager`: passed.
- `ruff check tg_msg_manager tests`: passed.
- `ruff format --check tg_msg_manager tests`: passed.
- `git diff --check`: passed.
- `make pre-commit`: passed; внутри выполнен `make verify`, 563 unittest passed.
- `make verify`: passed, 563 unittest passed.

## Skills

- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`
