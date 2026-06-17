# STAGE 6F.1 — SQLITE SCHEMA STARTUP PATH SPLIT

Status: active task
Stage: 6F.1
Type: refactor
Depends on: `docs/stages/reports/STAGE_6F_0_SQLITE_SCHEMA_STARTUP_GUARDRAILS_REPORT.md`

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` first.
- Read the Stage 6F.0 report before editing.
- Apply `stage-reviewer` before edits.
- Apply `architecture-guard` because this stage touches SQLite storage/schema startup.
- Write a plan with max 5 bullets before editing.
- Do not start Stage 6F.2 or later.

## 1. PURPOSE

Separate SQLite startup responsibilities so fresh schema bootstrap, compatibility `ensure_*` helpers, index creation, and versioned legacy migrations are easier to reason about.

This is a behavior-preserving refactor. It must not introduce new schema behavior.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/stages/reports/STAGE_6F_0_SQLITE_SCHEMA_STARTUP_GUARDRAILS_REPORT.md`
- `docs/architecture/SQLITE_SCHEMA_SPLIT_MAP.md`
- `docs/development/LOCAL_VERIFICATION_MATRIX.md`
- `tg_msg_manager/infrastructure/storage/_sqlite_schema.py`
- `tg_msg_manager/infrastructure/storage/schema/__init__.py`
- `tg_msg_manager/infrastructure/storage/schema/tables.py`
- `tg_msg_manager/infrastructure/storage/schema/indexes.py`
- `tg_msg_manager/infrastructure/storage/schema/compat.py`
- `tg_msg_manager/infrastructure/storage/schema/migrations.py`
- `tg_msg_manager/infrastructure/storage/schema/backfills.py`
- `tg_msg_manager/infrastructure/storage/schema/inspection.py`
- `tests/infrastructure/storage/test_storage_sqlite.py`
- `tests/infrastructure/storage/test_sqlite_schema_contract.py` if it exists

May create focused modules under:

- `tg_msg_manager/infrastructure/storage/schema/`

May create:

- `docs/stages/reports/STAGE_6F_1_SQLITE_SCHEMA_STARTUP_PATH_SPLIT_REPORT.md`

May update:

- `docs/architecture/SQLITE_SCHEMA_SPLIT_MAP.md`
- `docs/stages/README.md` during lifecycle cleanup only.

## 3. HARD PROHIBITIONS

- Do not add, remove, or rename SQLite tables, columns, indexes, migrations, backup tables, or schema versions.
- Do not change `PRAGMA user_version` transitions.
- Do not change SQL semantics except moving existing behavior behind clearer internal functions.
- Do not touch CLI, services, dataset export, channel export, or public docs.
- Do not add production dependencies.
- Do not combine this with migration registry work.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Introduce explicit internal startup phases with names equivalent to current behavior: current schema creation, compatibility column ensures, index creation, legacy migration execution, final commit.
2. Keep `SQLiteSchemaMixin._init_db()` orchestration-only and small.
3. Move or wrap code only inside `tg_msg_manager/infrastructure/storage/schema/` and `_sqlite_schema.py`.
4. Preserve all existing callback boundaries used by `run_migrations()`.
5. Extend existing tests only where needed to assert phase order and guard against accidental schema drift.
6. Update `docs/architecture/SQLITE_SCHEMA_SPLIT_MAP.md` if module ownership changes.
7. Create the Stage 6F.1 report in Russian.

## 5. REQUIRED DOCS

- `docs/architecture/SQLITE_SCHEMA_SPLIT_MAP.md` if startup ownership or module boundaries change.
- No user-facing docs.

## 6. TESTS / VERIFICATION

- `python3 -m pytest tests/infrastructure/storage/test_storage_sqlite.py -q`
- `python3 -m pytest tests/infrastructure/storage/test_sqlite_schema_contract.py -q` if the file exists
- `python3 -m compileall tg_msg_manager`
- `ruff check tg_msg_manager tests`
- `ruff format --check tg_msg_manager tests`
- `git diff --check`
- `make pre-commit`
- `make verify`

## 7. REPORT

Create `docs/stages/reports/STAGE_6F_1_SQLITE_SCHEMA_STARTUP_PATH_SPLIT_REPORT.md` in Russian.

The report must include:

- startup phases introduced;
- files changed;
- confirmation that no schema behavior, SQL semantics, or `PRAGMA user_version` transitions changed;
- verification results;
- skill lines:
  - `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
  - `architecture-guard: applied from .skills/architecture-guard/SKILL.md`

## 8. COMPLETION CRITERIA

- Startup code has explicit phase boundaries and `SQLiteSchemaMixin._init_db()` remains orchestration-only.
- Stage 6F.0 guardrails still pass.
- No schema behavior change is introduced.
- Required checks pass or tooling/baseline blockers are documented.
- `stage-completion-auditor` is applied after the report.
- Lifecycle cleanup is completed according to `AGENTS.md`; do not move later active 6F files.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Do not start another stage.
