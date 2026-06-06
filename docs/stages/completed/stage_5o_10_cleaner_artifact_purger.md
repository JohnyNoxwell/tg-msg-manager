# STAGE 5O.10 — Cleaner Artifact Purger

Status: completed
Stage: 5O.10
Type: implementation
Depends on: completed Stage 5O.0 report and current cleaner behavior

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` and this file before editing.
- Do not start unless `docs/stages/reports/STAGE_5O_0_REFACTORING_GUARDRAILS_REPORT.md` exists or the user explicitly overrides the dependency.
- Use `stage-reviewer` before implementation; if unavailable, read `.skills/stage-reviewer/SKILL.md` manually and state that in the report.
- Use `architecture-guard` because this stage touches services and destructive cleanup behavior; if unavailable, read `.skills/architecture-guard/SKILL.md` manually and state that in the report.
- Write a compact plan with no more than 5 bullets before edits.

## 1. PURPOSE

Move filesystem artifact deletion out of `CleanerService.purge_user_data` into a focused purger with root-boundary tests, preserving current CLI-visible cleanup behavior.

## 2. FILES TO INSPECT

- `tg_msg_manager/services/cleaner.py`
- cleaner tests under `tests/services/`
- CLI delete command handling in `tg_msg_manager/cli/commands/maintenance.py`
- `docs/development/CLI_CONTRACT.md`

May change:

- `tg_msg_manager/services/cleaner.py`
- new focused cleaner helper module under `tg_msg_manager/services/`
- focused tests under `tests/services/`
- CLI docs only if an existing mismatch is discovered
- `docs/stages/reports/STAGE_5O_10_CLEANER_ARTIFACT_PURGER_REPORT.md`
- lifecycle updates required by `AGENTS.md`

## 3. HARD PROHIBITIONS

- Do not change delete command name, arguments, prompts, output summary, or confirmation behavior.
- Do not change which DB records are deleted.
- Do not expand deletion scope beyond current artifact roots.
- Do not read or delete real export directories, logs, sessions, credentials, media, or local databases.
- Do not change SQLite schema.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Add tempfile-based tests for artifact deletion root boundaries, file matching, directory matching, unmatched names, and sidecar DB cleanup.
2. Extract filesystem deletion into a focused helper that receives explicit roots and user id.
3. Keep `CleanerService.purge_user_data` as orchestration between storage deletion and artifact purger.
4. Preserve current return summary fields and error handling semantics.
5. Run focused cleaner and CLI tests.

## 5. REQUIRED DOCS

- Update CLI docs only if current docs contradict preserved behavior.
- Create the required report in Russian.

## 6. TESTS / VERIFICATION

Run:

- `pytest tests/services -k cleaner`
- `pytest tests/cli -k delete`
- `python3 -m compileall tg_msg_manager`
- `ruff check tg_msg_manager/services/cleaner.py tests/services tests/cli`

## 7. REPORT

Create `docs/stages/reports/STAGE_5O_10_CLEANER_ARTIFACT_PURGER_REPORT.md` in Russian with:

- purger boundary and behavior;
- destructive safety tests added;
- commands run and results;
- confirmation that CLI and SQLite behavior were preserved.

## 8. COMPLETION CRITERIA

- Filesystem deletion is isolated and covered by temp-path tests.
- `CleanerService` remains orchestration-only for this path.
- Required report exists.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Keep final response under 1200 characters unless the user asks otherwise.
