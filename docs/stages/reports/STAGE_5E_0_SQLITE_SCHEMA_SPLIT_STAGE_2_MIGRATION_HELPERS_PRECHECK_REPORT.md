# Отчет Stage 5E.0 - SQLite Schema Split Stage 2 Migration Helpers Precheck

## Статус

Stage 5E.0 завершен.

## Базовая проверка

- `python3 -m pytest tests/infrastructure/storage/test_storage_sqlite.py -q`: passed, 42 passed.
- `python3 -m pytest tests/architecture/test_architecture_wrappers.py -q`: passed, 8 passed, 4 subtests passed.

Обе проверки выполнены до изменения `docs/architecture/SQLITE_SCHEMA_SPLIT_MAP.md`.

## Измененные документы

- `docs/architecture/SQLITE_SCHEMA_SPLIT_MAP.md`
- `docs/stages/reports/STAGE_5E_0_SQLITE_SCHEMA_SPLIT_STAGE_2_MIGRATION_HELPERS_PRECHECK_REPORT.md`
- `docs/stages/README.md`
- `docs/stages/completed/stage_5e_0_sqlite_schema_split_stage_2_migration_helpers_precheck.md`

## Разрешенные методы для Stage 5E.1

- `_run_migrations` -> `schema/migrations.py::run_migrations`
- `_ensure_sync_target_columns` -> `schema/compat.py::ensure_sync_target_columns`
- `_ensure_export_target_columns` -> `schema/compat.py::ensure_export_target_columns`
- `_ensure_retry_queue_columns` -> `schema/compat.py::ensure_retry_queue_columns`
- `_migrate_message_context_links_to_chat_safe` -> `schema/compat.py::migrate_message_context_links_to_chat_safe`
- `_migrate_message_target_links_metadata` -> `schema/compat.py::migrate_message_target_links_metadata`
- `_resolve_legacy_context_link_chat_id` -> `schema/compat.py::resolve_legacy_context_link_chat_id`
- `_resolve_legacy_target_link_chat_id` -> `schema/compat.py::resolve_legacy_target_link_chat_id`
- `_migrate_sync_targets_to_composite_pk` -> `schema/compat.py::migrate_sync_targets_to_composite_pk`
- `migrate_existing_links` -> `schema/compat.py::migrate_existing_links`
- `_backfill_export_targets` -> `schema/backfills.py::backfill_export_targets`
- `_backfill_missing_reply_refs` -> `schema/backfills.py::backfill_missing_reply_refs`
- `_normalize_context_link_types` -> `schema/backfills.py::normalize_context_link_types`
- `_reclassify_target_link_types` -> `schema/backfills.py::reclassify_target_link_types`

## Разрешенные runtime-модули для Stage 5E.1

- `tg_msg_manager/infrastructure/storage/schema/migrations.py`
- `tg_msg_manager/infrastructure/storage/schema/compat.py`
- `tg_msg_manager/infrastructure/storage/schema/backfills.py`
- `tg_msg_manager/infrastructure/storage/schema/__init__.py`
- `tg_msg_manager/infrastructure/storage/_sqlite_schema.py`

## Инварианты для Stage 5E.1

- Порядок `_init_db` сохраняется: tables, user identity schema, export target columns, sync target columns, retry queue columns, indexes, migrations, commit.
- `SQLiteSchemaMixin` остается compatibility surface с тонкими delegating wrappers.
- `run_migrations` сохраняет исходную модель ветвления по начальному `current_version` и переходы `PRAGMA user_version` с 2 по 14.
- SQL text, table/index definitions, backup table names, exception strings, log strings и commit behavior не меняются.
- `migrate_sync_targets_to_composite_pk` сохраняет внутренний `conn.commit()` и cleanup-on-error behavior.
- `migrate_existing_links` сохраняет существующую границу `_write_transaction()` через переданный transaction provider.
- Извлеченные storage schema helpers не импортируют services, CLI, dataset modules и не инспектируют private SQLite contents.

## Сохранено

- Runtime code не менялся.
- CLI не менялся.
- Dataset format не менялся.
- SQLite behavior и schema не менялись.
- Stage 5E.1 не реализован.

## Финальная проверка

- `git diff --check`: passed.
- Проверка lifecycle files: passed.

## Очистка lifecycle

- Active task file перенесен в `docs/stages/completed/stage_5e_0_sqlite_schema_split_stage_2_migration_helpers_precheck.md`.
- `docs/stages/README.md` обновлен.
- Более поздние active Stage 5E files не переносились.

## Навыки

- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`
