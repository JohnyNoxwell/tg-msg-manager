# Stage 0 Final Report

Date: 2026-05-04

## Scope

Stage 0 was completed as a behavior-preserving refactor/documentation gate.

No new product feature was added.

## What Changed

### CLI

- `tg_msg_manager/cli.py` was reduced to a thin entry/dispatch module.
- Parser construction moved to `tg_msg_manager/cli_parser.py`.
- Command handlers moved to `tg_msg_manager/cli_commands.py`.
- Interactive menu flows moved to `tg_msg_manager/cli_menu.py`.
- Shared CLI helper logic moved to `tg_msg_manager/cli_support.py`.
- Public command names, flags, defaults, and `python3 -m tg_msg_manager.cli ...` behavior were preserved.

### DB export

- `DBExportService` kept orchestration responsibility.
- Manifest/fingerprint helpers moved under `tg_msg_manager/services/db_export/manifest.py`.
- JSONL formatting helpers moved under `tg_msg_manager/services/db_export/jsonl_writer.py`.
- TXT formatting helpers moved under `tg_msg_manager/services/db_export/txt_writer.py`.
- Export-source / plan helpers moved under `tg_msg_manager/services/db_export/summary.py`.

### SQLite read-side

- The former `_sqlite_read_path.py` monolith was reduced to an aggregator.
- Read queries are now grouped under:
  - `read/messages.py`
  - `read/targets.py`
  - `read/context.py`
  - `read/exports.py`
  - `read/reporting.py`
  - shared coercion in `read/common.py`

### Scripts and documentation

- Stage 0 baseline/smoke/audit/storage docs were added;
- architecture rules for future contributors were added.

## What Was Already In Acceptable Stage 0 Shape And Was Preserved

- `ExportService` already delegated scan/checkpoint/planning logic into `services/sync/`.
- `DeepModeEngine` already delegated context traversal/fallback logic into `services/context/`.

Those boundaries were preserved and documented rather than rewritten again.

## Hot-Path File Size Review

Before Stage 0 work in this turn:

- `tg_msg_manager/cli.py` -> `835`
- `tg_msg_manager/services/exporter.py` -> `772`
- `tg_msg_manager/services/context_engine.py` -> `721`
- `tg_msg_manager/services/db_exporter.py` -> `718`
- `tg_msg_manager/infrastructure/storage/_sqlite_read_path.py` -> `676`

After Stage 0 completion:

- `tg_msg_manager/cli.py` -> `248`
- `tg_msg_manager/services/exporter.py` -> `772`
- `tg_msg_manager/services/context_engine.py` -> `721`
- `tg_msg_manager/services/db_exporter.py` -> `450`
- `tg_msg_manager/infrastructure/storage/_sqlite_read_path.py` -> `17`

Interpretation:

- `cli.py`, `db_exporter.py`, and `_sqlite_read_path.py` were materially reduced.
- `exporter.py` and `context_engine.py` remain large, but their detailed responsibilities were already split into focused submodules before this pass.

## Verification

Final verification was run serially on 2026-05-04.

Results:

- `python3 -m unittest discover -s tests -q` -> `Ran 148 tests`, `OK`
- `make test` -> `OK`
- `make verify` -> `OK`
- `python3 -m unittest tests.test_fixture_e2e -q` -> `Ran 4 tests`, `OK`
- CLI help smoke commands for top-level and Stage 0 subcommands exit successfully

## CLI Surface Check

Confirmed unchanged in Stage 0:

- no top-level command removed;
- no flag renamed;
- no parser default intentionally changed;
- menu hotkeys `R` and `P` remain available;
- `report` and `db-export` remain read-only Telegram-independent CLI paths.

## Remaining Known Hotspots

- `tg_msg_manager/services/exporter.py`
- `tg_msg_manager/services/context_engine.py`

These remain orchestration-heavy files. Stage 0 completion is still valid because their subordinate sync/context logic already lives in dedicated modules and no new feature logic was added back into them during this pass.
