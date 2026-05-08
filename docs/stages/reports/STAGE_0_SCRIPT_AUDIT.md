# Stage 0 Script Audit

Date: 2026-05-04

## Inventory

| Script | Purpose | Import / help health | Documented in main docs | Classification | Stage 0 decision |
| --- | --- | --- | --- | --- | --- |
| `scripts/cleanup_exports.py` | manual housekeeping for old export folders | `python3 -c "import scripts.cleanup_exports"` succeeds | no README/COMMANDS entry | ad-hoc maintenance | keep in place |
| `scripts/export_user_context_from_db.py` | read-only offline context export from SQLite | `--help` succeeds | mentioned in `CHANGELOG.md` | active diagnostic helper | keep in place |
| `scripts/reset_and_seed_targets.py` | wipe local artifacts and reseed `sync_targets` | `--help` succeeds | mentioned in `CHANGELOG.md` | active maintenance helper | keep in place |

## Notes

### `cleanup_exports.py`

- Safe to import.
- Not part of the supported runtime path.
- Kept because it still performs a bounded local cleanup task.

### `export_user_context_from_db.py`

- Uses direct SQLite reads and is intentionally outside the main CLI surface.
- Suitable for diagnostics and one-off offline analysis.

### `reset_and_seed_targets.py`

- Valid helper for controlled local workspace reset and reseed.
- Not used by production CLI flows.
