# STAGE 5O.6 — DB Export Run Coordinator Extraction

Status: active task
Stage: 5O.6
Type: implementation
Depends on: completed Stage 5O.5 report and current `tg_msg_manager/services/db_export/service.py`

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` and this file before editing.
- Do not start unless `docs/stages/reports/STAGE_5O_5_DB_EXPORT_RUN_LIFECYCLE_CHARACTERIZATION_REPORT.md` exists or the user explicitly overrides the dependency.
- Use `stage-reviewer` before implementation; if unavailable, read `.skills/stage-reviewer/SKILL.md` manually and state that in the report.
- Use `architecture-guard` because this stage touches a protected service facade; if unavailable, read `.skills/architecture-guard/SKILL.md` manually and state that in the report.
- Write a compact plan with no more than 5 bullets before edits.

## 1. PURPOSE

Move DB export full/update run orchestration out of the protected `DBExportService` facade into focused internal coordinators while preserving public service methods and output behavior.

## 2. FILES TO INSPECT

- `tg_msg_manager/services/db_export/service.py`
- `tg_msg_manager/services/db_export/`
- `tg_msg_manager/services/file_writer.py`
- `tests/services/db_export/`
- `docs/architecture/DB_EXPORT_SERVICE_SPLIT_MAP.md`
- `docs/development/FACADE_SIZE_BASELINE.md`

May change:

- `tg_msg_manager/services/db_export/service.py` only for mechanical wiring/delegation
- new focused modules under `tg_msg_manager/services/db_export/`
- tests under `tests/services/db_export/`
- `docs/development/FACADE_SIZE_BASELINE.md` if facade size meaningfully changes
- `docs/stages/reports/STAGE_5O_6_DB_EXPORT_RUN_COORDINATOR_EXTRACTION_REPORT.md`
- lifecycle updates required by `AGENTS.md`

## 3. HARD PROHIBITIONS

- Do not change `DBExportService` public method names, parameters, defaults, return values, event semantics, or CLI-visible results.
- Do not change DB export output formats, filenames, state files, incremental/update behavior, force behavior, or no-new-work behavior.
- Do not add raw SQL to services.
- Do not change SQLite schema or storage contracts.
- Do not read existing `docs/stages/reports/` files unrelated to this stage, except the Stage 5O.5 dependency report.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Extract full export run sequencing into a focused internal coordinator/helper that receives existing collaborators explicitly.
2. Extract update export run sequencing into a focused internal coordinator/helper only if it can be done without changing observable behavior.
3. Move duplicated progress tracking/failure finalization into a small helper if this reduces duplication without hiding control flow.
4. Keep `DBExportService` as a thin public facade that constructs/wires collaborators and delegates.
5. Update or add tests only for behavior that moved; do not broaden scope to writer internals.

## 5. REQUIRED DOCS

- Update `docs/development/FACADE_SIZE_BASELINE.md` if line-count or facade-size guidance changes.
- Do not update user-facing docs unless behavior changes; behavior changes are not allowed.
- Create the required report in Russian.

## 6. TESTS / VERIFICATION

Run:

- `pytest tests/services/db_export`
- `pytest tests/services/test_services.py`
- `python3 -m compileall tg_msg_manager`
- `ruff check tg_msg_manager/services/db_export tests/services/db_export`

## 7. REPORT

Create `docs/stages/reports/STAGE_5O_6_DB_EXPORT_RUN_COORDINATOR_EXTRACTION_REPORT.md` in Russian with:

- modules/classes extracted;
- protected facade changes and why they are mechanical;
- tests run and results;
- confirmation that CLI, SQLite, and output contracts were preserved.

## 8. COMPLETION CRITERIA

- `DBExportService` contains only orchestration/wiring for the moved paths.
- Existing DB export behavior is preserved by tests.
- Required report exists.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Keep final response under 1200 characters unless the user asks otherwise.
