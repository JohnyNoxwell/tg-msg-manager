# Stage 1 Baseline

## 1. Commit

- Branch: `main`
- Commit: `eb703a0dec15b579abd72d100f0a48f102ecc351`

## 2. Git status

```text
?? AGENTS.md
```

## 3. Test commands

- `make test`
- `make lint`
- `make format-check`
- `make verify`
- `python3 -m unittest tests.test_fixture_e2e -q`

## 4. Test results

### `make test`

- Status: passed
- Duration: `real 24.40`
- Result: `Ran 178 tests in 23.347s`

### `make lint`

- Status: failed
- Duration: `real 0.33`
- Result: `ruff check` reported 6 issues

Current failures before Stage 1 refactor:

- `tg_msg_manager/infrastructure/storage/_sqlite_schema.py:725` `F541`
- `tg_msg_manager/infrastructure/storage/_sqlite_write_path.py:5` `F401`
- `tg_msg_manager/services/context/engine.py:3` `F401`
- `tg_msg_manager/services/context/engine.py:3` `F401`
- `tg_msg_manager/services/context/engine.py:21` `F401`
- `tg_msg_manager/services/db_exporter.py:879` `F841`

### `make format-check`

- Status: failed
- Duration: `real 0.19`
- Result: `ruff format --check` would reformat 19 files

### `make verify`

- Status: failed
- Duration: `real 0.17`
- Failure mode: stops in `make lint` on the same pre-existing lint issues listed above

## 5. Fixture E2E results

### `python3 -m unittest tests.test_fixture_e2e -q`

- Status: passed
- Duration: `real 4.88`
- Result: `Ran 4 tests in 4.254s`

## 6. Known pre-existing issues

- Repository is not lint-clean before Stage 1.
- Repository is not format-clean before Stage 1.
- `make verify` fails before any Stage 1 changes because it depends on `make lint`.
- `services/db_exporter.py` already contains an unused local assignment on the hot path.

## 7. Files targeted by Stage 1

- `tg_msg_manager/services/db_exporter.py`
- `tg_msg_manager/services/private_archive.py`
- `tg_msg_manager/infrastructure/storage/interface.py`
- `tg_msg_manager/core/models/service_payloads.py`
- `tg_msg_manager/infrastructure/storage/read/analytics/`
- `docs/ARCHITECTURE_RULES.md`
- `docs/PR_CHECKLIST.md`
- `docs/testing/LIVE_SMOKE_CHECKLIST.md`
