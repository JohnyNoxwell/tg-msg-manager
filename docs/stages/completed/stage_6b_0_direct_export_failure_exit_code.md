# STAGE 6B.0 — DIRECT EXPORT FAILURE EXIT CODE

Status: completed
Stage: 6B.0
Type: bugfix
Depends on: `tg_msg_manager/cli/commands/export.py::_handle_export_command` swallowing export exceptions

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.

Execute Stage 6B.0 — DIRECT EXPORT FAILURE EXIT CODE.

Goal:
Fix the direct `export` command so a failed export exits with a non-zero status for automation.

Do not start later stages.
Do not add new features.
Do not change command names, CLI flags, defaults, output files, output directory layout, SQLite schema, export data flow, or interactive menu behavior except as required to fix this bug.

Use AGENTS.md compact output format.

## 1. SYMPTOM

Direct CLI `export` can fail inside `_handle_export_command`, log `Error during export: ...`, and return normally.

Affected path:

- `tg_msg_manager/cli/commands/export.py::_handle_export_command`
- direct `tg ... export ...`

Risk:

- scripts can observe exit code `0` even when export failed.

## 2. REPRODUCTION / OBSERVED OUTPUT

No live Telegram reproduction command is required.

Use a focused test with mocked `CLIContext` where `_run_export_sync` raises `RuntimeError("boom")`.

Expected direct-command behavior:

- `run_cli()` raises `SystemExit`;
- exit status is non-zero;
- current logging behavior is preserved.

## 3. LIKELY CAUSE

Likely cause:

- `_handle_export_command` catches broad `Exception`, logs the error when `ctx.pm.should_stop()` is false, and does not re-raise or exit non-zero.

## 4. FILES TO INSPECT

Required:

- `AGENTS.md`
- `docs/stages/active/stage_6b_0_direct_export_failure_exit_code.md`
- `tg_msg_manager/cli/commands/export.py`
- `tg_msg_manager/cli/__init__.py`
- `tests/cli/test_cli.py`

Optional only if needed:

- `tg_msg_manager/cli_support.py`
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
Do not change command names, CLI flags, defaults, output files, output directory layout, SQLite schema, export data flow, retry behavior, or report format.
Do not change interactive menu behavior unless the direct command path cannot be fixed without it.
Do not add analytics, OSINT logic, profiling, fingerprinting, OCR, STT, media recognition, or LLM-dependent behavior.
Do not add new runtime dependencies.
Do not modify protected service facades or compatibility wrappers.
Do not move export algorithms into CLI.

## 6. MINIMAL PATCH TASKS

1. Confirm the failing path.
   - inspect `_handle_export_command`;
   - inspect `run_cli()` direct command dispatch;
   - do not edit yet.

2. Patch the narrow cause.
   - preserve existing logger message;
   - convert non-interrupt export failure to non-zero direct-command exit;
   - preserve emergency-stop behavior for `ctx.pm.should_stop()`.

3. Add regression coverage.
   - add or update one focused test in `tests/cli/test_cli.py`;
   - mock `_run_export_sync` failure;
   - assert non-zero `SystemExit` from direct `export`.

4. Run focused verification.
   - compile;
   - run focused CLI tests;
   - run architecture boundary tests if CLI imports or dispatch shape changes.

## 7. REGRESSION TESTS

Required:

- `tests/cli/test_cli.py` must cover direct `export` failure returning non-zero.

The test must not require live Telegram, network access, or real SQLite data.

## 8. NON-REGRESSION CHECKS

Verify:

- successful direct `export` path remains unchanged;
- direct command names, flags, and defaults remain unchanged;
- JSONL/TXT export formats remain unchanged;
- SQLite schema remains unchanged;
- interactive menu behavior is not intentionally changed.

## 9. REQUIRED DOCS

Required:

- `docs/stages/reports/STAGE_6B_0_DIRECT_EXPORT_FAILURE_EXIT_CODE_REPORT.md`

Conditional:

- `CHANGELOG.md` only if project convention records this bug fix before release.
- `docs/development/CLI_CONTRACT.md` only if it currently documents exit-code behavior or examples become inaccurate.

Do not update user-facing docs otherwise.

## 10. REPORT

Create:

- `docs/stages/reports/STAGE_6B_0_DIRECT_EXPORT_FAILURE_EXIT_CODE_REPORT.md`

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

- direct `export` failure exits non-zero;
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
