# STAGE 5E.0 — SQLITE SCHEMA SPLIT STAGE 2 MIGRATION HELPERS PRECHECK

Status: active task
Stage: 5E.0
Type: architecture/precheck
Depends on: `docs/stages/reports/STAGE_5D_0_SQLITE_SCHEMA_SPLIT_STAGE_1_REPORT.md`, `docs/stages/reports/STAGE_5D_1_DATASET_CONTRACT_GAP_CLOSURE_PLAN_REPORT.md`, `docs/stages/reports/STAGE_5D_2_RUN_CHANGELOG_KEY_SET_CONTRACT_TESTS_REPORT.md`, `docs/stages/reports/STAGE_5D_3_TXT_PROJECTION_CONTRACT_CLARIFICATION_REPORT.md`, `docs/stages/reports/STAGE_5D_4_CHANNEL_EXPORT_MODE_MATRIX_TESTS_REPORT.md`, `docs/stages/reports/STAGE_5D_5_USER_QUICKSTART_SAFE_FIRST_EXPORT_GUIDE_REPORT.md`

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` first.
- Do not start this stage while unfinished 5D active tasks remain unless the user explicitly overrides that order.
- Apply `stage-reviewer` before edits.
- Apply `architecture-guard` because this stage touches storage architecture.
- Write a plan with max 5 bullets before editing.
- Do not implement Stage 5E.1.

## 1. PURPOSE

Precheck the Stage 2 SQLite schema split before moving migration helpers.

This stage must produce an exact extraction plan and baseline verification. It must not move code.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/stages/reports/STAGE_5D_0_SQLITE_SCHEMA_SPLIT_STAGE_1_REPORT.md`
- `docs/architecture/SQLITE_SCHEMA_SPLIT_MAP.md`
- `tg_msg_manager/infrastructure/storage/_sqlite_schema.py`
- `tg_msg_manager/infrastructure/storage/schema/__init__.py`
- `tg_msg_manager/infrastructure/storage/schema/tables.py`
- `tg_msg_manager/infrastructure/storage/schema/indexes.py`
- `tg_msg_manager/infrastructure/storage/schema/inspection.py`
- `tg_msg_manager/infrastructure/storage/sqlite.py`
- `tests/infrastructure/storage/test_storage_sqlite.py`
- `tests/architecture/test_architecture_wrappers.py`

## 3. HARD PROHIBITIONS

- Do not change Python runtime code.
- Do not move functions in this precheck.
- Do not change table SQL, index SQL, migration SQL, backup table names, exception messages, commit behavior, or `PRAGMA user_version`.
- Do not change storage interfaces, service code, CLI code, dataset code, or docs outside this stage scope.
- Do not inspect private SQLite database contents.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Run baseline storage verification before any docs edit.
2. Inventory remaining migration, compatibility, and backfill methods in `SQLiteSchemaMixin`.
3. Define the exact Stage 5E.1 extraction target list and destination modules.
4. Define allowed helper signatures and callback/delegation rules.
5. Update `docs/architecture/SQLITE_SCHEMA_SPLIT_MAP.md` with the Stage 2 precheck plan only.
6. Create the Stage 5E.0 report in Russian.

## 5. REQUIRED DOCS

- `docs/architecture/SQLITE_SCHEMA_SPLIT_MAP.md`
- No user-facing docs.

## 6. TESTS / VERIFICATION

- `python3 -m pytest tests/infrastructure/storage/test_storage_sqlite.py -q`
- `python3 -m pytest tests/architecture/test_architecture_wrappers.py -q`
- `git diff --check`

## 7. REPORT

Create `docs/stages/reports/STAGE_5E_0_SQLITE_SCHEMA_SPLIT_STAGE_2_MIGRATION_HELPERS_PRECHECK_REPORT.md` in Russian.

The report must include:

- baseline verification results;
- exact methods that may move in Stage 5E.1;
- exact modules that may be created or changed in Stage 5E.1;
- invariants that Stage 5E.1 must preserve;
- confirmation that runtime code, CLI, dataset format, and SQLite behavior were not changed;
- skill lines:
  - `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
  - `architecture-guard: applied from .skills/architecture-guard/SKILL.md`

## 8. COMPLETION CRITERIA

- Precheck report exists and is specific enough for Stage 5E.1 to execute without choosing new scope.
- Split map is updated.
- `stage-completion-auditor` is applied after the report.
- Lifecycle cleanup is completed according to `AGENTS.md`; do not move unrelated later active files.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Do not continue to Stage 5E.1.
