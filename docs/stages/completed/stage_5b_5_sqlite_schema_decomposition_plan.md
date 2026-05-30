# STAGE 5B.5 — SQLite Schema Decomposition Plan

Status: active task
Stage: 5B.5
Type: docs
Depends on: `tg_msg_manager/infrastructure/storage/_sqlite_schema.py`; `docs/architecture/README.md`

---

## 0. CODEX ENTRY CONTRACT

1. Read `AGENTS.md`.
2. Read this stage file only.
3. Apply `stage-reviewer` before work. If no tool exists, read `.skills/stage-reviewer/SKILL.md`.
4. Apply `architecture-guard` because this stage touches architecture docs. If no tool exists, read `.skills/architecture-guard/SKILL.md`.
5. Do not implement schema decomposition in this stage.
6. Do not start any other active 5B stage.

## 1. PURPOSE

Create a precise decomposition map for `tg_msg_manager/infrastructure/storage/_sqlite_schema.py` before any future schema refactor.

Current maintainability risk:

- `_sqlite_schema.py` is large and mixes table creation, index creation, migrations, compatibility migration helpers, and backfills.

This stage is documentation-only.

## 2. FILES TO INSPECT

Inspect only:

- `AGENTS.md`
- `docs/architecture/README.md`
- `docs/architecture/ARCHITECTURE_RULES.md`
- `docs/architecture/SQLITE_WRITE_PATH_SPLIT_MAP.md`
- `docs/architecture/STORAGE_CONTRACT_SPLIT_MAP.md`
- `tg_msg_manager/infrastructure/storage/_sqlite_schema.py`
- `tg_msg_manager/infrastructure/storage/sqlite.py`
- `tg_msg_manager/infrastructure/storage/write/`
- `tg_msg_manager/infrastructure/storage/read/`
- `tests/infrastructure/storage/test_storage_sqlite.py`

May create:

- `docs/architecture/SQLITE_SCHEMA_SPLIT_MAP.md`
- `docs/stages/reports/STAGE_5B_5_SQLITE_SCHEMA_DECOMPOSITION_PLAN_REPORT.md`

May update:

- `docs/architecture/README.md`
- `docs/stages/README.md` during lifecycle cleanup only.

## 3. HARD PROHIBITIONS

- Do not edit runtime Python code.
- Do not edit tests.
- Do not change SQLite schema, migrations, indexes, or `PRAGMA user_version`.
- Do not move functions.
- Do not create empty Python packages.
- Do not authorize schema changes through docs.
- Do not read archive files or unrelated historical reports.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Map `_sqlite_schema.py` responsibilities by exact function names and line ranges.
2. Propose future module boundaries without moving code.
3. Mark each proposed future module as one of:
   - table creation;
   - index creation;
   - versioned migrations;
   - compatibility migration helpers;
   - backfills;
   - schema inspection helpers.
4. Record hard future constraints:
   - no schema behavior change in a split-only stage;
   - migration order must remain identical;
   - `PRAGMA user_version` transitions must remain identical;
   - storage must not import services.
5. Update `docs/architecture/README.md` to link the new map.

## 5. REQUIRED DOCS

Create:

- `docs/architecture/SQLITE_SCHEMA_SPLIT_MAP.md`
- `docs/stages/reports/STAGE_5B_5_SQLITE_SCHEMA_DECOMPOSITION_PLAN_REPORT.md`

Update:

- `docs/architecture/README.md`

## 6. TESTS / VERIFICATION

Run:

- `git diff --check`
- `python3 -m compileall tg_msg_manager`

Do not run storage tests unless runtime code changes accidentally occur. If runtime code changes occur, revert them before completion.

## 7. REPORT

Report in Russian:

- docs created/updated;
- confirmation no runtime code changed;
- checks run;
- `stage-reviewer` and `architecture-guard` application.

## 8. COMPLETION CRITERIA

- Split map exists and is linked from architecture README.
- No runtime code, tests, schema, or migrations changed.
- Future split constraints are explicit.
- Required checks pass or blockers are documented.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md` final structure, be in Russian, and stay under 1200 characters.
