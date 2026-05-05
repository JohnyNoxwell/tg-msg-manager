# Stage 0 Refactor Report

## 1. Summary

Stage 0 finished with compatibility-preserving module extraction around three hot paths:

- `services/exporter.py` became a compatibility wrapper over `services/export/service.py`
- `services/context_engine.py` became a compatibility wrapper over `services/context/engine.py`
- SQLite write responsibilities were split into `infrastructure/storage/write/` while old mixins stayed as stable wrappers

`ExportService` and `DeepModeEngine` were also thinned into facades over dedicated `export/` and `context/` modules. CLI names, argument names, defaults, DB export format, and test-visible behavior were preserved.

## 2. Files Changed

| File | Change type | Reason |
| --- | --- | --- |
| `tg_msg_manager/services/exporter.py` | wrapper | stop hot-path growth |
| `tg_msg_manager/services/export/service.py` | thin facade | dedicated export namespace |
| `tg_msg_manager/services/export/chat_sync.py` | new module | chat-level sync orchestration |
| `tg_msg_manager/services/export/dialog_sync.py` | new module | bulk dialog sync orchestration |
| `tg_msg_manager/services/export/*.py` | new modules | planner/event/checkpoint/fetch/target boundaries |
| `tg_msg_manager/services/context_engine.py` | wrapper | stop hot-path growth |
| `tg_msg_manager/services/context/engine.py` | thin facade | dedicated context namespace |
| `tg_msg_manager/services/context/rounds.py` | new module | batch-round context orchestration |
| `tg_msg_manager/services/context/{cluster_builder,deduplicator,neighbor_window_resolver,reply_chain_resolver,scope_policy}.py` | new modules | explicit context strategy boundaries |
| `tg_msg_manager/infrastructure/storage/sqlite.py` | updated | connection/transaction coordinator wiring |
| `tg_msg_manager/infrastructure/storage/_sqlite_write_path.py` | compatibility split | delegate to writer modules |
| `tg_msg_manager/infrastructure/storage/_sqlite_sync_state.py` | compatibility split | delegate state/export/retry writes |
| `tg_msg_manager/infrastructure/storage/write/*.py` | new modules | write-side responsibility split |
| `tg_msg_manager/infrastructure/storage/read/analytics/__init__.py` | new namespace | future analytics boundary |
| `tests/test_cli.py` | updated tests | CLI contract guardrail |
| `docs/refactor/*.md`, `docs/ARCHITECTURE_RULES.md`, `docs/PR_CHECKLIST.md`, `PROJECT_ARCHITECTURE_OVERVIEW.md` | docs | architecture/reporting guardrails |

## 3. Extracted Modules

| Old location | New module | Responsibility |
| --- | --- | --- |
| `services/exporter.py` | `services/export/service.py` | sync orchestration implementation |
| `services/export/service.py` | `services/export/chat_sync.py` | chat sync orchestration |
| `services/export/service.py` | `services/export/dialog_sync.py` | dialog sync orchestration |
| `services/context_engine.py` | `services/context/engine.py` | deep-context implementation |
| `services/context/engine.py` | `services/context/rounds.py` | multi-round batch extraction |
| `_sqlite_write_path.py` | `storage/write/message_writer.py` | message upsert/delete |
| `_sqlite_write_path.py` | `storage/write/target_link_writer.py` | target link writes |
| `_sqlite_write_path.py` | `storage/write/context_writer.py` | context/missing-reply writes |
| `_sqlite_sync_state.py` | `storage/write/checkpoint_writer.py` | sync checkpoints |
| `_sqlite_sync_state.py` | `storage/write/user_writer.py` | users/chats/targets |
| `_sqlite_sync_state.py` | `storage/write/report_writer.py` | export target + export run journal |
| `_sqlite_sync_state.py` | `storage/write/retry_writer.py` | retry queue lifecycle |

## 4. Behavior Compatibility

- CLI changed: no
- Export format changed: no
- DB schema changed: no new schema change in this refactor batch
- Tests passed: yes

## 5. Test Results

- `python3 -m unittest discover -s tests -q` -> `Ran 178 tests in 23.548s`, `OK`
- `python3 -m unittest tests.test_services tests.test_sync_system tests.test_cli tests.test_storage_sqlite -q` -> `Ran 111 tests in 17.569s`, `OK`
- `python3 -m unittest tests.test_fixture_e2e -q` -> `Ran 4 tests`, `OK`
- `python3 -m unittest tests.test_storage_sqlite -q` -> `Ran 39 tests`, `OK`
- `python3 -m unittest tests.test_db_exporter -q` -> `Ran 17 tests`, `OK`
- `python3 -m unittest tests.test_cli -q` -> `Ran 18 tests`, `OK`

## 6. Known Risks

- `_sqlite_write_path.py` and `_sqlite_sync_state.py` remain compatibility layers until imports are cleaned up in a later stage.
- `services/db_exporter.py` and `services/private_archive.py` remain outside this Stage 0 split and are the main remaining large service files.

## 7. Deferred Tasks

- compatibility wrappers were intentionally retained instead of removed
- analytics implementation was not added; only the boundary package was created

## 8. Next Recommended Stage

- migrate direct imports to the new `services/export/`, `services/context/`, and `storage/write/` modules
- continue with read-side analytics only after dedicated product requirements exist
- treat `db_exporter.py` and `private_archive.py` as the next refactor candidates if another architecture-hardening pass is planned
