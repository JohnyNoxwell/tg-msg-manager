# Stage 3A Baseline

## Commit

- `9b1142db0c59382794308ec056d88a8b0b7bbe58`

## Branch

- `main`

## Git status

```text
git status --short
?? docs/stages/
```

## Baseline commands

| Command | Result | Notes |
|---|---|---|
| `git status --short` | warning | Worktree is not clean because `docs/stages/` is untracked. This does not overlap the `channel_export` implementation scope. |
| `git rev-parse HEAD` | passed | Resolved to `9b1142db0c59382794308ec056d88a8b0b7bbe58`. |
| `git branch --show-current` | passed | Current branch is `main`. |
| `make test` | failed | Baseline branch is already red in unrelated storage/reporting areas before Stage 3A work. Failing tests include `tests/test_cleaner.py`, `tests/test_reporting.py`, `tests/test_storage_sqlite.py`, and `tests/test_sync_system.py`. |
| `make verify` | failed | Fails because `make test` fails. `compileall`, `ruff check`, and `ruff format --check` passed before the test phase failed. |

## Existing architecture constraints

- Keep `CLI -> services -> domain -> contracts -> infrastructure` layering intact.
- Do not add Stage 3A logic to protected hot-path files such as `tg_msg_manager/services/db_exporter.py`, `tg_msg_manager/services/exporter.py`, `tg_msg_manager/services/private_archive.py`, or `tg_msg_manager/services/context_engine.py`.
- Do not change CLI contracts, Telegram client code, SQLite schema, existing export formats, or existing service orchestration in this slice.
- Keep new channel-export components small and single-purpose: models, plan builder, renderers, manifest writing, and media policy only.

## Feature scope

- Implement Stage 3A Phases 1–8 only.
- Add `tg_msg_manager/services/channel_export/` components for:
  - models
  - plan builder
  - JSONL renderer
  - TXT renderer
  - manifest writer
  - media policy
  - media manifest writer
- Add targeted tests for these components only.
- Defer source resolver, post fetching/mapping, service orchestration, CLI wiring, runtime integration, docs beyond this baseline, and changelog updates.
