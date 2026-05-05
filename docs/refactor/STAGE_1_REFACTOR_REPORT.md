# Stage 1 Refactor Report

## 1. Summary

Stage 1 completed the next architectural hardening pass after Stage 0 without changing the public CLI surface or export/archive formats.

Main outcomes:

- `DBExportService` is now a thin facade over dedicated `db_export` components
- PM archive orchestration now lives in `services/private_archive/` components instead of one large service file
- storage protocols are split into `infrastructure/storage/contracts/`
- service/event payloads are split into `core/models/payloads/`
- analytics now has an explicit read-only boundary
- context relation tables now have a documented status
- a live/manual smoke checklist was added

## 2. Baseline

- Commit before: `eb703a0dec15b579abd72d100f0a48f102ecc351`
- Commit after: `eb703a0dec15b579abd72d100f0a48f102ecc351` plus Stage 1 workspace changes
- Tests before: `make test` passed, `make verify` failed because of pre-existing lint/format debt
- Tests after: `make test` passed, `make verify` passed, fixture E2E passed

## 3. DBExportService split

| Old method/module | New module | Responsibility |
|---|---|---|
| `services/db_exporter.py` | `services/db_export/service.py` | facade orchestration |
| `_load_export_source`, `_load_incremental_export_source` | `services/db_export/source_loader.py` | DB export source loading |
| `_prepare_export_plan`, author resolution helpers | `services/db_export/plan_builder.py` | deterministic planning and filenames |
| `_db_skip_match`, `_legacy_manifest_skip_match`, `_maybe_skip_unchanged_export` | `services/db_export/skip_policy.py` | unchanged export detection |
| `_start_export_run`, `_finish_export_run`, target state helpers | `services/db_export/state_manager.py` | export state and run persistence |
| `_write_export_payloads`, `_cleanup_existing_export_files`, batch sizing | `services/db_export/payload_writer.py` | file-write orchestration |
| JSONL serialization helpers | `services/db_export/jsonl_renderer.py` | JSONL rendering |
| TXT formatting helpers | `services/db_export/txt_renderer.py` | TXT rendering |
| legacy manifest access | `services/db_export/manifest_writer.py` | compatibility manifest lookup |
| telemetry/logging side effects | `services/db_export/event_emitter.py` | DB export events/metrics |

## 4. PrivateArchiveService split

| Old method/module | New module | Responsibility |
|---|---|---|
| `services/private_archive.py` | `services/private_archive/service.py` | facade orchestration |
| `_prepare_archive_context`, folder naming | `services/private_archive/planner.py` | archive scope and output paths |
| user/entity field extraction | `services/private_archive/source_resolver.py` | source descriptor building |
| `_media_category`, media decisions | `services/private_archive/media_policy.py` | media policy |
| `_download_media` | `services/private_archive/media_downloader.py` | isolated media download delegation |
| `_archive_message`, `_archive_message_stream`, media progress flow | `services/private_archive/stream_processor.py` | message stream processing and progress emission |
| `_ensure_archive_dirs`, `_format_pm_log` | `services/private_archive/archive_writer.py` | archive file writing |
| `get_last_msg_id`, `register_target`, `update_last_sync_at` coordination | `services/private_archive/state_manager.py` | archive state/checkpoint flow |
| `_emit_event`, start/progress/complete payloads | `services/private_archive/event_emitter.py` | archive events |

## 5. Storage contracts

| Old interface area | New contract | Used by |
|---|---|---|
| umbrella service protocols in `interface.py` | `contracts/export_storage.py` | `ExportService` |
| umbrella service protocols in `interface.py` | `contracts/db_export_storage.py` | `DBExportService` |
| umbrella service protocols in `interface.py` | `contracts/private_archive_storage.py` | `PrivateArchiveService` |
| umbrella service protocols in `interface.py` | `contracts/context_storage.py` | `ContextEngine` |
| umbrella service protocols in `interface.py` | `contracts/retry_storage.py` | `RetryWorker` |
| umbrella service protocols in `interface.py` | `contracts/report_storage.py` | reporting read-side |
| shared protocol definitions | `contracts/common.py` | all service contracts |
| future analytics placeholder | `contracts/analytics_storage.py` | future read-only analytics only |

## 6. Payloads and boundaries

- `core/models/service_payloads.py` is now a compatibility aggregator.
- Active domain payload definitions live in:
  - `core/models/payloads/export.py`
  - `core/models/payloads/private_archive.py`
  - `core/models/payloads/cleaner.py`
- Placeholder domain modules were added for `sync`, `db_export`, `context`, `retry`, `report`, and `telemetry`.
- `message_context_links` is now explicitly documented as a legacy compatibility layer.
- `message_target_links`, `messages.reply_to_id`, and `messages.context_group_id` remain first-class relation sources.

## 7. Validation

- `make test` -> passed (`Ran 186 tests`)
- `make verify` -> passed
- `python3 -m unittest tests.test_fixture_e2e -q` -> passed (`Ran 4 tests`)
- import smoke for legacy and new module paths -> passed
- targeted component tests added for new `db_export` and `private_archive` components
