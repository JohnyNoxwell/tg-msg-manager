# Storage Contract Split Map

| Method / area | Used by | Domain | New contract | Can be private | Notes |
|---|---|---|---|---|---|
| `start/flush/close` | runtime, export flows | shared/common | `contracts/common.py::StorageLifecycle` | no | lifecycle boundary remains shared |
| `request_stop/should_stop` | export sync loops | shared/common | `contracts/common.py::StopAwareStorage` | no | cooperative shutdown only |
| `save_message/save_messages` | sync, export, context, private archive | shared/common | `contracts/common.py::MessageWriteStorage` | no | write path stays infrastructure-only |
| `get_message/message_exists/get_last_msg_id/get_message_count/get_all_message_ids_for_chat` | cleaner, export, context, archive | shared/common | `contracts/common.py::MessageReadStorage` | no | base read primitives |
| `get_unique_sync_users/get_user/get_user_identity_history/get_user_messages` | export, db export, report | shared/common | `contracts/common.py::UserReadStorage` | no | still grouped for read-side callers |
| `get_user_export_summary* / iter_user_export_rows* / get_user_export_rows* / get_export_target / list_export_runs` | db export, report | db_export | `contracts/db_export_storage.py::DBExportStorage` via `UserReadStorage` | no | DB export-specific projections and state |
| `has_target_link/get_target_message_breakdown` | export sync, reporting | export/shared | `contracts/common.py::TargetLinkReadStorage` | no | target-link semantics preserved |
| `register_target/get_primary_targets/upsert_user/upsert_chat` | sync, private archive, export | shared/common | `contracts/common.py::TargetRegistryStorage` | no | registry remains shared but explicit |
| `get_sync_status/get_outdated_chats/update_sync_tail/update_last_msg_id/update_last_sync_at` | sync/export/archive | sync | `contracts/common.py::SyncStateStorage` and `contracts/sync_storage.py::SyncStorage` | no | sync checkpoint/state only |
| `delete_messages/delete_user_data` | cleaner, delete flow | cleaner | `contracts/common.py::CleanupStorage` and `contracts/cleaner_storage.py::CleanerStorage` | no | destructive operations isolated from other services |
| `ContextStorage` aggregate | context engine | context | `contracts/context_storage.py::ContextStorage` | no | keeps reply stitching narrow |
| `DBExportStorage` aggregate | `DBExportService` | db_export | `contracts/db_export_storage.py::DBExportStorage` | no | now imported directly by new DB export facade |
| `PrivateArchiveStorage` aggregate | `PrivateArchiveService` | private_archive | `contracts/private_archive_storage.py::PrivateArchiveStorage` | no | archive service no longer depends on umbrella interface |
| `ExportStorage` aggregate | `ExportService` | export | `contracts/export_storage.py::ExportStorage` | no | orchestrator depends on export-use-case contract only |
| `RetryStorage` aggregate | retry worker | retry | `contracts/retry_storage.py::RetryStorage` | no | retry state fully isolated |
| `ReportStorage` aggregate | reporting service | report | `contracts/report_storage.py::ReportStorage` | no | read-only audit contract |
| `AnalyticsStorage` placeholder | future analytics only | analytics | `contracts/analytics_storage.py::AnalyticsStorage` | n/a | reserved read-only boundary |
| `BaseStorage` umbrella ABC | SQLite implementation compatibility | legacy/shared | `infrastructure/storage/interface.py::BaseStorage` | no | retained as compatibility umbrella only |
