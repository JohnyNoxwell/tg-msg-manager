# STAGE 5E.2 — SQLITE SCHEMA SPLIT REGRESSION EXPANSION

Status: active task
Stage: 5E.2
Type: tests
Depends on: `docs/stages/reports/STAGE_5E_1_SQLITE_SCHEMA_SPLIT_STAGE_2_MIGRATION_HELPER_EXTRACTION_REPORT.md`

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` first.
- Read the Stage 5E.1 report before editing.
- Apply `stage-reviewer` before edits.
- Apply `architecture-guard` because this stage tests storage schema behavior.
- Write a plan with max 5 bullets before editing.
- Do not start any later stage.

## 1. PURPOSE

Expand regression tests around the SQLite schema split after Stage 5E.1 extraction.

This stage is tests-first. Runtime behavior changes are allowed only to fix a regression caused by the extraction.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/stages/reports/STAGE_5E_1_SQLITE_SCHEMA_SPLIT_STAGE_2_MIGRATION_HELPER_EXTRACTION_REPORT.md`
- `docs/architecture/SQLITE_SCHEMA_SPLIT_MAP.md`
- `tg_msg_manager/infrastructure/storage/_sqlite_schema.py`
- `tg_msg_manager/infrastructure/storage/schema/`
- `tests/infrastructure/storage/test_storage_sqlite.py`
- `tests/architecture/test_architecture_wrappers.py`

## 3. HARD PROHIBITIONS

- Do not add new SQLite schema behavior.
- Do not change migrations, SQL, backup table names, `PRAGMA user_version`, or public storage contracts except to fix a Stage 5E.1 regression.
- Do not change services, CLI, dataset validation, channel export, or user-facing docs.
- Do not inspect private SQLite database contents.
- Do not add broad refactors or formatting churn.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Identify regression gaps left by Stage 5E.1 from the report and current tests.
2. Add focused tests for extracted helper delegation and migration behavior that was not already covered.
3. Prefer extending `tests/infrastructure/storage/test_storage_sqlite.py` unless a new focused test file is clearer.
4. Assert final `PRAGMA user_version` where migration branch tests create legacy databases.
5. If a test fails because Stage 5E.1 changed behavior, fix only the extracted helper or delegate responsible.
6. Update the split map only if test ownership or helper boundaries changed.
7. Create the Stage 5E.2 report in Russian.

## 5. REQUIRED DOCS

- `docs/architecture/SQLITE_SCHEMA_SPLIT_MAP.md` only if helper/test ownership changed.
- No user-facing docs.

## 6. TESTS / VERIFICATION

- `python3 -m pytest tests/infrastructure/storage/test_storage_sqlite.py -q`
- `python3 -m pytest tests/architecture/test_architecture_wrappers.py -q`
- `python3 -m compileall tg_msg_manager`
- `ruff check tg_msg_manager tests`
- `git diff --check`

## 7. REPORT

Create `docs/stages/reports/STAGE_5E_2_SQLITE_SCHEMA_SPLIT_REGRESSION_EXPANSION_REPORT.md` in Russian.

The report must include:

- regression tests added or changed;
- any extraction regression fixed;
- verification results;
- confirmation that schema behavior, `PRAGMA user_version`, CLI, services, and dataset behavior were preserved;
- skill lines:
  - `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
  - `architecture-guard: applied from .skills/architecture-guard/SKILL.md`

## 8. COMPLETION CRITERIA

- Additional regression coverage exists for Stage 5E.1 extraction scope.
- No new schema behavior is introduced.
- Required checks pass or unrelated baseline failures are documented.
- `stage-completion-auditor` is applied after the report.
- Lifecycle cleanup is completed according to `AGENTS.md`; do not move unrelated later active files.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Do not start another stage.
