# STAGE 6B.1 — DIRECT PM ARCHIVE FAILURE EXIT CODE

Status: completed
Stage: 6B.1
Type: bugfix
Depends on: Stage 6B.0 complete; `tg_msg_manager/cli/commands/export.py::_handle_export_pm_command` swallowing PM archive exceptions

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.

Execute Stage 6B.1 — DIRECT PM ARCHIVE FAILURE EXIT CODE only after Stage 6B.0 is complete.

Goal:
Fix the direct `export-pm` command so a failed PM archive exits with a non-zero status while preserving retry-task enqueue behavior.

Do not start later stages.
Do not add new features.
Do not change command names, CLI flags, defaults, output files, output directory layout, SQLite schema, archive data flow, or retry enqueue behavior except as required to fix this bug.

Use AGENTS.md compact output format.

## 1. SYMPTOM

Direct CLI `export-pm` can fail inside `_handle_export_pm_command`, enqueue a retry task, log `Error during PM archive: ...`, and return normally.

Affected path:

- `tg_msg_manager/cli/commands/export.py::_handle_export_pm_command`
- direct `tg ... export-pm ...`

Risk:

- scripts can observe exit code `0` even when the current PM archive attempt failed.

## 2. REPRODUCTION / OBSERVED OUTPUT

No live Telegram reproduction command is required.

Use the existing mocked `export-pm` failure test path where `ctx.private_archive.archive_pm` raises `RuntimeError("boom")`.

Expected direct-command behavior:

- retry task is still enqueued;
- current logging behavior is preserved;
- `run_cli()` raises `SystemExit`;
- exit status is non-zero.

## 3. LIKELY CAUSE

Likely cause:

- `_handle_export_pm_command` catches broad `Exception`, enqueues retry, logs the error, and does not re-raise or exit non-zero.

## 4. FILES TO INSPECT

Required:

- `AGENTS.md`
- `docs/stages/active/stage_6b_1_direct_pm_archive_failure_exit_code.md`
- `tg_msg_manager/cli/commands/export.py`
- `tg_msg_manager/cli/__init__.py`
- `tests/cli/test_cli.py`

Optional only if needed:

- `tg_msg_manager/services/retry_worker.py`
- `docs/development/CLI_CONTRACT.md`

Do not read or change:

- unrelated source modules
- unrelated docs
- `docs/archive/`
- completed stages
- existing `docs/stages/reports/` files unrelated to this stage

## 5. HARD PROHIBITIONS

Do not add features.
Do not perform broad refactors.
Do not change command names, CLI flags, defaults, output files, output directory layout, SQLite schema, archive data flow, retry enqueue behavior, or report format.
Do not remove retry-task enqueue on PM archive failure.
Do not add analytics, OSINT logic, profiling, fingerprinting, OCR, STT, media recognition, or LLM-dependent behavior.
Do not add new runtime dependencies.
Do not modify protected service facades or compatibility wrappers.
Do not move archive algorithms into CLI.

## 6. MINIMAL PATCH TASKS

1. Confirm the failing path.
   - inspect `_handle_export_pm_command`;
   - inspect existing PM archive failure test;
   - do not edit yet.

2. Patch the narrow cause.
   - preserve retry-task enqueue;
   - preserve existing logger message;
   - convert the direct-command failure to non-zero exit.

3. Add regression coverage.
   - update the focused `export-pm` failure test in `tests/cli/test_cli.py`;
   - assert retry enqueue still happens;
   - assert non-zero `SystemExit` from direct `export-pm`.

4. Run focused verification.
   - compile;
   - run focused CLI tests;
   - run architecture boundary tests if CLI imports or dispatch shape changes.

## 7. REGRESSION TESTS

Required:

- `tests/cli/test_cli.py` must cover direct `export-pm` failure returning non-zero while preserving retry enqueue.

The test must not require live Telegram, network access, or real SQLite data.

## 8. NON-REGRESSION CHECKS

Verify:

- successful direct `export-pm` path remains unchanged;
- retry enqueue on PM archive failure remains unchanged;
- direct command names, flags, and defaults remain unchanged;
- SQLite schema remains unchanged.

## 9. REQUIRED DOCS

Required:

- `docs/stages/reports/STAGE_6B_1_DIRECT_PM_ARCHIVE_FAILURE_EXIT_CODE_REPORT.md`

Conditional:

- `CHANGELOG.md` only if project convention records this bug fix before release.
- `docs/development/CLI_CONTRACT.md` only if it currently documents exit-code behavior or examples become inaccurate.

Do not update user-facing docs otherwise.

## 10. REPORT

Create:

- `docs/stages/reports/STAGE_6B_1_DIRECT_PM_ARCHIVE_FAILURE_EXIT_CODE_REPORT.md`

Report must record:

- exact files changed;
- exact checks run;
- bug fixed;
- behavior unchanged;
- what was not run and why;
- completion status.

Write the report in Russian.

## 11. COMPLETION CRITERIA

This stage is complete when:

- direct `export-pm` failure exits non-zero;
- retry enqueue remains covered and preserved;
- regression coverage exists or inability is documented;
- prohibited behavior remains unchanged;
- docs were updated only if required, or no docs update was needed;
- tests/checks are recorded;
- report exists;
- lifecycle cleanup is completed according to AGENTS.md.

## 12. OUTPUT LIMITS

Use AGENTS.md compact final response format.

Final response must contain only:

DONE:
- ...

CHANGED:
- ...

CHECKS:
- ...

NOTES:
- ...

STAGE:
- complete/incomplete: <reason if incomplete>

Do not paste full diffs.
Do not explain the task back to the user.
Do not include broad summaries.
Do not include future recommendations unless required by a real blocker.
