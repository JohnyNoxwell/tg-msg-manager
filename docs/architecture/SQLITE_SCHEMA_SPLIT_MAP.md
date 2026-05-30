# SQLite Schema Split Map

Stage: 5B.5
Scope: documentation-only decomposition plan for `tg_msg_manager/infrastructure/storage/_sqlite_schema.py`.

This map records current responsibilities before any future split. It does not authorize schema behavior changes, migrations, index changes, table changes, or `PRAGMA user_version` changes.

## Current File

- `tg_msg_manager/infrastructure/storage/_sqlite_schema.py`
- Current mixin: `SQLiteSchemaMixin`
- Current caller: `tg_msg_manager/infrastructure/storage/sqlite.py::SQLiteStorage`
- Current tests with schema and migration coverage: `tests/infrastructure/storage/test_storage_sqlite.py`

## Current Responsibility Map

- `SQLiteSchemaMixin` (`20-1175`): schema initialization, compatibility migrations, migration backfills, schema inspection helpers, and legacy link population.
- `_init_db` (`21-35`): initialization sequence; creates base tables, applies compatibility column ensures, creates indexes, runs migrations, commits.
- `_create_tables` (`36-182`): base table creation for messages, users, chats, context links, target links, sync state, retry queue, sync targets, export targets, export runs, and missing reply refs.
- `_create_indexes` (`183-215`): top-level index creation and delegation to context link, target link, missing reply ref, and user identity indexes.
- `_ensure_sync_target_columns` (`216-229`): compatibility column additions for legacy `sync_targets` databases.
- `_ensure_export_target_columns` (`230-246`): compatibility column additions for legacy `export_targets` databases.
- `_ensure_retry_queue_columns` (`247-262`): compatibility column additions for legacy `retry_queue` databases.
- `_run_migrations` (`263-422`): ordered versioned migration coordinator from `user_version` 2 through 14.
- `_create_context_link_indexes` (`423-444`): context link index creation gated by chat-safe schema inspection.
- `_create_target_link_indexes` (`445-466`): target link index creation gated by chat-safe schema inspection.
- `_create_missing_reply_ref_indexes` (`467-480`): missing reply reference index creation.
- `_context_links_has_chat_scope` (`481-489`): schema inspection for chat-safe context link columns.
- `_target_links_has_chat_scope` (`490-498`): schema inspection for chat-safe target link columns.
- `_target_links_has_metadata` (`499-509`): schema inspection for target link metadata columns.
- `_migrate_message_context_links_to_chat_safe` (`510-657`): compatibility migration helper for legacy context link rows and backup table creation.
- `_normalize_context_link_types` (`658-695`): migration data normalization for context link type and algorithm values.
- `_migrate_message_target_links_metadata` (`696-828`): compatibility migration helper for target link metadata and backup table creation.
- `_reclassify_target_link_types` (`829-865`): migration data reclassification for target link semantics.
- `_resolve_legacy_context_link_chat_id` (`866-901`): legacy context link chat resolution helper.
- `_resolve_legacy_target_link_chat_id` (`902-932`): legacy target link chat resolution helper.
- `_table_exists` (`933-943`): schema inspection helper.
- `_backfill_export_targets` (`944-978`): export target state backfill from sync targets and users.
- `_create_export_runs_table` (`979-996`): export runs table creation used by migrations and base schema setup.
- `_create_export_runs_indexes` (`997-1010`): export runs index creation used by migrations and base schema setup.
- `_create_missing_reply_refs_table` (`1011-1024`): missing reply refs table creation used by migrations and base schema setup.
- `_backfill_missing_reply_refs` (`1025-1051`): missing reply refs backfill from orphan reply relationships.
- `_migrate_sync_targets_to_composite_pk` (`1052-1098`): compatibility migration helper for composite primary key conversion.
- `_sync_targets_has_composite_primary_key` (`1099-1110`): schema inspection helper for `sync_targets` primary key shape.
- `migrate_existing_links` (`1111-1175`): compatibility migration helper that populates `message_target_links` for existing messages.

## Future Module Boundaries

Keep `SQLiteSchemaMixin` as the compatibility import surface during a split-only stage. It should contain only delegation and initialization ordering after the split.

- `tg_msg_manager/infrastructure/storage/schema/tables.py`
  - Category: table creation.
  - Owns future extraction of `_create_tables`, `_create_export_runs_table`, and `_create_missing_reply_refs_table`.

- `tg_msg_manager/infrastructure/storage/schema/indexes.py`
  - Category: index creation.
  - Owns future extraction of `_create_indexes`, `_create_context_link_indexes`, `_create_target_link_indexes`, `_create_missing_reply_ref_indexes`, and `_create_export_runs_indexes`.

- `tg_msg_manager/infrastructure/storage/schema/migrations.py`
  - Category: versioned migrations.
  - Owns future extraction of `_run_migrations` and preserves the exact migration sequence.

- `tg_msg_manager/infrastructure/storage/schema/compat.py`
  - Category: compatibility migration helpers.
  - Owns future extraction of `_ensure_sync_target_columns`, `_ensure_export_target_columns`, `_ensure_retry_queue_columns`, `_migrate_message_context_links_to_chat_safe`, `_migrate_message_target_links_metadata`, `_migrate_sync_targets_to_composite_pk`, `_resolve_legacy_context_link_chat_id`, `_resolve_legacy_target_link_chat_id`, and `migrate_existing_links`.

- `tg_msg_manager/infrastructure/storage/schema/backfills.py`
  - Category: backfills.
  - Owns future extraction of `_backfill_export_targets`, `_backfill_missing_reply_refs`, `_normalize_context_link_types`, and `_reclassify_target_link_types`.

- `tg_msg_manager/infrastructure/storage/schema/inspection.py`
  - Category: schema inspection helpers.
  - Owns future extraction of `_context_links_has_chat_scope`, `_target_links_has_chat_scope`, `_target_links_has_metadata`, `_table_exists`, and `_sync_targets_has_composite_primary_key`.

## Split-Only Constraints

- A future schema split stage must preserve current schema behavior exactly.
- Table SQL, index SQL, migration SQL, data backfills, backup table names, and exception behavior must remain identical unless a later explicit migration stage scopes a behavior change.
- `_init_db` ordering must remain identical:
  - `_create_tables`
  - `_ensure_user_identity_schema`
  - `_ensure_export_target_columns`
  - `_ensure_sync_target_columns`
  - `_ensure_retry_queue_columns`
  - `_create_indexes`
  - `_run_migrations`
  - `commit`
- `_run_migrations` must preserve migration checks and execution order from `user_version` 2 through 14.
- `PRAGMA user_version` transitions must remain identical for every migration branch.
- Future split modules must stay under `tg_msg_manager/infrastructure/storage/`.
- Storage code must not import `tg_msg_manager.services.*` or CLI modules.
- Core/domain code must not import infrastructure modules as part of a schema split.
- SQLite schema changes, migrations, new tables, new indexes, and new columns require a separate explicit stage.
- Existing storage tests remain the regression anchor for any later mechanical split.

## Adjacent Storage Structure

- Current write-path split modules live under `tg_msg_manager/infrastructure/storage/write/`.
- Current read-path split modules live under `tg_msg_manager/infrastructure/storage/read/`.
- `sqlite.py` composes `SQLiteSchemaMixin`, identity, write-path, read-path, sync-state, and `BaseStorage`.
- Any future schema package should follow the existing storage direction: focused infrastructure modules, no service imports, and no business logic in compatibility aggregators.
