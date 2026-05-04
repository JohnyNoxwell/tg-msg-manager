# Stage 0 SQLite Read Inventory

Date: 2026-05-04

Stage 0 split the former `_sqlite_read_path.py` monolith into grouped read modules while keeping the same `SQLiteStorage` public API.

## Private Helpers

| Method | New module | Responsibility | Known callers | Coverage |
| --- | --- | --- | --- | --- |
| `_chunked()` | `read/common.py` | chunk large `IN (...)` reads | `get_messages_by_ids()`, `filter_missing_target_links()` | `tests/test_storage_sqlite.py` |
| `_row_to_message()` | `read/common.py` | SQLite row -> `MessageData` coercion | all message-returning reads | `tests/test_storage_sqlite.py`, `tests/test_fixture_e2e.py` |

## Message Retrieval

| Method | New module | Responsibility | Known callers | Coverage |
| --- | --- | --- | --- | --- |
| `get_message()` | `read/messages.py` | single message fetch | context storage fallback, cleaner, tests | `tests/test_storage_sqlite.py`, `tests/test_services.py` |
| `message_exists()` | `read/messages.py` | existence check | cleaner/tests | `tests/test_storage_sqlite.py` |
| `get_last_msg_id()` | `read/messages.py` | sync-state headline read | storage tests | `tests/test_storage_sqlite.py` |
| `filter_existing_ids()` | `read/messages.py` | remove already stored IDs | storage tests / compatibility | `tests/test_storage_sqlite.py` |
| `get_message_count()` | `read/messages.py` | chat or target-linked count | cleaner/storage tests | `tests/test_storage_sqlite.py` |
| `get_all_message_ids_for_chat()` | `read/messages.py` | descending chat message IDs | storage tests | `tests/test_storage_sqlite.py` |
| `get_messages_in_id_range()` | `read/messages.py` | range hydration | `services/context/fetchers.py` | `tests/test_services.py` |
| `get_messages_by_ids()` | `read/messages.py` | batched ID hydration | `services/context/fetchers.py` | `tests/test_services.py`, `tests/test_storage_sqlite.py` |

## Target Retrieval

| Method | New module | Responsibility | Known callers | Coverage |
| --- | --- | --- | --- | --- |
| `get_sync_status()` | `read/targets.py` | tracked target sync state | `ExportService` | `tests/test_storage_sqlite.py`, `tests/test_sync_system.py` |
| `get_outdated_chats()` | `read/targets.py` | tracked refresh plan input | `ExportService.sync_all_outdated()` | `tests/test_sync_system.py` |
| `filter_missing_target_links()` | `read/targets.py` | target-link dedup | `services/sync/range_scanner.py` | `tests/test_storage_sqlite.py`, `tests/test_services.py` |
| `get_unique_sync_users()` | `read/targets.py` | unique users present in messages | storage compatibility | `tests/test_storage_sqlite.py` |
| `get_user()` | `read/targets.py` | stored user metadata | CLI/export/reporting paths | `tests/test_storage_sqlite.py`, `tests/test_db_exporter.py` |
| `get_primary_targets()` | `read/targets.py` | tracked target list with counts | CLI/update/menu flows | `tests/test_storage_sqlite.py`, `tests/test_sync_system.py` |
| `has_target_link()` | `read/targets.py` | target link existence | storage compatibility | `tests/test_storage_sqlite.py` |
| `get_target_message_breakdown()` | `read/targets.py` | own/context linked counts | sync finalization, fixtures | `tests/test_storage_sqlite.py`, `tests/test_fixture_e2e.py` |

## Context Retrieval

| Method | New module | Responsibility | Known callers | Coverage |
| --- | --- | --- | --- | --- |
| `get_messages_replying_to()` | `read/context.py` | child reply lookup | `services/context/fetchers.py` | `tests/test_services.py` |

Observation:

- no current read path uses `message_context_links` as an active source of truth;
- current context reconstruction relies on `reply_to_id`, `context_group_id`, `message_target_links`, and live/storage fetchers.

## Export Retrieval

| Method | New module | Responsibility | Known callers | Coverage |
| --- | --- | --- | --- | --- |
| `get_user_messages()` | `read/exports.py` | materialized linked messages | `DBExportService` fallback path | `tests/test_db_exporter.py`, `tests/test_storage_sqlite.py` |
| `get_user_export_summary()` | `read/exports.py` | fingerprint summary | `DBExportService` fast path | `tests/test_db_exporter.py`, `tests/test_storage_sqlite.py` |
| `iter_user_export_rows()` | `read/exports.py` | streaming export rows | `DBExportService` AI JSON fast path | `tests/test_db_exporter.py`, `tests/test_storage_sqlite.py` |
| `get_user_export_rows()` | `read/exports.py` | materialized export rows | `DBExportService` legacy fallback | `tests/test_db_exporter.py` |

## Reporting / Retry Reads

| Method | New module | Responsibility | Known callers | Coverage |
| --- | --- | --- | --- | --- |
| `get_report_database_summary()` | `read/reporting.py` | DB-level audit counters | `ReportCollector` | `tests/test_reporting.py` |
| `get_report_target_summaries()` | `read/reporting.py` | tracked target audit rows | `ReportCollector` | `tests/test_reporting.py` |
| `get_report_retry_summary()` | `read/reporting.py` | retry queue summary | `ReportCollector` | `tests/test_reporting.py` |
| `get_due_retry_tasks()` | `read/reporting.py` | ordered due retry fetch | `RetryWorker` | `tests/test_retry_worker.py`, `tests/test_storage_sqlite.py` |
| `get_retry_tasks()` | `read/reporting.py` | compatibility alias | storage compatibility | `tests/test_storage_sqlite.py` |
| `list_retry_tasks()` | `read/reporting.py` | inspection-oriented retry list | CLI/report/tests | `tests/test_retry_worker.py`, `tests/test_storage_sqlite.py`, `tests/test_fixture_e2e.py` |

## Compatibility Result

- `SQLiteStorage` still exposes the same public read methods.
- `_sqlite_read_path.py` is now an aggregator over focused mixins.
- No service call sites were renamed in Stage 0.
