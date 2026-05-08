# Stage 0 Baseline

Date: 2026-05-05
Commit hash: `092dbde91c0591dd6e1bc5fe83a26a4f2f7b6f19`

## Project Structure Snapshot

- Root docs present: `README.md`, `PROJECT_ARCHITECTURE_OVERVIEW.md`, `docs/ARCHITECTURE_RULES.md`
- Core runtime: `tg_msg_manager/core/`
- Services: `tg_msg_manager/services/`
- Infrastructure: `tg_msg_manager/infrastructure/`
- CLI surface: `tg_msg_manager/cli.py`, `tg_msg_manager/cli_parser.py`, `tg_msg_manager/cli_commands.py`
- Tests: `tests/`
- Scripts: `scripts/`

## Test Runner

- Primary command: `python3 -m unittest discover -s tests -q`
- Result: `Ran 178 tests in 23.351s`
- Status: `OK`

## Smoke / Focused Checks

- `python3 -m unittest tests.test_fixture_e2e -q`
  Result: `Ran 4 tests in 4.233s`, `OK`
- `python3 -m unittest tests.test_storage_sqlite -q`
  Result: `Ran 39 tests in 11.479s`, `OK`
- `python3 -m unittest tests.test_db_exporter -q`
  Result: `Ran 17 tests in 0.220s`, `OK`
- `python3 -m unittest tests.test_cli -q`
  Result: `Ran 18 tests`, `OK`
- `python3 -m unittest tests.test_services tests.test_storage_sqlite -q`
  Result: `Ran 79 tests in 16.358s`, `OK`

## Known Pre-Existing Non-Blocking Signals

These messages appeared during test execution and are expected by the current test suite:

- retryable fixture logs such as `Tracked sync failed ... fixture retryable sync failure`
- deep-mode fallback warnings such as `Deep full-range live fill failed ...`
- CLI/runtime test logs for archive/export flows

No undocumented failing baseline errors remained after the final Stage 0 verification run.
