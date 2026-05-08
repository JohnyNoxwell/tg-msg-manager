# Stage 0 Final Report

Date: 2026-05-05

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

## Export And Context Hot Paths

- `tg_msg_manager/services/exporter.py` is now a 6-line compatibility wrapper.
- `tg_msg_manager/services/export/service.py` is a 192-line facade backed by:
  - `planner.py`
  - `target_resolver.py`
  - `fetch_orchestrator.py`
  - `checkpoint_manager.py`
  - `chat_sync.py`
  - `dialog_sync.py`
  - `event_emitter.py`
- `tg_msg_manager/services/context_engine.py` is now a 6-line compatibility wrapper.
- `tg_msg_manager/services/context/engine.py` is a 209-line facade backed by:
  - `reply_chain_resolver.py`
  - `neighbor_window_resolver.py`
  - `cluster_builder.py`
  - `deduplicator.py`
  - `scope_policy.py`
  - `rounds.py`
  - existing `fetchers.py` / `fallback.py`

## Hot-Path File Size Review

Current post-Stage-0 snapshot:

- `tg_msg_manager/cli.py` -> `256`
- `tg_msg_manager/services/exporter.py` -> `6`
- `tg_msg_manager/services/export/service.py` -> `192`
- `tg_msg_manager/services/context_engine.py` -> `6`
- `tg_msg_manager/services/context/engine.py` -> `209`
- `tg_msg_manager/services/db_exporter.py` -> `921`
- `tg_msg_manager/infrastructure/storage/_sqlite_read_path.py` -> `17`

Interpretation:

- `exporter.py` and `context_engine.py` no longer act as hot-path monoliths.
- export/context orchestration now sits behind dedicated namespace modules with explicit responsibility boundaries.
- the main remaining large service file is `db_exporter.py`, which was outside the strict Stage 0 target list.

## Verification

Final verification was run serially on 2026-05-05.

Results:

- `python3 -m unittest discover -s tests -q` -> `Ran 178 tests in 23.548s`, `OK`
- `python3 -m unittest tests.test_services tests.test_sync_system tests.test_cli tests.test_storage_sqlite -q` -> `Ran 111 tests in 17.569s`, `OK`
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

- `tg_msg_manager/services/db_exporter.py`
- `tg_msg_manager/services/private_archive.py`

These are outside the completed Stage 0 export/context/write-path split and are the main candidates for any future architecture pass.
