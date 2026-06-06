# STAGE 5O.5 — DB Export Run Lifecycle Characterization

Status: active task
Stage: 5O.5
Type: implementation
Depends on: completed Stage 5O.0 report and current `DBExportService` behavior

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` and this file before editing.
- Do not start unless `docs/stages/reports/STAGE_5O_0_REFACTORING_GUARDRAILS_REPORT.md` exists or the user explicitly overrides the dependency.
- Use `stage-reviewer` before implementation; if unavailable, read `.skills/stage-reviewer/SKILL.md` manually and state that in the report.
- Use `architecture-guard` because this stage touches services and db-export contracts; if unavailable, read `.skills/architecture-guard/SKILL.md` manually and state that in the report.
- Write a compact plan with no more than 5 bullets before edits.

## 1. PURPOSE

Add focused characterization tests for DB export full/update run lifecycle before extracting orchestration from `DBExportService`.

## 2. FILES TO INSPECT

- `tg_msg_manager/services/db_export/service.py`
- `tg_msg_manager/services/db_export/`
- `tg_msg_manager/services/file_writer.py`
- `tests/services/db_export/`
- `tests/services/test_services.py` only for existing db-export coverage references
- `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_V1.md`
- `docs/development/NON_CHANNEL_CONTRACT_TEST_PLAN.md`

May change:

- focused tests under `tests/services/db_export/`
- `docs/stages/reports/STAGE_5O_5_DB_EXPORT_RUN_LIFECYCLE_CHARACTERIZATION_REPORT.md`
- lifecycle updates required by `AGENTS.md`

## 3. HARD PROHIBITIONS

- Do not change production code in this stage unless an existing test helper requires a mechanical import update.
- Do not change DB export output files, state files, TXT profiles, JSONL format, CLI behavior, or SQLite schema.
- Do not run live Telegram integrations.
- Do not read real export directories, logs, sessions, credentials, or local databases.
- Do not read existing `docs/stages/reports/` files unrelated to this stage.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Add tests covering successful full export run bookkeeping, including start/success/finalization state where current test helpers allow it.
2. Add tests covering update/no-new behavior and unchanged output decisions without using live services.
3. Add tests covering failure path bookkeeping for writer/source failures, including emitted failure result or stored failure status.
4. Add tests around progress callback behavior only if current code exposes it without brittle timing assumptions.
5. Keep fixtures synthetic and local to pytest temp paths.

## 5. REQUIRED DOCS

- Do not update user docs unless tests reveal an existing contract/documentation mismatch.
- Create the required report in Russian.

## 6. TESTS / VERIFICATION

Run:

- `pytest tests/services/db_export`
- `pytest tests/services/test_services.py`
- `python3 -m compileall tg_msg_manager`
- `ruff check tests/services/db_export`

## 7. REPORT

Create `docs/stages/reports/STAGE_5O_5_DB_EXPORT_RUN_LIFECYCLE_CHARACTERIZATION_REPORT.md` in Russian with:

- behaviors characterized;
- gaps intentionally left uncovered and why;
- commands run and results;
- confirmation that production behavior was unchanged.

## 8. COMPLETION CRITERIA

- DB export run lifecycle has focused protective tests.
- Production code behavior is unchanged.
- Required report exists.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Keep final response under 1200 characters unless the user asks otherwise.
