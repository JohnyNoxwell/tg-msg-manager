# STAGE 5E.1 — SQLITE SCHEMA SPLIT STAGE 2 MIGRATION HELPER EXTRACTION

Status: active task
Stage: 5E.1
Type: storage/refactor
Depends on: `docs/stages/reports/STAGE_5E_0_SQLITE_SCHEMA_SPLIT_STAGE_2_MIGRATION_HELPERS_PRECHECK_REPORT.md`

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` first.
- Read the Stage 5E.0 report before editing.
- Apply `stage-reviewer` before edits.
- Apply `architecture-guard` because this stage changes storage schema modules.
- Write a plan with max 5 bullets before editing.
- Do not implement Stage 5E.2.

## 1. PURPOSE

Mechanically extract only the migration helper scope approved by Stage 5E.0.

Behavior must remain identical.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/stages/reports/STAGE_5E_0_SQLITE_SCHEMA_SPLIT_STAGE_2_MIGRATION_HELPERS_PRECHECK_REPORT.md`
- `docs/architecture/SQLITE_SCHEMA_SPLIT_MAP.md`
- `tg_msg_manager/infrastructure/storage/_sqlite_schema.py`
- `tg_msg_manager/infrastructure/storage/schema/__init__.py`
- `tg_msg_manager/infrastructure/storage/schema/tables.py`
- `tg_msg_manager/infrastructure/storage/schema/indexes.py`
- `tg_msg_manager/infrastructure/storage/schema/inspection.py`
- only new schema helper modules explicitly allowed by Stage 5E.0
- `tests/infrastructure/storage/test_storage_sqlite.py`
- `tests/architecture/test_architecture_wrappers.py`

## 3. HARD PROHIBITIONS

- Do not add, remove, or alter tables, indexes, columns, migrations, backup table names, SQL semantics, exception behavior, commits, or `PRAGMA user_version`.
- Do not change `_init_db` ordering.
- Do not change `tg_msg_manager/infrastructure/storage/sqlite.py` unless Stage 5E.0 explicitly allowed it.
- Do not change storage interfaces, services, CLI, dataset validation, or channel export code.
- Do not import services or CLI from infrastructure modules.
- Do not extract functions not listed in the Stage 5E.0 report.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Run baseline storage tests before edits.
2. Create only Stage 5E.0-approved helper module files.
3. Move one approved helper category at a time.
4. Keep `SQLiteSchemaMixin` method names as compatibility delegates unless Stage 5E.0 explicitly allows removal.
5. Preserve all call ordering and callback behavior exactly.
6. Update `schema/__init__.py` only for names used by `_sqlite_schema.py`.
7. Update `docs/architecture/SQLITE_SCHEMA_SPLIT_MAP.md`.
8. Create the Stage 5E.1 report in Russian.

## 5. REQUIRED DOCS

- `docs/architecture/SQLITE_SCHEMA_SPLIT_MAP.md`
- No user-facing docs.

## 6. TESTS / VERIFICATION

- Baseline before edit: `python3 -m pytest tests/infrastructure/storage/test_storage_sqlite.py -q`
- After edit: `python3 -m pytest tests/infrastructure/storage/test_storage_sqlite.py -q`
- `python3 -m pytest tests/architecture/test_architecture_wrappers.py -q`
- `python3 -m compileall tg_msg_manager`
- `ruff check tg_msg_manager tests`
- `git diff --check`

## 7. REPORT

Create `docs/stages/reports/STAGE_5E_1_SQLITE_SCHEMA_SPLIT_STAGE_2_MIGRATION_HELPER_EXTRACTION_REPORT.md` in Russian.

The report must include:

- delegated functions and destination modules;
- baseline and final verification results;
- confirmation that `_init_db` ordering and `PRAGMA user_version` transitions are unchanged;
- confirmation that SQLite schema behavior, CLI, services, and dataset behavior were preserved;
- skill lines:
  - `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
  - `architecture-guard: applied from .skills/architecture-guard/SKILL.md`

## 8. COMPLETION CRITERIA

- Only Stage 5E.0-approved helpers moved.
- Storage tests and architecture checks pass or failures are documented as unrelated baseline failures.
- Split map and report are complete.
- `stage-completion-auditor` is applied after the report.
- Lifecycle cleanup is completed according to `AGENTS.md`; do not move unrelated later active files.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Do not continue to Stage 5E.2.
