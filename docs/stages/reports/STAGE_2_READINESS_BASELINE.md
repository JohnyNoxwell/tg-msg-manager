# Stage 2 Readiness Baseline

## 1. Commit

- `74dec45a6572a22c25ecc2a8a8fcb6e43eda2e70`

## 2. Branch

- `main`

## 3. Git status

```text
git status --short
(clean working tree)
```

## 4. Current known risks

- `PROJECT_ARCHITECTURE_OVERVIEW.md` still needs periodic refresh after refactor waves.
- Compatibility wrapper files must stay thin and must not grow back into active implementations.
- `tg_msg_manager/services/private_archive.py` still coexists with the `services/private_archive/` package and remains a shadow-wrapper trap if future code starts importing the wrong surface.
- `tg_msg_manager/services/db_export/service.py` is still the largest active facade and needs explicit growth protection.
- Live/manual smoke guidance still needs explicit `retry`, `clean`, and `delete` safety coverage.

## 5. Commands to be run

- `make test`
- `make verify`
- `python3 -m compileall tg_msg_manager`
- `ruff check tg_msg_manager tests`
- `ruff format --check tg_msg_manager tests`
- import smoke for `tg_msg_manager.services.*`, storage contracts, and payload modules

## 6. Test results

| Command | Result | Notes |
|---|---|---|
| `make test` | passed | `Ran 193 tests in 24.149s` |
| `make verify` | passed | includes compileall, `ruff check`, `ruff format --check`, and `make test` |
| `python3 -m compileall tg_msg_manager` | passed | no syntax/import issues |
| `ruff check tg_msg_manager tests` | passed | `All checks passed!` |
| `ruff format --check tg_msg_manager tests` | passed | `183 files already formatted` |
| import smoke | passed | `import smoke ok` |
