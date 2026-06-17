# STAGE 6C.1 — SQLITE WRITER FAILED BATCH QUEUE ACCOUNTING

Status: completed
Stage: 6C.1
Type: bugfix
Depends on: Stage 6C.0 diagnosis, `tg_msg_manager/infrastructure/storage/_sqlite_write_path.py`, `tg_msg_manager/infrastructure/storage/sqlite.py`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.

Execute Stage 6C.1 only.

Goal:
Fix the SQLite background writer failed-batch queue accounting bug with the smallest safe patch.

Do not start later stages.
Do not add new features.
Do not change public CLI behavior, output formats, SQLite schema, or data flow except to make failed async writes unblock `flush()` and surface the error.

Use AGENTS.md compact output format.

## 1. PURPOSE

Fix the confirmed reliability defect:

- dequeued writer items must always be acknowledged with `task_done()`;
- `flush()` must not hang forever after a batch commit error;
- commit failure must not be hidden from the caller that flushes.

## 2. FILES TO INSPECT

Required:

- `docs/stages/reports/STAGE_6C_0_SQLITE_WRITER_FLUSH_FAILURE_DIAGNOSIS_REPORT.md`
- `tg_msg_manager/infrastructure/storage/_sqlite_write_path.py`
- `tg_msg_manager/infrastructure/storage/sqlite.py`
- `tests/infrastructure/storage/test_storage_sqlite.py`

May read:

- `AGENTS.md`
- this stage file
- `.skills/architecture-guard/SKILL.md`

Do not read or change:

- unrelated source modules
- unrelated tests
- unrelated docs
- `docs/archive`
- completed stages
- existing `docs/stages/reports` files unrelated to this stage

## 3. HARD PROHIBITIONS

Do not add features.
Do not perform broad refactors.
Do not change command names, CLI flags, defaults, output files, output directory layout, SQLite schema, or data flow except the failed-batch flush behavior scoped here.
Do not retry, requeue, or duplicate failed batches in this stage.
Do not add analytics, OSINT logic, profiling, fingerprinting, OCR, STT, media recognition, or LLM-dependent behavior.
Do not add new runtime dependencies.
Do not modify protected service facades or compatibility wrappers.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Add regression coverage.
   - add one focused async test in `tests/infrastructure/storage/test_storage_sqlite.py`
   - simulate `_save_batches_by_target` raising
   - assert `flush()` completes within a bounded timeout by raising the stored writer error
   - assert queue accounting is drained

2. Patch queue accounting.
   - update `_background_writer` so every dequeued item gets `task_done()` in a `finally` path
   - preserve successful commit telemetry and logging behavior

3. Patch error propagation.
   - store the background writer commit error on the storage instance
   - update `flush()` to raise after `join()` if a background commit failed
   - clear the stored error only after it has been surfaced

4. Run focused verification.
   - compile storage modules
   - run focused SQLite storage tests
   - run ruff on changed files

## 5. REQUIRED DOCS

Required:

- `docs/stages/reports/STAGE_6C_1_SQLITE_WRITER_FAILED_BATCH_QUEUE_ACCOUNTING_REPORT.md`

Conditional:

- no user-facing docs unless behavior documentation becomes inaccurate

Do not update `CHANGELOG.md` in this stage.

## 6. TESTS / VERIFICATION

Run:

- `python3 -m compileall tg_msg_manager/infrastructure/storage`
- `pytest tests/infrastructure/storage/test_storage_sqlite.py -k "flush or write_queue or batch"`
- `ruff check tg_msg_manager/infrastructure/storage/_sqlite_write_path.py tg_msg_manager/infrastructure/storage/sqlite.py tests/infrastructure/storage/test_storage_sqlite.py`

Do not claim tests passed unless actually run.

## 7. REPORT

Report must record:

- exact files changed
- exact checks run
- bug fixed
- behavior unchanged
- what was not run and why
- completion status
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`

## 8. COMPLETION CRITERIA

This stage is complete when:

- failed batch no longer leaves `flush()` hanging;
- regression coverage exists;
- SQLite schema and CLI behavior remain unchanged;
- required checks are recorded;
- report exists;
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Use AGENTS.md compact final response format.

Do not paste full diffs.
Do not explain the task back to the user.
Do not include broad summaries.
Do not include future recommendations unless required by a real blocker.
