# STAGE 5O.2 — i18n Parity Guard

Status: active task
Stage: 5O.2
Type: implementation
Depends on: completed Stage 5O.0 report and current `tg_msg_manager/i18n.py`

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` and this file before editing.
- Do not start unless `docs/stages/reports/STAGE_5O_0_REFACTORING_GUARDRAILS_REPORT.md` exists or the user explicitly overrides the dependency.
- Use `stage-reviewer` before implementation; if unavailable, read `.skills/stage-reviewer/SKILL.md` manually and state that in the report.
- Write a compact plan with no more than 5 bullets before edits.

## 1. PURPOSE

Add protective tests for translation key parity and placeholder compatibility before any future i18n split or cleanup.

## 2. FILES TO INSPECT

- `tg_msg_manager/i18n.py`
- existing tests under `tests/` that reference `i18n`

May change:

- tests under `tests/core/` or another existing i18n test location
- `docs/stages/reports/STAGE_5O_2_I18N_PARITY_GUARD_REPORT.md`
- lifecycle updates required by `AGENTS.md`

## 3. HARD PROHIBITIONS

- Do not change visible user-facing text in this stage unless a test reveals an actual missing key or broken placeholder.
- Do not split `tg_msg_manager/i18n.py` in this stage.
- Do not change CLI output contracts.
- Do not add runtime dependencies.
- Do not read existing `docs/stages/reports/` files unrelated to this stage.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Add a test that verifies every supported locale has the same translation key set.
2. Add a test that verifies each translated string has the same named format placeholders as the corresponding fallback locale string.
3. If an existing mismatch is found, fix only the missing key or placeholder mismatch required to make the translations internally consistent.
4. Keep the public translation helper API unchanged.

## 5. REQUIRED DOCS

- No user docs are required unless visible text changes.
- Create the required report in Russian.

## 6. TESTS / VERIFICATION

Run:

- `pytest tests/core`
- `python3 -m compileall tg_msg_manager`
- `ruff check tg_msg_manager/i18n.py tests/core`

## 7. REPORT

Create `docs/stages/reports/STAGE_5O_2_I18N_PARITY_GUARD_REPORT.md` in Russian with:

- parity checks added;
- any translation correction made;
- commands run and results;
- confirmation that CLI behavior was preserved.

## 8. COMPLETION CRITERIA

- Translation key and placeholder parity are covered by tests.
- Required verification is run or blockers are documented.
- Required report exists.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Keep final response under 1200 characters unless the user asks otherwise.
