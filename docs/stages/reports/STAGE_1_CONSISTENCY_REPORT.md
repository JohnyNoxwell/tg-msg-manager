# Stage 1 Consistency Report

## 1. Summary

Stage 1 consistency pass closed the remaining post-refactor drift without changing CLI surface, export formats, archive layout, or schema.

Closed issues:

- stale internal imports were moved to the new DB export package entrypoint
- narrow private-archive storage contract usage was completed
- remaining PM archive stream/media operational logic was extracted from the facade
- compatibility import coverage was added for DB export, private archive, and payload aggregators
- Stage 1 audit/baseline/report documentation was brought in line with the actual code

## 2. Baseline

- Commit: `31b78b342fe8129149dcd13dfa434eb352558640`
- Branch: `main`
- Tests before: `make test` passed, `make verify` passed, `compileall` passed, import smoke passed
- Known issues before:
  - stale internal wrapper imports remained
  - `PrivateArchiveService` still contained stream/media operational logic
  - compatibility import checks were missing
  - consistency-pass audit documents were missing

## 3. Duplicate implementation audit

### DBExportService

- Active implementation: `tg_msg_manager/services/db_export/service.py`
- Compatibility wrapper: `tg_msg_manager/services/db_exporter.py`
- Public package entrypoint: `tg_msg_manager/services/db_export/__init__.py`
- Fixed issues:
  - migrated CLI/runtime/internal helper imports to `tg_msg_manager.services.db_export`
  - preserved old import path through a pure wrapper
  - added compatibility import regression coverage

### PrivateArchiveService

- Active implementation: `tg_msg_manager/services/private_archive/service.py`
- Compatibility wrapper file: `tg_msg_manager/services/private_archive.py`
- Public package entrypoint: `tg_msg_manager/services/private_archive/__init__.py`
- Fixed issues:
  - verified actual import resolution points to the package, not the shadow file
  - kept public package import stable for CLI/runtime/tests
  - extracted stream/media operational logic out of the facade

## 4. Import compatibility

| Import path | Status |
|---|---|
| `tg_msg_manager.services.db_export.service.DBExportService` | active implementation |
| `tg_msg_manager.services.db_export.DBExportService` | active package re-export |
| `tg_msg_manager.services.db_exporter.DBExportService` | compatibility wrapper, verified |
| `tg_msg_manager.services.private_archive.service.PrivateArchiveService` | active implementation |
| `tg_msg_manager.services.private_archive.PrivateArchiveService` | active package re-export, verified |
| `tg_msg_manager.core.models.service_payloads.*` | compatibility aggregator, verified |
| `tg_msg_manager.infrastructure.storage.interface.*` | compatibility aggregator, retained for legacy/tests |

## 5. Storage contracts

What was verified:

- `DBExportService`, `PrivateArchiveService`, `ExportService`, and `ContextEngine` use narrow service contracts from `infrastructure/storage/contracts/`
- the remaining service-layer import from `infrastructure.storage.interface` was removed from `services/private_archive/state_manager.py`
- `infrastructure/storage/interface.py` remains an aggregator, not an active dumping ground

What remains:

- `tests/test_storage_sqlite.py` still imports the compatibility aggregator intentionally

## 6. Payload compatibility

What was verified:

- primary payload definitions live in `core/models/payloads/`
- `core/models/service_payloads.py` is a compatibility aggregator only
- compatibility identity tests now confirm old and new payload imports resolve to the same objects

What remains:

- a few tests still exercise the compatibility import path intentionally

## 7. Private archive facade

Extracted from `services/private_archive/service.py` during the pass:

- `media_downloader.py` for isolated Telegram media download delegation
- `stream_processor.py` for message-loop processing, per-message archive flow, and progress emission

Left in the facade intentionally:

- dependency assembly
- archive scope planning
- state transitions
- top-level start/completion event orchestration

## 8. Context relation tables decision

- Existing decision document: `docs/refactor/CONTEXT_RELATION_TABLES_DECISION.md`
- Current status:
  - `message_context_links`: legacy compatibility layer
  - `messages.context_group_id`: first-class grouping signal
  - `messages.reply_to_id` and `message_target_links`: first-class hot-path relations

## 9. Documentation updates

Updated:

- `PROJECT_ARCHITECTURE_OVERVIEW.md`
- `docs/ARCHITECTURE_RULES.md`
- `docs/PR_CHECKLIST.md`
- `CHANGELOG.md`
- `docs/testing/LIVE_SMOKE_CHECKLIST.md`
- `docs/refactor/STAGE_1_REFACTOR_REPORT.md`

Added:

- `docs/refactor/STAGE_1_CONSISTENCY_BASELINE.md`
- `docs/refactor/DB_EXPORT_ENTRYPOINT_AUDIT.md`
- `docs/refactor/PRIVATE_ARCHIVE_ENTRYPOINT_AUDIT.md`
- `docs/refactor/STAGE_1_CONSISTENCY_REPORT.md`

## 10. Test results

Targeted checks:

- `python3 -m unittest tests.test_compat_imports tests.test_private_archive_components tests.test_services tests.test_db_exporter tests.test_db_export_components -q` -> passed (`Ran 72 tests`)
- `python3 -m unittest tests.test_cli tests.test_storage_sqlite -q` -> passed (`Ran 57 tests`)

Final checks:

- `python3 -m unittest tests.test_fixture_e2e -q` -> passed (`Ran 4 tests`)
- `make test` -> passed (`Ran 193 tests in 24.049s`)
- `make verify` -> passed (`ruff check`, `ruff format --check`, `compileall`, and `make test`)
- `python3 -m compileall tg_msg_manager` -> passed
- import smoke -> passed (`import smoke ok`)
- duplicate-class grep -> passed (`DBExportService` and `PrivateArchiveService` each declared once)

## 11. Remaining risks

- `services/private_archive.py` remains a same-name shadow compatibility file; normal imports resolve through the package, so future work must keep the package `__init__` as the public entrypoint.
- Compatibility aggregators are still intentionally present, so future cleanup must stay behavior-safe and import-safe.

## 12. Recommended next step

Focus the next refactor stage on remaining active-package hotspots rather than reopening compatibility files or broad aggregators.
