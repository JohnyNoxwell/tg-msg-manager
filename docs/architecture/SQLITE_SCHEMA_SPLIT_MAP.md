# SQLite Schema Split Map

Stage: 5B.5 plan; Stage 5D.0 Stage 1 split applied; Stage 5E.1 Stage 2 migration helper extraction applied.
Scope: decomposition map for `tg_msg_manager/infrastructure/storage/_sqlite_schema.py` and the schema helper package.

This map records current responsibilities after the Stage 5E.1 mechanical extraction. It does not authorize schema behavior changes, migrations, index changes, table changes, or `PRAGMA user_version` changes.

## Current File

- `tg_msg_manager/infrastructure/storage/_sqlite_schema.py`
- `tg_msg_manager/infrastructure/storage/schema/tables.py`
- `tg_msg_manager/infrastructure/storage/schema/indexes.py`
- `tg_msg_manager/infrastructure/storage/schema/inspection.py`
- `tg_msg_manager/infrastructure/storage/schema/migrations.py`
- `tg_msg_manager/infrastructure/storage/schema/compat.py`
- `tg_msg_manager/infrastructure/storage/schema/backfills.py`
- Current mixin: `SQLiteSchemaMixin`
- Current caller: `tg_msg_manager/infrastructure/storage/sqlite.py::SQLiteStorage`
- Current tests with schema and migration coverage: `tests/infrastructure/storage/test_storage_sqlite.py`

## Current Responsibility Map

- `SQLiteSchemaMixin` (`37-180`): schema initialization and thin compatibility delegation surface.
- `_init_db` (`38-52`): initialization sequence; creates base tables, applies compatibility column ensures, creates indexes, runs migrations, commits.
- `_create_tables` (`53-54`): delegates base table creation to `schema/tables.py`.
- `_create_indexes` (`56-57`): delegates top-level index creation to `schema/indexes.py` while preserving user identity index callback order.
- `_ensure_sync_target_columns` (`59-60`): delegates legacy `sync_targets` compatibility columns to `schema/compat.py`.
- `_ensure_export_target_columns` (`62-63`): delegates legacy `export_targets` artifact metadata columns to `schema/compat.py`.
- `_ensure_retry_queue_columns` (`65-66`): delegates legacy `retry_queue` lifecycle columns to `schema/compat.py`.
- `_run_migrations` (`68-97`): delegates ordered migration coordination to `schema/migrations.py`.
- `_create_context_link_indexes` (`99-100`): delegates to `schema/indexes.py`.
- `_create_target_link_indexes` (`102-103`): delegates to `schema/indexes.py`.
- `_create_missing_reply_ref_indexes` (`105-106`): delegates to `schema/indexes.py`.
- `_context_links_has_chat_scope` (`108-109`): delegates to `schema/inspection.py`.
- `_target_links_has_chat_scope` (`111-112`): delegates to `schema/inspection.py`.
- `_target_links_has_metadata` (`114-115`): delegates to `schema/inspection.py`.
- `_migrate_message_context_links_to_chat_safe` (`117-118`): delegates legacy context link rewrite to `schema/compat.py`.
- `_normalize_context_link_types` (`120-121`): delegates context link normalization to `schema/backfills.py`.
- `_migrate_message_target_links_metadata` (`123-124`): delegates legacy target link rewrite to `schema/compat.py`.
- `_reclassify_target_link_types` (`126-127`): delegates target link reclassification to `schema/backfills.py`.
- `_resolve_legacy_context_link_chat_id` (`129-140`): delegates legacy context link chat resolution to `schema/compat.py`.
- `_resolve_legacy_target_link_chat_id` (`142-148`): delegates legacy target link chat resolution to `schema/compat.py`.
- `_table_exists` (`150-151`): delegates to `schema/inspection.py`.
- `_backfill_export_targets` (`153-154`): delegates export target state backfill to `schema/backfills.py`.
- `_create_export_runs_table` (`156-157`): delegates to `schema/tables.py`.
- `_create_export_runs_indexes` (`159-160`): delegates to `schema/indexes.py`.
- `_create_missing_reply_refs_table` (`162-163`): delegates to `schema/tables.py`.
- `_backfill_missing_reply_refs` (`165-166`): delegates missing reply refs backfill to `schema/backfills.py`.
- `_migrate_sync_targets_to_composite_pk` (`168-170`): delegates composite primary key conversion to `schema/compat.py`.
- `_sync_targets_has_composite_primary_key` (`172-174`): delegates to `schema/inspection.py`.
- `migrate_existing_links` (`176-180`): delegates legacy target link population to `schema/compat.py`.
- `schema/tables.py`: extracted Stage 1 table creation for base tables, `export_runs`, and `missing_reply_refs`.
- `schema/indexes.py`: extracted Stage 1 index creation for top-level, context link, target link, missing reply ref, and export run indexes.
- `schema/inspection.py`: extracted Stage 1 schema inspection helpers.
- `schema/migrations.py`: extracted Stage 2 migration coordinator for `PRAGMA user_version` 2 through 14.
- `schema/compat.py`: extracted Stage 2 compatibility column ensures, legacy table rewrite helpers, legacy chat-id resolution helpers, composite primary key migration, and legacy target-link population.
- `schema/backfills.py`: extracted Stage 2 data backfills and normalization/reclassification helpers.

## Stage 5E.0 Precheck Inventory

Baseline verification before this docs update:

- `python3 -m pytest tests/infrastructure/storage/test_storage_sqlite.py -q`: passed, 42 passed.
- `python3 -m pytest tests/architecture/test_architecture_wrappers.py -q`: passed, 8 passed, 4 subtests passed.

Remaining non-Stage-1 logic in `SQLiteSchemaMixin` is limited to initialization orchestration, compatibility column ensures, versioned migration coordination, migration/backfill helpers, and thin wrappers around already extracted schema helpers.

Current migration, compatibility, and backfill methods still owned by `SQLiteSchemaMixin`:

- `_ensure_sync_target_columns(conn)`: legacy `sync_targets` compatibility columns.
- `_ensure_export_target_columns(conn)`: legacy `export_targets` artifact metadata columns.
- `_ensure_retry_queue_columns(conn)`: legacy `retry_queue` lifecycle columns.
- `_run_migrations(conn)`: migration coordinator for `PRAGMA user_version` 2 through 14.
- `_migrate_message_context_links_to_chat_safe(conn)`: legacy context link table rewrite and backup handling.
- `_normalize_context_link_types(conn)`: context link type and algorithm normalization.
- `_migrate_message_target_links_metadata(conn)`: legacy target link metadata rewrite and backup handling.
- `_reclassify_target_link_types(conn)`: target link semantic reclassification.
- `_resolve_legacy_context_link_chat_id(conn, *, message_id, context_message_id)`: currently unused legacy resolution helper.
- `_resolve_legacy_target_link_chat_id(conn, *, message_id)`: currently unused legacy resolution helper.
- `_backfill_export_targets(conn)`: export target state backfill.
- `_backfill_missing_reply_refs(conn)`: missing reply refs backfill.
- `_migrate_sync_targets_to_composite_pk()`: legacy `sync_targets` primary key rewrite with existing commit behavior.
- `migrate_existing_links()`: legacy target link population through `_write_transaction()`.

## Stage 5E.1 Extraction Plan

Stage 5E.1 moved only the following methods, preserving SQL semantics, backup table names, exception messages, logging strings, `PRAGMA user_version` assignments, and commit behavior:

- `_run_migrations` -> `schema/migrations.py::run_migrations`.
- `_ensure_sync_target_columns` -> `schema/compat.py::ensure_sync_target_columns`.
- `_ensure_export_target_columns` -> `schema/compat.py::ensure_export_target_columns`.
- `_ensure_retry_queue_columns` -> `schema/compat.py::ensure_retry_queue_columns`.
- `_migrate_message_context_links_to_chat_safe` -> `schema/compat.py::migrate_message_context_links_to_chat_safe`.
- `_migrate_message_target_links_metadata` -> `schema/compat.py::migrate_message_target_links_metadata`.
- `_resolve_legacy_context_link_chat_id` -> `schema/compat.py::resolve_legacy_context_link_chat_id`.
- `_resolve_legacy_target_link_chat_id` -> `schema/compat.py::resolve_legacy_target_link_chat_id`.
- `_migrate_sync_targets_to_composite_pk` -> `schema/compat.py::migrate_sync_targets_to_composite_pk`.
- `migrate_existing_links` -> `schema/compat.py::migrate_existing_links`.
- `_backfill_export_targets` -> `schema/backfills.py::backfill_export_targets`.
- `_backfill_missing_reply_refs` -> `schema/backfills.py::backfill_missing_reply_refs`.
- `_normalize_context_link_types` -> `schema/backfills.py::normalize_context_link_types`.
- `_reclassify_target_link_types` -> `schema/backfills.py::reclassify_target_link_types`.

Stage 5E.1 created or changed only these runtime modules for extraction:

- `tg_msg_manager/infrastructure/storage/schema/migrations.py`
- `tg_msg_manager/infrastructure/storage/schema/compat.py`
- `tg_msg_manager/infrastructure/storage/schema/backfills.py`
- `tg_msg_manager/infrastructure/storage/schema/__init__.py`
- `tg_msg_manager/infrastructure/storage/_sqlite_schema.py`

Stage 5E.1 kept `SQLiteSchemaMixin` as the compatibility surface. The mixin methods listed above remain thin delegating wrappers.

Allowed extracted helper signatures:

- `run_migrations(conn: sqlite3.Connection, *, migrate_existing_links, sync_targets_has_composite_primary_key, migrate_sync_targets_to_composite_pk, ensure_user_identity_schema, create_user_identity_indexes, backfill_user_identity_state, migrate_message_context_links_to_chat_safe, migrate_message_target_links_metadata, backfill_export_targets, create_export_runs_table, create_export_runs_indexes, create_missing_reply_refs_table, create_missing_reply_ref_indexes, backfill_missing_reply_refs, normalize_context_link_types, create_context_link_indexes, reclassify_target_link_types, ensure_export_target_columns) -> None`
- `ensure_sync_target_columns(conn: sqlite3.Connection) -> None`
- `ensure_export_target_columns(conn: sqlite3.Connection) -> None`
- `ensure_retry_queue_columns(conn: sqlite3.Connection) -> None`
- `migrate_message_context_links_to_chat_safe(conn: sqlite3.Connection) -> None`
- `migrate_message_target_links_metadata(conn: sqlite3.Connection) -> None`
- `resolve_legacy_context_link_chat_id(conn: sqlite3.Connection, *, message_id: int, context_message_id: int) -> int`
- `resolve_legacy_target_link_chat_id(conn: sqlite3.Connection, *, message_id: int) -> int`
- `migrate_sync_targets_to_composite_pk(conn: sqlite3.Connection) -> None`
- `migrate_existing_links(write_transaction) -> None`
- `backfill_export_targets(conn: sqlite3.Connection) -> None`
- `backfill_missing_reply_refs(conn: sqlite3.Connection) -> None`
- `normalize_context_link_types(conn: sqlite3.Connection) -> None`
- `reclassify_target_link_types(conn: sqlite3.Connection) -> None`

Delegation rules for Stage 5E.1:

- `_init_db` ordering must remain unchanged.
- `_run_migrations` wrapper must delegate once to `schema/migrations.py::run_migrations` with callbacks; it must not inline new migration logic.
- Extracted `run_migrations` must use the initial `current_version` exactly as today and must not recompute it between migration branches.
- `migrate_sync_targets_to_composite_pk` must preserve the internal `conn.commit()` and cleanup-on-error behavior.
- `migrate_existing_links` must receive the existing write transaction provider and preserve the transaction boundary.
- Extracted compatibility/backfill helpers may import sibling `schema` inspection/index helpers and storage link type constants only; they must not import services, CLI, or dataset modules.
- `schema/__init__.py` may re-export new helper names only for storage schema delegation.
- No Stage 5E.1 change may alter table SQL, index SQL, migration SQL, backup table names, exception strings, log strings, `PRAGMA user_version`, storage interfaces, CLI behavior, dataset format, or private SQLite database contents.

## Future Module Boundaries

Keep `SQLiteSchemaMixin` as the compatibility import surface during a split-only stage. It should contain only delegation and initialization ordering after the split.

- `tg_msg_manager/infrastructure/storage/schema/tables.py` (Stage 5D.0 complete)
  - Category: table creation.
  - Owns extracted `create_tables`, `create_export_runs_table`, and `create_missing_reply_refs_table`.

- `tg_msg_manager/infrastructure/storage/schema/indexes.py` (Stage 5D.0 complete)
  - Category: index creation.
  - Owns extracted `create_indexes`, `create_context_link_indexes`, `create_target_link_indexes`, `create_missing_reply_ref_indexes`, and `create_export_runs_indexes`.

- `tg_msg_manager/infrastructure/storage/schema/migrations.py` (Stage 5E.1 complete)
  - Category: versioned migrations.
  - Owns extracted `run_migrations` and preserves the exact migration sequence.

- `tg_msg_manager/infrastructure/storage/schema/compat.py` (Stage 5E.1 complete)
  - Category: compatibility migration helpers.
  - Owns extracted `ensure_sync_target_columns`, `ensure_export_target_columns`, `ensure_retry_queue_columns`, `migrate_message_context_links_to_chat_safe`, `migrate_message_target_links_metadata`, `migrate_sync_targets_to_composite_pk`, `resolve_legacy_context_link_chat_id`, `resolve_legacy_target_link_chat_id`, and `migrate_existing_links`.

- `tg_msg_manager/infrastructure/storage/schema/backfills.py` (Stage 5E.1 complete)
  - Category: backfills.
  - Owns extracted `backfill_export_targets`, `backfill_missing_reply_refs`, `normalize_context_link_types`, and `reclassify_target_link_types`.

- `tg_msg_manager/infrastructure/storage/schema/inspection.py` (Stage 5D.0 complete)
  - Category: schema inspection helpers.
  - Owns extracted `context_links_has_chat_scope`, `target_links_has_chat_scope`, `target_links_has_metadata`, `table_exists`, and `sync_targets_has_composite_primary_key`.

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
