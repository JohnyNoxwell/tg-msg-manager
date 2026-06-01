# Отчет Stage 5E.2 - SQLite Schema Split Regression Expansion

## Статус

Stage 5E.2 завершен.

## Регрессионные тесты

- Добавлен `TestSQLiteSchemaSplitHelpers.test_run_migrations_uses_extracted_callbacks_in_order_from_version_9`.
  - Проверяет извлеченный `schema/migrations.py::run_migrations`.
  - Фиксирует порядок callbacks для веток `user_version` 10-14.
  - Проверяет итоговый `PRAGMA user_version = 14`.
- Добавлен `TestSQLiteSchemaSplitHelpers.test_schema_mixin_keeps_stage2_methods_as_delegating_wrappers`.
  - Проверяет, что Stage 5E.1 methods в `SQLiteSchemaMixin` остались thin delegates.
  - Покрывает delegation для `migrations.py`, `compat.py`, `backfills.py` и transaction provider для `migrate_existing_links`.

## Регрессии extraction

- Regression fixes не потребовались.
- Runtime helpers не менялись.

## Измененные файлы

- `tests/infrastructure/storage/test_storage_sqlite.py`
- `docs/stages/reports/STAGE_5E_2_SQLITE_SCHEMA_SPLIT_REGRESSION_EXPANSION_REPORT.md`
- `docs/stages/README.md`
- `docs/stages/completed/stage_5e_2_sqlite_schema_split_regression_expansion.md`

## Проверки

- `python3 -m pytest tests/infrastructure/storage/test_storage_sqlite.py -q`: passed, 44 passed.
- `python3 -m pytest tests/architecture/test_architecture_wrappers.py -q`: passed, 8 passed, 4 subtests passed.
- `python3 -m compileall tg_msg_manager`: passed.
- `ruff check tg_msg_manager tests`: passed.
- `git diff --check`: passed.

## Сохранено

- SQLite schema behavior не менялся.
- `PRAGMA user_version` transitions не менялись.
- CLI не менялся.
- Services не менялись.
- Dataset behavior не менялся.
- Stage 5E.2 не запускал later stages.

## Очистка lifecycle

- Active task file перенесен в `docs/stages/completed/stage_5e_2_sqlite_schema_split_regression_expansion.md`.
- `docs/stages/README.md` обновлен.
- Later stages не запускались.

## Навыки

- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`
