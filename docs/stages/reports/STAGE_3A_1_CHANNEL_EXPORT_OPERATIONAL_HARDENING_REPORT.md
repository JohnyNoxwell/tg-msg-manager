# Stage 3A.1 — Channel Export Operational Hardening Report

## 1. Summary

Stage 3A.1 operational hardening for `export-channel` is complete within the intended scope.

Implemented in this stage:

- per-dataset `channel_export_state.json`
- incremental channel export based on `last_exported_message_id`
- append-only updates for `messages.jsonl`, `messages.txt`, and `media_manifest.jsonl`
- real `--force` full re-export behavior
- streaming full-export payload writing without materializing the entire history
- dedicated channel export progress events
- CLI progress rendering and no-new-posts messaging
- safe state persistence only after successful payload + manifest writes

## 2. Architecture outcome

All new operational channel-export logic remains isolated under `tg_msg_manager/services/channel_export/`.

New/expanded channel export components:

- `service.py` -> orchestration only
- `state_manager.py` -> filesystem state load/save/validation/run-mode decisions
- `event_emitter.py` -> channel export service events
- `payload_writer.py` -> streaming/append writer session
- `post_fetcher.py` -> incremental `min_message_id` support
- `models.py` -> state/run/result models

Protected hot-path services such as `ExportService`, `DBExportService`, `PrivateArchiveService`, and `ContextEngine` were not used as feature dump points.

## 3. Behavioral result

`export-channel` now behaves as follows:

- first run:
  - full export
  - writes dataset files
  - writes `channel_export_state.json`
- second run:
  - loads state
  - exports only newer posts
  - appends to dataset payload files
  - rewrites `manifest.json`
  - updates state after success
- `--force`:
  - ignores existing state
  - overwrites payload files
  - recreates state from a fresh full export
- no-new-posts:
  - emits `channel_export.no_new_posts`
  - does not advance export state
  - still returns a successful result with zero new posts for the run

## 4. Files changed

- `tg_msg_manager/services/channel_export/__init__.py`
- `tg_msg_manager/services/channel_export/errors.py`
- `tg_msg_manager/services/channel_export/event_emitter.py`
- `tg_msg_manager/services/channel_export/models.py`
- `tg_msg_manager/services/channel_export/payload_writer.py`
- `tg_msg_manager/services/channel_export/plan_builder.py`
- `tg_msg_manager/services/channel_export/post_fetcher.py`
- `tg_msg_manager/services/channel_export/service.py`
- `tg_msg_manager/services/channel_export/source_resolver.py`
- `tg_msg_manager/cli_commands.py`
- `tg_msg_manager/cli_io.py`
- `README.md`
- `COMMANDS.md`
- `PROJECT_ARCHITECTURE_OVERVIEW.md`
- `docs/testing/LIVE_SMOKE_CHECKLIST.md`
- `CHANGELOG.md`
- `docs/refactor/STAGE_3A_1_BASELINE.md`
- `tests/test_channel_export_cli.py`
- `tests/test_channel_export_payload_writer.py`
- `tests/test_channel_export_plan_builder.py`
- `tests/test_channel_export_post_fetcher.py`
- `tests/test_channel_export_service.py`
- `tests/test_channel_export_state_manager.py`

## 5. Tests added or expanded

- full export writes state and payloads
- incremental rerun appends only new posts
- no-new-posts path
- force re-export overwrite semantics
- state not updated on failure
- progress event emission
- state manager round-trip and validation
- payload writer append/progress behavior
- plan builder state path coverage
- post fetcher incremental filtering

## 6. Verification

Channel-export scoped verification passed:

- `pytest tests/test_channel_export_*.py`
- `ruff check tg_msg_manager/services/channel_export tg_msg_manager/cli_io.py tg_msg_manager/cli_commands.py tests/test_channel_export_*.py`

Baseline/global verification status:

- `make test` was already failing before Stage 3A.1 changes in unrelated `tests/test_storage_sqlite.py` areas
- `make verify` was already failing before Stage 3A.1 changes for the same reason
- that baseline state is recorded in `docs/refactor/STAGE_3A_1_BASELINE.md`

## 7. Known limitations

- `--media full` remains intentionally blocked
- channel export still targets broadcast channels only
- channel posts are still not persisted into SQLite
- incremental runs guarantee state safety, but they do not roll back already appended payload files if a write fails mid-run

## 8. Completion status

Stage 3A.1 is complete for the requested operational hardening scope.
