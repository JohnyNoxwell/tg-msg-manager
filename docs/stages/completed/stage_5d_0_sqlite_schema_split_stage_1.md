# STAGE 5D.0 — SQLITE SCHEMA SPLIT STAGE 1

Status: completed
Stage: 5D.0
Type: storage refactor / split-only
Depends on: all Stage 5C tasks complete; `docs/architecture/SQLITE_SCHEMA_SPLIT_MAP.md`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.

Execute Stage 5D.0 only.

Goal:
Perform the first mechanical split of SQLite schema responsibilities without changing schema behavior.

Do not start later stages.
Do not change table/index SQL semantics, migration order, migration behavior, `PRAGMA user_version`, storage contracts, CLI behavior, or dataset behavior.
Use `AGENTS.md` compact output format.

## 1. PURPOSE

Reduce `tg_msg_manager/infrastructure/storage/_sqlite_schema.py` by extracting low-risk schema creation and inspection helpers into focused infrastructure modules.

Stage 1 scope is limited to:
- table creation helpers;
- index creation helpers;
- schema inspection helpers.

Migrations, compatibility rewrites, backfills, and `migrate_existing_links` stay in `_sqlite_schema.py` for later explicit stages.

## 2. FILES TO INSPECT

Required:
- `AGENTS.md`
- this stage file
- `docs/architecture/README.md`
- `docs/architecture/ARCHITECTURE_RULES.md`
- `docs/architecture/SQLITE_SCHEMA_SPLIT_MAP.md`
- `tg_msg_manager/infrastructure/storage/_sqlite_schema.py`
- `tg_msg_manager/infrastructure/storage/sqlite.py`
- `tests/infrastructure/storage/test_storage_sqlite.py`
- `tests/architecture/test_architecture_wrappers.py`

May create/change:
- `tg_msg_manager/infrastructure/storage/schema/__init__.py`
- `tg_msg_manager/infrastructure/storage/schema/tables.py`
- `tg_msg_manager/infrastructure/storage/schema/indexes.py`
- `tg_msg_manager/infrastructure/storage/schema/inspection.py`
- `tg_msg_manager/infrastructure/storage/_sqlite_schema.py`
- `docs/architecture/SQLITE_SCHEMA_SPLIT_MAP.md`
- `docs/stages/reports/STAGE_5D_0_SQLITE_SCHEMA_SPLIT_STAGE_1_REPORT.md`
- `docs/stages/README.md`
- this stage file location during lifecycle cleanup

Do not change:
- `tg_msg_manager/infrastructure/storage/sqlite.py` unless an import/wiring change is strictly required;
- storage contracts;
- services or CLI modules;
- migrations/backfills/compat modules;
- unrelated tests or docs.

## 3. HARD PROHIBITIONS

- Do not change SQLite schema behavior.
- Do not add, remove, rename, or reorder tables, columns, indexes, migrations, backup tables, or `PRAGMA user_version` transitions.
- Do not move `_run_migrations`, compatibility migrations, backfills, or `migrate_existing_links` in this stage.
- Do not introduce service or CLI imports into infrastructure storage.
- Do not import infrastructure from core/domain modules.
- Do not add raw SQL outside `tg_msg_manager/infrastructure/storage/`.
- Do not change public storage method names.
- Do not change runtime export, validation, retry, scheduler, delete, or CLI behavior.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Apply required skills before editing.
   - Apply `stage-reviewer` from `.skills/stage-reviewer/SKILL.md`.
   - Apply `architecture-guard` from `.skills/architecture-guard/SKILL.md`.
   - Record both in the report.

2. Baseline current behavior.
   - Run `python3 -m pytest tests/infrastructure/storage/test_storage_sqlite.py -q`.
   - Inspect the methods named in Stage 1 scope.
   - Do not edit yet.

3. Create schema package.
   - Add `tg_msg_manager/infrastructure/storage/schema/__init__.py`.
   - Add focused functions in `tables.py`, `indexes.py`, and `inspection.py`.
   - Keep SQL text and condition checks semantically identical.
   - Keep modules infrastructure-only.

4. Convert mixin methods to delegation.
   - In `_sqlite_schema.py`, preserve public/internal method names used by tests or migrations.
   - Delegate `_create_tables`, `_create_indexes`, `_create_context_link_indexes`, `_create_target_link_indexes`, `_create_missing_reply_ref_indexes`, `_create_export_runs_table`, `_create_export_runs_indexes`, `_create_missing_reply_refs_table`, `_context_links_has_chat_scope`, `_target_links_has_chat_scope`, `_target_links_has_metadata`, `_table_exists`, and `_sync_targets_has_composite_primary_key`.
   - Do not change `_init_db` ordering.

5. Verify and document.
   - Run section 6 checks.
   - Update `SQLITE_SCHEMA_SPLIT_MAP.md` with Stage 1 completed extraction boundaries.
   - Create the Russian report.
   - Apply `stage-completion-auditor` from `.skills/stage-completion-auditor/SKILL.md` before claiming complete.
   - Perform lifecycle cleanup only after report exists.

## 5. REQUIRED DOCS

Required:
- `docs/architecture/SQLITE_SCHEMA_SPLIT_MAP.md`
- `docs/stages/reports/STAGE_5D_0_SQLITE_SCHEMA_SPLIT_STAGE_1_REPORT.md`
- `docs/stages/README.md` during lifecycle cleanup

Do not update user-facing docs because no CLI or user behavior should change.

## 6. TESTS / VERIFICATION

Run:
- `python3 -m pytest tests/infrastructure/storage/test_storage_sqlite.py -q`
- `python3 -m pytest tests/architecture/test_architecture_wrappers.py -q`
- `python3 -m compileall tg_msg_manager`
- `ruff check tg_msg_manager tests`
- `git diff --check`

If any storage test fails, stop and report. Do not continue to later stages.

## 7. REPORT

Create `docs/stages/reports/STAGE_5D_0_SQLITE_SCHEMA_SPLIT_STAGE_1_REPORT.md` in Russian.

Include:
- exact functions moved or delegated;
- exact files changed;
- checks run;
- confirmation that `_init_db` ordering and migration behavior were unchanged;
- confirmation that SQLite schema, `PRAGMA user_version`, CLI, dataset formats, and service behavior were unchanged;
- skill application:
  - `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
  - `architecture-guard: applied from .skills/architecture-guard/SKILL.md`
  - `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`

## 8. COMPLETION CRITERIA

- Schema Stage 1 modules exist under `tg_msg_manager/infrastructure/storage/schema/`.
- `_sqlite_schema.py` remains the compatibility mixin surface.
- Migration/backfill/compat behavior stays in `_sqlite_schema.py`.
- Focused storage and architecture tests pass or blocker is recorded.
- Required report exists.
- lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- No full diffs.
- No SQL excerpts longer than necessary.
- No markdown tables in the final response.
