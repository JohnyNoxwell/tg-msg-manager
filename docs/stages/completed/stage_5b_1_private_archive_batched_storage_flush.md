# STAGE 5B.1 — Private Archive Batched Storage Flush

Status: active task
Stage: 5B.1
Type: implementation
Depends on: `tg_msg_manager/services/private_archive/`; `tg_msg_manager/infrastructure/storage/contracts/private_archive_storage.py`

---

## 0. CODEX ENTRY CONTRACT

1. Read `AGENTS.md`.
2. Read this stage file only.
3. Apply `stage-reviewer` before implementation. If no tool exists, read `.skills/stage-reviewer/SKILL.md`.
4. Apply `architecture-guard` because this touches a protected service facade and storage behavior. If no tool exists, read `.skills/architecture-guard/SKILL.md`.
5. Do not start any other active 5B stage.

## 1. PURPOSE

Remove the private archive per-message SQLite flush bottleneck while preserving archive output, CLI behavior, storage schema, retry semantics, and PM archive state semantics.

Current risk to address:

- `PrivateArchiveStreamProcessor.process_message()` calls `storage.save_message(message, target_id=user_id)` with default `flush=True`.
- Large PM archives can wait for SQLite queue drain once per message.

## 2. FILES TO INSPECT

Inspect only:

- `AGENTS.md`
- `docs/architecture/README.md`
- `docs/architecture/ARCHITECTURE_RULES.md`
- `docs/development/README.md`
- `tg_msg_manager/services/private_archive/service.py`
- `tg_msg_manager/services/private_archive/stream_processor.py`
- `tg_msg_manager/services/private_archive/archive_writer.py`
- `tg_msg_manager/services/private_archive/media_downloader.py`
- `tg_msg_manager/services/private_archive/state_manager.py`
- `tg_msg_manager/infrastructure/storage/contracts/private_archive_storage.py`
- `tg_msg_manager/infrastructure/storage/contracts/common.py`
- `tests/services/private_archive/test_private_archive_components.py`
- `tests/services/test_services.py` only if existing private archive assertions require it

May create or update tests only under:

- `tests/services/private_archive/`

May create:

- `docs/stages/reports/STAGE_5B_1_PRIVATE_ARCHIVE_BATCHED_STORAGE_FLUSH_REPORT.md`

## 3. HARD PROHIBITIONS

- Do not change CLI commands, flags, prompts, output text, filenames, directory layout, or state file names.
- Do not change SQLite schema or migrations.
- Do not add raw SQL outside storage modules.
- Do not add business logic to compatibility wrappers.
- Do not change media download concurrency or media path policy.
- Do not change retry task format.
- Do not make `PrivateArchiveService` hold new feature logic; only minimal orchestration wiring is allowed there.
- Do not change public behavior of `export-pm` except reduced internal flush frequency.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Change private archive message persistence so each message is queued with `flush=False`.
2. Add one final `await storage.flush()` after message streaming completes and before `emit_completed()` and `mark_synced()`.
3. Keep media download and archive text writing order unchanged.
4. If a stream exception occurs, do not mark the target synced.
5. Add focused tests proving:
   - per-message saves use `flush=False`;
   - final flush is awaited before `mark_synced()`;
   - `mark_synced()` is not called when stream processing raises.

## 5. REQUIRED DOCS

No user docs are required if CLI behavior and output files are unchanged.

Create the stage report:

- `docs/stages/reports/STAGE_5B_1_PRIVATE_ARCHIVE_BATCHED_STORAGE_FLUSH_REPORT.md`

Update architecture/development docs only if this stage changes documented behavior.

## 6. TESTS / VERIFICATION

Run:

- `pytest tests/services/private_archive/test_private_archive_components.py`
- `python3 -m compileall tg_msg_manager`
- `ruff check tg_msg_manager tests`

If a required check cannot run, record the exact reason in the report and final response.

## 7. REPORT

Report in Russian:

- files changed;
- behavior preserved;
- why any protected file change was only orchestration;
- tests/checks run;
- `stage-reviewer` and `architecture-guard` application.

## 8. COMPLETION CRITERIA

- Per-message private archive storage calls no longer flush individually.
- Final flush occurs before completed state is marked.
- Required tests pass or failures are documented as unrelated blockers.
- No schema, CLI, dataset, media, or retry format changes.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md` final structure, be in Russian, and stay under 1200 characters.
