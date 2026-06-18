# STAGE 7A.0 — TEST INFRASTRUCTURE BASELINE AND HARDENING PLAN

Status: completed
Stage: 7A.0
Type: docs
Depends on: `Makefile`, `.github/workflows/ci.yml`, `pyproject.toml`, `docs/development/`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.

Execute only Stage 7A.0.

Goal:
Record the current test infrastructure baseline and create atomic follow-up stages for hardening toward a serious local data pipeline gate.

Do not change product code, CLI behavior, SQLite schema, dataset formats, Telegram logic, or runtime dependencies.

Use AGENTS.md compact output format.

## 1. PURPOSE

Create a factual baseline and staged hardening path for:

- pytest as the authoritative local/CI test runner;
- fixture-backed contract snapshot gates;
- coverage and type-check gate precheck.

## 2. FILES TO INSPECT

Required:
- `AGENTS.md`
- `Makefile`
- `.github/workflows/ci.yml`
- `pyproject.toml`
- `docs/development/README.md`
- `docs/development/LOCAL_VERIFICATION_MATRIX.md`
- `docs/development/PR_CHECKLIST.md`
- `docs/stages/README.md`

May create:
- `docs/stages/reports/STAGE_7A_0_TEST_INFRASTRUCTURE_BASELINE_AND_HARDENING_PLAN_REPORT.md`
- `docs/stages/active/STAGE_7A_1_PYTEST_AUTHORITY_AND_CI_GATE_ALIGNMENT.md`
- `docs/stages/active/STAGE_7A_2_FIXTURE_CONTRACT_SNAPSHOT_GATE.md`
- `docs/stages/active/STAGE_7A_3_COVERAGE_AND_TYPECHECK_GATE_PRECHECK.md`

Do not read or change:
- source modules;
- test implementation files beyond path inventory;
- unrelated docs;
- `docs/archive`;
- existing `docs/stages/reports` files unrelated to this stage.

## 3. HARD PROHIBITIONS

Do not change code or tests.
Do not change `Makefile` in this stage.
Do not add or remove dependencies.
Do not change CLI names, flags, defaults, outputs, or behavior.
Do not change SQLite schema or migrations.
Do not change export formats, fixture contents, or runtime data flow.
Do not add analytics, profiling, OSINT, OCR, STT, media analysis, or LLM-dependent logic.
Do not modify protected service facades or compatibility wrappers.
Do not mark later stages complete.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Inspect the required files and record the current gate.
2. Run a non-mutating pytest collection/execution check if available.
3. Create follow-up stage files for Stage 7A.1, Stage 7A.2, and Stage 7A.3.
4. Create the Stage 7A.0 report in Russian.
5. Update `docs/stages/README.md` to show Stage 7A.0 complete and Stage 7A.1-7A.3 active.

## 5. REQUIRED DOCS

Required:
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_7A_0_TEST_INFRASTRUCTURE_BASELINE_AND_HARDENING_PLAN_REPORT.md`

Do not update user-facing product docs.

## 6. TESTS / VERIFICATION

Required:

```bash
python3 -m pytest tests -q
git diff --check
```

Do not claim checks passed unless actually run.

## 7. REPORT

Create:

```text
docs/stages/reports/STAGE_7A_0_TEST_INFRASTRUCTURE_BASELINE_AND_HARDENING_PLAN_REPORT.md
```

The report must be factual and written in Russian.

Record:
- current `make test` runner;
- current CI gate;
- current dev test dependencies;
- pytest result if run;
- created stage files;
- dirty worktree caveat if present;
- skills applied;
- completion status.

## 8. COMPLETION CRITERIA

This stage is complete when:

- baseline is recorded;
- follow-up stage files exist;
- required report exists;
- `docs/stages/README.md` reflects Stage 7A state;
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must use AGENTS.md format.
Do not paste full diffs.
Do not summarize unrelated repository history.
Keep notes compact.
