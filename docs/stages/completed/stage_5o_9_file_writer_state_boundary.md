# STAGE 5O.9 — File Writer State Boundary

Status: completed
Stage: 5O.9
Type: implementation
Depends on: completed Stage 5O.0 report and current file writer tests

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` and this file before editing.
- Do not start unless `docs/stages/reports/STAGE_5O_0_REFACTORING_GUARDRAILS_REPORT.md` exists or the user explicitly overrides the dependency.
- Use `stage-reviewer` before implementation; if unavailable, read `.skills/stage-reviewer/SKILL.md` manually and state that in the report.
- Use `architecture-guard` because this stage touches shared service writer behavior; if unavailable, read `.skills/architecture-guard/SKILL.md` manually and state that in the report.
- Write a compact plan with no more than 5 bullets before edits.

## 1. PURPOSE

Isolate file writer state persistence/recovery and rotation decisions from the shared `FileRotateWriter` class without changing writer-state files or export output.

## 2. FILES TO INSPECT

- `tg_msg_manager/services/file_writer.py`
- `tg_msg_manager/services/db_export/payload_writer.py`
- private archive writer usage under `tg_msg_manager/services/private_archive/`
- writer tests under `tests/services/`
- DB export tests under `tests/services/db_export/`

May change:

- `tg_msg_manager/services/file_writer.py`
- new focused writer helper modules under `tg_msg_manager/services/`
- focused tests under `tests/services/`
- `docs/stages/reports/STAGE_5O_9_FILE_WRITER_STATE_BOUNDARY_REPORT.md`
- lifecycle updates required by `AGENTS.md`

## 3. HARD PROHIBITIONS

- Do not change writer-state filename, JSON keys, rotation naming, append behavior, cleanup behavior, or telemetry event fields.
- Do not change DB export output formats or private archive output formats.
- Do not change SQLite behavior or CLI behavior.
- Do not add new runtime dependencies.
- Do not read real export directories or private artifacts.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Add focused tests for missing/corrupt writer state and existing part-file recovery using pytest temp paths.
2. Extract state load/save/recovery into a small helper with explicit inputs and outputs.
3. Extract rotation decision logic only if it can be tested without changing naming behavior.
4. Keep `FileRotateWriter` public constructor and methods compatible.
5. Run DB export and writer tests to catch shared behavior regressions.

## 5. REQUIRED DOCS

- Update docs only if writer-state documented behavior was already inaccurate; no behavior change is expected.
- Create the required report in Russian.

## 6. TESTS / VERIFICATION

Run:

- `pytest tests/services/db_export`
- `pytest tests/services -k file_writer`
- `python3 -m compileall tg_msg_manager`
- `ruff check tg_msg_manager/services/file_writer.py tests/services`

## 7. REPORT

Create `docs/stages/reports/STAGE_5O_9_FILE_WRITER_STATE_BOUNDARY_REPORT.md` in Russian with:

- state/rotation helpers extracted;
- recovery edge cases covered;
- commands run and results;
- confirmation that writer-state and output contracts were preserved.

## 8. COMPLETION CRITERIA

- Writer state logic is covered by focused tests.
- Public writer behavior is unchanged.
- Required report exists.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Keep final response under 1200 characters unless the user asks otherwise.
