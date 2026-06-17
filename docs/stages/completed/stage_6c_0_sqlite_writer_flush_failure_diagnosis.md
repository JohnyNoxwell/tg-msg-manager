# STAGE 6C.0 — SQLITE WRITER FLUSH FAILURE DIAGNOSIS

Status: completed
Stage: 6C.0
Type: bugfix-diagnosis
Depends on: `tg_msg_manager/infrastructure/storage/_sqlite_write_path.py`, `tg_msg_manager/infrastructure/storage/sqlite.py`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.

Execute Stage 6C.0 only.

Goal:
Confirm the SQLite background writer failure path with no runtime patch.

Do not start later stages.
Do not add features.
Do not change public CLI behavior, output formats, SQLite schema, or data flow.

Use AGENTS.md compact output format.

## 1. PURPOSE

Diagnose the reported reliability defect:

- `_background_writer` dequeues items from `_write_queue`;
- `_save_batches_by_target` can raise during commit;
- `task_done()` is currently reached only after successful save;
- `flush()` waits on `_write_queue.join()` and can hang after a failed batch.

## 2. FILES TO INSPECT

Required:

- `tg_msg_manager/infrastructure/storage/_sqlite_write_path.py`
- `tg_msg_manager/infrastructure/storage/sqlite.py`
- `tests/infrastructure/storage/test_storage_sqlite.py`

May read:

- `AGENTS.md`
- this stage file
- `.skills/architecture-guard/SKILL.md`

Do not read or change:

- unrelated source modules
- unrelated docs
- `docs/archive`
- completed stages
- existing `docs/stages/reports` files unrelated to this stage

## 3. HARD PROHIBITIONS

Do not patch runtime code in this stage.
Do not add tests in this stage.
Do not add features.
Do not perform broad refactors.
Do not change command names, CLI flags, defaults, output files, output directory layout, SQLite schema, or data flow.
Do not add analytics, OSINT logic, profiling, fingerprinting, OCR, STT, media recognition, or LLM-dependent behavior.
Do not add new runtime dependencies.
Do not modify protected files.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Confirm the failing path.
   - inspect `_background_writer`
   - inspect `flush`
   - inspect existing queue tests
   - do not edit runtime or tests

2. Record the diagnosis.
   - create `docs/stages/reports/STAGE_6C_0_SQLITE_WRITER_FLUSH_FAILURE_DIAGNOSIS_REPORT.md`
   - include exact files inspected and whether the defect is confirmed

3. Run focused baseline verification.
   - `pytest tests/infrastructure/storage/test_storage_sqlite.py -k "flush_drains_all_queued_writes or save_message_waits_when_write_queue_is_full"`

## 5. REQUIRED DOCS

Required:

- `docs/stages/reports/STAGE_6C_0_SQLITE_WRITER_FLUSH_FAILURE_DIAGNOSIS_REPORT.md`

Do not update user-facing docs or `CHANGELOG.md` in this stage.

## 6. TESTS / VERIFICATION

Run:

- `pytest tests/infrastructure/storage/test_storage_sqlite.py -k "flush_drains_all_queued_writes or save_message_waits_when_write_queue_is_full"`

Do not claim tests passed unless actually run.

## 7. REPORT

Report must record:

- exact files inspected
- exact checks run
- whether the defect is confirmed
- runtime files changed: none
- completion status

## 8. COMPLETION CRITERIA

This stage is complete when:

- defect diagnosis is recorded;
- no runtime or test patch was made;
- focused baseline check is recorded;
- report exists;
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Use AGENTS.md compact final response format.

Do not paste full diffs.
Do not explain the task back to the user.
Do not include broad summaries.
Do not include future recommendations unless required by a real blocker.
