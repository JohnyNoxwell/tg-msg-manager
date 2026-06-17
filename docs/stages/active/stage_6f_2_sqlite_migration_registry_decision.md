# STAGE 6F.2 — SQLITE MIGRATION REGISTRY DECISION

Status: active task
Stage: 6F.2
Type: docs
Depends on: `docs/stages/reports/STAGE_6F_1_SQLITE_SCHEMA_STARTUP_PATH_SPLIT_REPORT.md`

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` first.
- Read the Stage 6F.0 and Stage 6F.1 reports before editing.
- Apply `stage-reviewer` before work.
- Apply `architecture-guard` because this stage evaluates SQLite schema architecture.
- Write a plan with max 5 bullets before editing.
- Do not implement a migration registry in this stage.

## 1. PURPOSE

Decide whether a migration registry is justified after the startup guardrails and startup path split.

This stage is documentation-only unless it creates follow-up stage files explicitly authorized by its decision.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/stages/reports/STAGE_6F_0_SQLITE_SCHEMA_STARTUP_GUARDRAILS_REPORT.md`
- `docs/stages/reports/STAGE_6F_1_SQLITE_SCHEMA_STARTUP_PATH_SPLIT_REPORT.md`
- `docs/architecture/SQLITE_SCHEMA_SPLIT_MAP.md`
- `tg_msg_manager/infrastructure/storage/_sqlite_schema.py`
- `tg_msg_manager/infrastructure/storage/schema/migrations.py`
- `tests/infrastructure/storage/test_storage_sqlite.py`
- `tests/infrastructure/storage/test_sqlite_schema_contract.py` if it exists

May create:

- `docs/architecture/SQLITE_MIGRATION_REGISTRY_DECISION.md`
- `docs/stages/reports/STAGE_6F_2_SQLITE_MIGRATION_REGISTRY_DECISION_REPORT.md`

May create active follow-up stage files only if the decision explicitly says registry implementation is needed.

May update:

- `docs/architecture/README.md`
- `docs/stages/README.md` during lifecycle cleanup only.

## 3. HARD PROHIBITIONS

- Do not edit runtime Python code.
- Do not edit tests.
- Do not change SQLite schema, migrations, indexes, or `PRAGMA user_version`.
- Do not create a migration registry implementation.
- Do not authorize analytics, post-processing, services, CLI, or dataset changes.
- Do not read archive files or unrelated reports.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Review the risk that remains after Stages 6F.0 and 6F.1.
2. Compare two options only: keep the current ordered `run_migrations()` with guardrails, or implement a small registry with version/name/precheck/postcheck/idempotency metadata.
3. Record a decision in `docs/architecture/SQLITE_MIGRATION_REGISTRY_DECISION.md`.
4. If the decision is "defer", state the concrete threshold that would reopen the registry work.
5. If the decision is "implement", create exactly one follow-up active stage file for registry implementation and one optional follow-up active stage file for registry regression expansion.
6. Create the Stage 6F.2 report in Russian.

## 5. REQUIRED DOCS

- Create `docs/architecture/SQLITE_MIGRATION_REGISTRY_DECISION.md`.
- Update `docs/architecture/README.md` to link the decision.

## 6. TESTS / VERIFICATION

- `git diff --check`
- `python3 -m compileall tg_msg_manager`

Do not run full storage tests unless runtime code or tests are accidentally changed. If runtime code or tests change accidentally, revert those changes before completion.

## 7. REPORT

Create `docs/stages/reports/STAGE_6F_2_SQLITE_MIGRATION_REGISTRY_DECISION_REPORT.md` in Russian.

The report must include:

- final decision;
- rationale from Stage 6F.0 and Stage 6F.1 evidence;
- files created or updated;
- verification results;
- whether follow-up active stages were created;
- skill lines:
  - `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
  - `architecture-guard: applied from .skills/architecture-guard/SKILL.md`

## 8. COMPLETION CRITERIA

- A migration-registry decision exists and is linked from architecture docs.
- No runtime code, tests, schema, migrations, or CLI behavior changed.
- Required checks pass or blockers are documented.
- `stage-completion-auditor` is applied after the report.
- Lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Do not start another stage.
