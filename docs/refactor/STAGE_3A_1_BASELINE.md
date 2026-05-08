# Stage 3A.1 Baseline

Date: 2026-05-07

## Commit

- Branch: `main`
- Commit: `0e9cfba2c9d811a65e07590187b767099ee64b5b`

## Commands

| Command | Result |
|---|---|
| `git status --short` | existing untracked file: `docs/stages/stage_3a_1_channel_export_operational_hardening_codex_tasks.md` |
| `git rev-parse HEAD` | passed |
| `git branch --show-current` | passed |
| `pytest tests/test_channel_export_*.py` | passed (`51 passed`) |
| `make test` | failed before Stage 3A.1 changes |
| `make verify` | failed before Stage 3A.1 changes |

## Existing unrelated baseline failures

The pre-change full-suite failures are outside `services/channel_export/` and were already present before Stage 3A.1 implementation work started.

Observed failing areas:

- `tests/test_storage_sqlite.py`
- SQLite migration backup-table expectations
- export target state reads returning `None`
- target-link/context-link migration behavior
- checkpoint persistence assertions
- intermittent `disk I/O error` / readonly SQLite test failures

Representative failing tests from the baseline run:

- `test_checkpoint_updates_do_not_refresh_last_sync_at`
- `test_context_link_migration_backfills_chat_safe_rows_and_keeps_backup`
- `test_context_link_migration_fails_when_chat_id_is_ambiguous`
- `test_register_target_preserves_last_sync_at_on_existing_target`
- `test_target_link_migration_adds_metadata_and_keeps_backup`
- `test_target_link_reclassification_upgrades_legacy_rows_in_place`
- `test_upsert_and_get_export_target`

## Known channel export limitations before Stage 3A.1

- full re-export only
- no `channel_export_state.json`
- no append-only incremental mode
- `--force` does not rebuild state semantics
- service materializes all mapped records in memory
- no dedicated channel progress events/rendering
- no explicit `no_new_posts` path
- no formal state-update-after-success guarantee
