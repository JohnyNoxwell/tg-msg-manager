# Stage 0 Baseline

Date: 2026-05-04

## Initial Baseline Before Stage 0 Edits

- Command: `python3 -m unittest discover -s tests -q`
- Result: `Ran 147 tests`
- Status: `OK`

Initial CLI import-health check:

- Command: `python3 -m tg_msg_manager.cli --help`
- Exit status: `0`
- Major commands listed:
  - `export`
  - `update`
  - `retry`
  - `report`
  - `clean`
  - `export-pm`
  - `delete`
  - `schedule`
  - `setup`
  - `db-export`

Makefile verification surface present at baseline:

- `make test`
- `make verify`
- `make lint`
- `make format-check`

## Fragile Behavior Map

### `ExportService`

Behavior that must not change:

- scan-range planning for first sync / head update / tail resume;
- tail checkpoint protection against false contiguous completion;
- tracked-target update flow and dirty-target export follow-up;
- shared tracked-target orchestration through `sync_all_tracked()` and related paths.

Coverage anchors:

- `tests/test_sync_system.py`
- `tests/test_services.py`
- `tests/test_fixture_e2e.py`

### `DeepModeEngine`

Behavior that must not change:

- parent reply lookup;
- child reply inclusion;
- depth-aware structural expansion;
- deterministic fallback clustering;
- graceful degradation on live-fetch failures.

Coverage anchors:

- `tests/test_services.py`
- `tests/test_fixture_e2e.py`

### `DBExportService`

Behavior that must not change:

- TXT export format;
- AI JSONL profile shape;
- full JSON profile passthrough;
- manifest/fingerprint skip behavior;
- streaming export fast path.

Coverage anchors:

- `tests/test_db_exporter.py`
- `tests/test_fixture_e2e.py`

### Former `_sqlite_read_path.py` Monolith

Behavior that must not change:

- typed record coercion from SQLite rows;
- export summary and export row ordering;
- retry queue read ordering;
- target breakdown/reporting counts;
- chunked `IN (...)` reads for large ID lists.

Coverage anchors:

- `tests/test_storage_sqlite.py`
- `tests/test_reporting.py`
- `tests/test_retry_worker.py`
- `tests/test_fixture_e2e.py`

## Final Verification Delta

One additional parser regression test was added during Stage 0 to freeze CLI surface.

- Final command: `python3 -m unittest discover -s tests -q`
- Final result: `Ran 148 tests`
- Final status: `OK`
