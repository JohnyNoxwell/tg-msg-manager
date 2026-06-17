# STAGE 6F.0 — SQLITE SCHEMA STARTUP GUARDRAILS

Status: active task
Stage: 6F.0
Type: tests
Depends on: `tg_msg_manager/infrastructure/storage/_sqlite_schema.py`; `tg_msg_manager/infrastructure/storage/schema/`; `tests/infrastructure/storage/test_storage_sqlite.py`

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` first.
- Read only this stage file and files listed here.
- Apply `stage-reviewer` before edits.
- Apply `architecture-guard` because this stage touches SQLite storage/schema behavior.
- Write a plan with max 5 bullets before editing.
- Do not start Stage 6F.1 or later.

## 1. PURPOSE

Add explicit regression guardrails for SQLite startup so future schema-touch changes cannot silently alter fresh bootstrap, legacy migration, idempotent startup, or current schema shape.

This stage is tests-first. Runtime changes are allowed only to fix a newly exposed startup regression.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/architecture/SQLITE_SCHEMA_SPLIT_MAP.md`
- `docs/development/LOCAL_VERIFICATION_MATRIX.md`
- `tg_msg_manager/infrastructure/storage/_sqlite_schema.py`
- `tg_msg_manager/infrastructure/storage/schema/`
- `tg_msg_manager/infrastructure/storage/_sqlite_identity.py`
- `tg_msg_manager/infrastructure/storage/sqlite.py`
- `tests/infrastructure/storage/test_storage_sqlite.py`

May create:

- `tests/infrastructure/storage/test_sqlite_schema_contract.py` if keeping the contract tests separate is clearer.
- `docs/stages/reports/STAGE_6F_0_SQLITE_SCHEMA_STARTUP_GUARDRAILS_REPORT.md`

May update:

- `docs/stages/README.md` during lifecycle cleanup only.

## 3. HARD PROHIBITIONS

- Do not add SQLite tables, columns, indexes, migrations, or schema versions.
- Do not change `PRAGMA user_version`, migration order, backup table names, or startup behavior except to fix a test-proven regression.
- Do not change CLI, services, dataset export, channel export, or user-facing docs.
- Do not inspect private SQLite database contents.
- Do not add broad refactors or formatting churn.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Add a fresh-database startup contract test that asserts final `PRAGMA user_version`, required tables, key columns, primary keys, and representative indexes.
2. Add legacy-database startup tests for at least versions `0`, `5`, `9`, `10`, `12`, and `13`, asserting final version `14` and preserved data for each scenario.
3. Add idempotency coverage: open the same database twice and assert no duplicate rows, no schema drift, and unchanged version.
4. Add a focused contract helper only inside tests; do not introduce production schema snapshot tooling.
5. If tests expose a startup regression, fix only the smallest storage/schema code path responsible.
6. Create the Stage 6F.0 report in Russian.

## 5. REQUIRED DOCS

- No user-facing docs.
- Update `docs/architecture/SQLITE_SCHEMA_SPLIT_MAP.md` only if test ownership or schema guardrail ownership changes.

## 6. TESTS / VERIFICATION

- `python3 -m pytest tests/infrastructure/storage/test_storage_sqlite.py -q`
- `python3 -m pytest tests/infrastructure/storage/test_sqlite_schema_contract.py -q` if the file is created
- `python3 -m compileall tg_msg_manager`
- `ruff check tg_msg_manager tests`
- `ruff format --check tg_msg_manager tests`
- `git diff --check`
- `make pre-commit`
- `make verify`

## 7. REPORT

Create `docs/stages/reports/STAGE_6F_0_SQLITE_SCHEMA_STARTUP_GUARDRAILS_REPORT.md` in Russian.

The report must include:

- tests added or changed;
- whether any runtime regression was fixed;
- verification results;
- confirmation that schema behavior, `PRAGMA user_version`, CLI behavior, services, and dataset behavior were preserved;
- skill lines:
  - `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
  - `architecture-guard: applied from .skills/architecture-guard/SKILL.md`

## 8. COMPLETION CRITERIA

- Startup guardrails cover fresh DB, selected legacy versions, and repeated startup.
- No new schema behavior is introduced unless fixing a test-proven regression.
- Required checks pass or tooling/baseline blockers are documented.
- `stage-completion-auditor` is applied after the report.
- Lifecycle cleanup is completed according to `AGENTS.md`; do not move later active 6F files.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Do not start another stage.
