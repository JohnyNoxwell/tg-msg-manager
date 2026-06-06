# STAGE 5O.13 — Storage Compatibility Guardrails

Status: active task
Stage: 5O.13
Type: implementation
Depends on: completed Stage 5O.0 report and current storage compatibility contracts

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` and this file before editing.
- Do not start unless `docs/stages/reports/STAGE_5O_0_REFACTORING_GUARDRAILS_REPORT.md` exists or the user explicitly overrides the dependency.
- Use `stage-reviewer` before implementation; if unavailable, read `.skills/stage-reviewer/SKILL.md` manually and state that in the report.
- Use `architecture-guard` because this stage touches storage compatibility boundaries; if unavailable, read `.skills/architecture-guard/SKILL.md` manually and state that in the report.
- Write a compact plan with no more than 5 bullets before edits.

## 1. PURPOSE

Prevent new growth in broad storage compatibility surfaces while avoiding SQLite schema, migration, or public import-path changes.

## 2. FILES TO INSPECT

- `tg_msg_manager/infrastructure/storage/interface.py`
- `tg_msg_manager/infrastructure/storage/contracts/`
- `tg_msg_manager/infrastructure/storage/_sqlite_write_path.py`
- `tg_msg_manager/infrastructure/storage/_sqlite_sync_state.py`
- `tg_msg_manager/infrastructure/storage/records.py`
- `tests/architecture/`
- `tests/infrastructure/storage/`
- `docs/architecture/STORAGE_CONTRACT_SPLIT_MAP.md`
- `docs/architecture/SQLITE_WRITE_PATH_SPLIT_MAP.md`

May change:

- architecture/storage tests
- docs listed above only if current guidance is stale
- `docs/stages/reports/STAGE_5O_13_STORAGE_COMPATIBILITY_GUARDRAILS_REPORT.md`
- lifecycle updates required by `AGENTS.md`

## 3. HARD PROHIBITIONS

- Do not change SQLite schema, migrations, SQL text/order, `user_version`, or storage table layout.
- Do not remove or rename compatibility wrappers or public import paths.
- Do not move business logic into wrappers.
- Do not change storage behavior or exported records.
- Do not read existing `docs/stages/reports/` files unrelated to this stage.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Add tests or architecture checks that discourage new service code from depending on `BaseStorage` when a narrow protocol exists.
2. Add checks that storage compatibility wrapper files do not import services or CLI modules.
3. Document any current broad compatibility surface that must remain for backward compatibility.
4. If docs are stale about current split boundaries, update only the affected split-map lines.
5. Do not split storage code in this stage.

## 5. REQUIRED DOCS

- Update storage split-map docs only for factual boundary corrections.
- Create the required report in Russian.

## 6. TESTS / VERIFICATION

Run:

- `pytest tests/architecture`
- `pytest tests/infrastructure/storage`
- `python3 -m compileall tg_msg_manager`
- `ruff check tests/architecture tests/infrastructure/storage`

## 7. REPORT

Create `docs/stages/reports/STAGE_5O_13_STORAGE_COMPATIBILITY_GUARDRAILS_REPORT.md` in Russian with:

- guardrails added;
- compatibility surfaces intentionally preserved;
- commands run and results;
- confirmation that SQLite schema and storage behavior were unchanged.

## 8. COMPLETION CRITERIA

- Storage compatibility growth is guarded by tests or documented blockers.
- No storage schema or behavior changed.
- Required report exists.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Keep final response under 1200 characters unless the user asks otherwise.
