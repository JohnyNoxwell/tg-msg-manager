# Stage 6G.0 — Compatibility Surface Baseline Report

Дата: 2026-06-18

## Статус

- Stage 6G.0 выполнен как audit/report-only stage.
- Runtime Python-код не изменялся.
- Stage 6G.1 и Stage 6G.2 не начинались.
- stage-reviewer: applied from .skills/stage-reviewer/SKILL.md
- architecture-guard: applied from .skills/architecture-guard/SKILL.md
- stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md

## Изменённые файлы

- `docs/stages/reports/STAGE_6G_0_COMPATIBILITY_SURFACE_BASELINE_REPORT.md`: создан factual baseline report.
- `docs/stages/README.md`: Stage 6G.0 убран из active list, добавлены ссылка на отчёт и completed prompt group.
- `docs/stages/completed/STAGE_6G_0_COMPATIBILITY_SURFACE_BASELINE.md`: task prompt перемещён из active в completed.

## Сохранено без изменений

- CLI команды, флаги, defaults и вывод не изменялись.
- SQLite schema, dataset formats, state files и runtime behavior не изменялись.
- Compatibility imports не удалялись.

## Инспектированные файлы

- `AGENTS.md`
- `docs/stages/active/STAGE_6G_0_COMPATIBILITY_SURFACE_BASELINE.md`
- `docs/stages/README.md`
- `docs/architecture/ARCHITECTURE_RULES.md`
- `docs/architecture/PROJECT_ARCHITECTURE_OVERVIEW.md`
- `docs/architecture/EXPORT_SERVICE_SPLIT_MAP.md`
- `docs/architecture/CONTEXT_ENGINE_SPLIT_MAP.md`
- `docs/architecture/DB_EXPORT_ENTRYPOINT_AUDIT.md`
- `docs/architecture/PRIVATE_ARCHIVE_IMPORT_RESOLUTION.md`
- `docs/architecture/SQLITE_WRITE_PATH_SPLIT_MAP.md`
- `docs/architecture/STORAGE_CONTRACT_SPLIT_MAP.md`
- `tg_msg_manager/services/exporter.py`
- `tg_msg_manager/services/context_engine.py`
- `tg_msg_manager/services/db_exporter.py`
- `tg_msg_manager/services/private_archive.py`
- `tg_msg_manager/services/db_export/__init__.py`
- `tg_msg_manager/services/private_archive/__init__.py`
- `tg_msg_manager/core/models/service_payloads.py`
- `tg_msg_manager/infrastructure/storage/interface.py`
- `tg_msg_manager/infrastructure/storage/contracts/__init__.py`
- `tg_msg_manager/infrastructure/storage/_sqlite_write_path.py`
- `tg_msg_manager/infrastructure/storage/_sqlite_sync_state.py`
- `tg_msg_manager/infrastructure/storage/_sqlite_read_path.py`
- `tg_msg_manager/cli_commands.py`
- `tests/architecture/test_architecture_wrappers.py`
- `tests/architecture/test_static_boundaries.py`

## Inventory compatibility surfaces

- `tg_msg_manager/services/exporter.py`: thin public compatibility wrapper for `ExportService`; 6 строк. Next action: migrate internal production/test imports away, keep public compatibility import.
- `tg_msg_manager/services/context_engine.py`: thin public compatibility wrapper for `DeepModeEngine`; 6 строк. Next action: migrate non-compat tests away, keep public compatibility import.
- `tg_msg_manager/services/db_exporter.py`: thin public compatibility wrapper for `DBExportService`; 6 строк. Next action: migrate non-compat tests away, keep public compatibility import.
- `tg_msg_manager/services/private_archive.py`: shadow compatibility shim; Python import of `tg_msg_manager.services.private_archive` resolves to package `__init__.py`. Next action: defer removal, keep shim logic-free.
- `tg_msg_manager/services/db_export/__init__.py`: package-level re-export entrypoint; 3 строки. Next action: acceptable public entrypoint; optional internal convergence can import `.service` directly.
- `tg_msg_manager/services/private_archive/__init__.py`: package-level re-export entrypoint; 3 строки. Next action: acceptable public entrypoint; optional internal convergence can import `.service` directly.
- `tg_msg_manager/core/models/service_payloads.py`: compatibility payload aggregator; 48 строк. Next action: migrate non-compat tests away to `core.models.payloads.*`, keep public compatibility import.
- `tg_msg_manager/infrastructure/storage/interface.py`: umbrella `BaseStorage` and contract re-export compatibility surface; 368 строк. Next action: defer removal; do not add service dependencies or SQL.
- `tg_msg_manager/infrastructure/storage/contracts/__init__.py`: contract package aggregator; 43 строки. Next action: keep as public convenience re-export unless a later stage narrows imports.
- `tg_msg_manager/infrastructure/storage/_sqlite_write_path.py`: compatibility mixin/aggregator with remaining non-thin write queue, background writer, sync save, and row insert logic; 261 строка. Next action: shrink in Stage 6G.2.
- `tg_msg_manager/infrastructure/storage/_sqlite_sync_state.py`: compatibility wrapper over checkpoint/user/report/retry/message writers; 240 строк. Next action: keep for now; mostly delegation.
- `tg_msg_manager/infrastructure/storage/_sqlite_read_path.py`: read-side compatibility mixin aggregator; 19 строк. Next action: keep.
- `tg_msg_manager/cli_commands.py`: CLI command handler compatibility aggregator; 34 строки. Next action: migrate internal production imports away where practical, keep public/test compatibility import.

## Import usage findings

- `services.exporter`: production imports in `tg_msg_manager/application/services.py` and `tg_msg_manager/testing/runtime.py`; tests in `tests/services/test_services.py` and `tests/services/sync/test_sync_system.py`. The `rg` result also matched `services/channel_export/discussions/exporter.py`, which is unrelated by name only.
- `services.context_engine`: test import in `tests/services/test_services.py`; no production import found.
- `services.db_exporter`: test imports in `tests/services/db_export/test_db_export_components.py`, `tests/services/db_export/test_db_exporter.py`, `tests/architecture/test_compat_imports.py`, and `tests/architecture/test_architecture_wrappers.py`; no production import found.
- `services.private_archive` package entrypoint: production imports in `tg_msg_manager/application/services.py` and `tg_msg_manager/testing/runtime.py`; tests in `tests/services/test_services.py`, `tests/architecture/test_compat_imports.py`, and `tests/architecture/test_architecture_wrappers.py`.
- `core.models.service_payloads`: test imports in `tests/services/cleaner/test_cleaner.py`, `tests/services/test_services.py`, `tests/services/sync/test_sync_system.py`, and `tests/architecture/test_compat_imports.py`; no production import found.
- `infrastructure.storage.interface`: production import only in `tg_msg_manager/infrastructure/storage/sqlite.py`; test import in `tests/infrastructure/storage/test_storage_sqlite.py`. Static boundary tests assert no service dependency on `BaseStorage`.
- `_sqlite_write_path`, `_sqlite_sync_state`, `_sqlite_read_path`: production imports only in `tg_msg_manager/infrastructure/storage/sqlite.py`; static architecture tests list write/sync wrappers as compatibility surfaces.
- `cli_commands.py`: production imports in `tg_msg_manager/cli/__init__.py` and `tg_msg_manager/cli_menu.py`; tests in `tests/cli/test_channel_export_cli.py` and `tests/services/dataset_validation/test_dataset_validation_contracts.py`.
- `infrastructure.storage.contracts` package aggregator: no direct package-level imports found by the scoped `rg`; callers use submodules or no import.

## Risk classification

- Low: simple service wrappers `exporter.py`, `context_engine.py`, `db_exporter.py`, `private_archive.py`; package re-exports for `db_export` and `private_archive`; `_sqlite_read_path.py`.
- Medium: `cli_commands.py`, `service_payloads.py`, `storage/interface.py`, `contracts/__init__.py`, `_sqlite_sync_state.py`. These are compatibility surfaces with broad import convenience or legacy contract surface, but no observed service/CLI boundary violation.
- High: `_sqlite_write_path.py`, because it still contains non-thin queue/background writer behavior and raw SQL row insertion while being documented as a compatibility aggregator.

## Stage 6G.1 candidate files

- `tg_msg_manager/application/services.py`: migrate from `..services.exporter` to `..services.export.service`; optionally import DB/private archive implementation classes directly from `.service`.
- `tg_msg_manager/testing/runtime.py`: same service import convergence as application runtime.
- `tg_msg_manager/cli/__init__.py`: migrate internal imports from `..cli_commands` to `..cli.commands`.
- `tg_msg_manager/cli_menu.py`: migrate internal import from `.cli_commands` to `.cli.commands`.
- `tests/services/test_services.py`: migrate non-compat imports from `context_engine`, `exporter`, `private_archive`, and `service_payloads`.
- `tests/services/sync/test_sync_system.py`: migrate `exporter` and `service_payloads`.
- `tests/services/cleaner/test_cleaner.py`: migrate `service_payloads`.
- `tests/services/db_export/test_db_export_components.py`: migrate `db_exporter` to `services.db_export`.
- Keep `tests/architecture/test_compat_imports.py`, `tests/architecture/test_architecture_wrappers.py`, and focused compatibility tests on old import paths.

## Stage 6G.2 candidate files

- `tg_msg_manager/infrastructure/storage/_sqlite_write_path.py`: extract or delegate remaining non-thin methods `_enqueue_write_item`, `save_message`, `save_messages`, `_save_message_sync`, `_background_writer`, and `_upsert_message_row_in_conn`.
- `tg_msg_manager/infrastructure/storage/write/message_writer.py`: likely target for row insert/save sync behavior.
- `tg_msg_manager/infrastructure/storage/write/transaction.py` or a dedicated writer worker module: likely target for queue/background writer behavior if existing split modules do not already own it.
- `tests/architecture/test_architecture_wrappers.py` and `tests/architecture/test_static_boundaries.py`: add or adjust guardrails only if Stage 6G.2 changes compatibility boundaries.

## Recommended next stage order

1. Stage 6G.1 first: reduce internal production/test imports from compatibility surfaces without changing public import behavior.
2. Stage 6G.2 second: shrink `_sqlite_write_path.py` after import convergence evidence is stable.

## Commands run

- `find docs/stages/active -maxdepth 1 -type f | sort`: passed; first active stage identified as `STAGE_6G_0_COMPATIBILITY_SURFACE_BASELINE.md`.
- `sed` reads of required stage, skill, architecture, wrapper, aggregator, and guard-test files: passed.
- `rg` import searches for compatibility surfaces across `tg_msg_manager` and `tests`: passed except one no-match search for package-level `contracts` imports, which returned exit code 1 with no output.
- `wc -l` on compatibility surface files: passed.

## Verification

- `python3 -m pytest tests/architecture/test_architecture_wrappers.py tests/architecture/test_static_boundaries.py -q`: passed, 18 passed in 2.16s.

## Completion audit

- VERDICT: complete
- BLOCKERS: none
- SCOPE: pass; only report/lifecycle docs changed.
- CHECKS: pass; required architecture tests passed and are recorded.
- DOCS: pass; required report exists and lifecycle index was updated.
- LIFECYCLE: pass; Stage 6G.0 task moved from active to completed.
