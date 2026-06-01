# Отчет Stage 5E.1 - SQLite Schema Split Stage 2 Migration Helper Extraction

## Статус

Stage 5E.1 завершен.

## Делегированные функции

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

## Измененные файлы

- `tg_msg_manager/infrastructure/storage/schema/migrations.py`
- `tg_msg_manager/infrastructure/storage/schema/compat.py`
- `tg_msg_manager/infrastructure/storage/schema/backfills.py`
- `tg_msg_manager/infrastructure/storage/schema/__init__.py`
- `tg_msg_manager/infrastructure/storage/_sqlite_schema.py`
- `docs/architecture/SQLITE_SCHEMA_SPLIT_MAP.md`
- `docs/stages/reports/STAGE_5E_1_SQLITE_SCHEMA_SPLIT_STAGE_2_MIGRATION_HELPER_EXTRACTION_REPORT.md`
- `docs/stages/README.md`
- `docs/stages/completed/stage_5e_1_sqlite_schema_split_stage_2_migration_helper_extraction.md`

## Проверки

- Baseline до правок: `python3 -m pytest tests/infrastructure/storage/test_storage_sqlite.py -q`: passed, 42 passed.
- После правок: `python3 -m pytest tests/infrastructure/storage/test_storage_sqlite.py -q`: passed, 42 passed.
- `python3 -m pytest tests/architecture/test_architecture_wrappers.py -q`: passed, 8 passed, 4 subtests passed.
- `python3 -m compileall tg_msg_manager`: passed.
- `ruff check tg_msg_manager tests`: passed.
- `git diff --check`: passed.

## Подтверждения

- Порядок `_init_db` не менялся: tables, user identity schema, export target columns, sync target columns, retry queue columns, indexes, migrations, commit.
- Переходы `PRAGMA user_version` с 2 по 14 сохранены в extracted `run_migrations`.
- Имена методов `SQLiteSchemaMixin` сохранены как thin compatibility delegates.
- SQLite schema behavior, backup table names, exception strings, commit behavior и migration ordering сохранены.
- CLI, services и dataset behavior не менялись.
- Stage 5E.2 не реализован.

## Очистка lifecycle

- Active task file перенесен в `docs/stages/completed/stage_5e_1_sqlite_schema_split_stage_2_migration_helper_extraction.md`.
- `docs/stages/README.md` обновлен.
- Stage 5E.2 active file не переносился.

## Навыки

- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`
