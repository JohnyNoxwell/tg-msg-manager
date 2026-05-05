# Legacy Inventory

Last reviewed: 2026-05-05

## Scripts

| Path | Status | Current use | Can remove now | Replacement / note |
| --- | --- | --- | --- | --- |
| `scripts/db_diagnostics.py` | active | schema/data diagnostics | no | baseline and smoke support |
| `scripts/cleanup_exports.py` | manual tool | one-off export cleanup | no | keep as operator utility |
| `scripts/export_user_context_from_db.py` | manual tool | ad-hoc local export inspection | no | DB export flow is primary supported path |
| `scripts/reset_and_seed_targets.py` | manual tool | local/dev target seeding | no | test/dev helper |

## Compatibility Paths

| Path | Status | Why retained | Replacement | Planned removal |
| --- | --- | --- | --- | --- |
| `tg_msg_manager/services/exporter.py` | compatibility | imported by tests/CLI/runtime | `tg_msg_manager/services/export/service.py` | next cleanup stage |
| `tg_msg_manager/services/context_engine.py` | compatibility | imported by tests/services | `tg_msg_manager/services/context/engine.py` | next cleanup stage |
| `tg_msg_manager/infrastructure/storage/_sqlite_write_path.py` | compatibility | storage mixin surface kept stable | `tg_msg_manager/infrastructure/storage/write/` | next cleanup stage |
| `tg_msg_manager/infrastructure/storage/_sqlite_sync_state.py` | compatibility | storage public API preserved | `tg_msg_manager/infrastructure/storage/write/` | next cleanup stage |
| `tg_msg_manager/infrastructure/storage/_sqlite_read_path.py` | compatibility | grouped read-side import surface | `tg_msg_manager/infrastructure/storage/read/` | remove only after import audit |
