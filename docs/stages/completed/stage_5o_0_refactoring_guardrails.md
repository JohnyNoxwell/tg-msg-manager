# STAGE 5O.0 — Refactoring Guardrails

Status: active task
Stage: 5O.0
Type: implementation
Depends on: current architecture rules and existing architecture tests

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` and this file before editing.
- Use `stage-reviewer` before implementation; if unavailable, read `.skills/stage-reviewer/SKILL.md` manually and state that in the report.
- Use `architecture-guard` because this stage touches architecture rules/tests; if unavailable, read `.skills/architecture-guard/SKILL.md` manually and state that in the report.
- Do not inspect private artifacts, real credentials, sessions, exports, logs, screenshots, media, or local databases.
- Write a compact plan with no more than 5 bullets before edits.
- Stop if a required guardrail would require runtime behavior changes.

## 1. PURPOSE

Create low-risk automated guardrails before the refactoring sequence starts. This stage must not refactor production code; it protects existing boundaries so later stages cannot accidentally move SQL, CLI parsing, or broad storage dependencies into the wrong layer.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `docs/architecture/README.md`
- `docs/architecture/ARCHITECTURE_RULES.md`
- `docs/development/PR_CHECKLIST.md`
- `tests/architecture/test_architecture_wrappers.py`
- `tests/architecture/`
- `tg_msg_manager/` only through static file/import scans

May change:

- `tests/architecture/test_architecture_wrappers.py`
- new files under `tests/architecture/`
- `docs/stages/reports/STAGE_5O_0_REFACTORING_GUARDRAILS_REPORT.md`
- lifecycle updates required by `AGENTS.md`

## 3. HARD PROHIBITIONS

- Do not change runtime code under `tg_msg_manager/`.
- Do not change CLI flags, defaults, outputs, command names, or parser behavior.
- Do not change SQLite schema, migrations, SQL behavior, storage records, or export formats.
- Do not add feature logic, analytics, OSINT, profiling, LLM behavior, or post-processing behavior.
- Do not read existing `docs/stages/reports/` files unrelated to this stage.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Add or extend architecture tests that statically verify raw SQL keywords are not introduced outside `tg_msg_manager/infrastructure/storage/`, excluding tests and comments only when the test implementation can do so deterministically.
2. Add or extend architecture tests that verify `tg_msg_manager/core` does not import `tg_msg_manager.infrastructure`, and `tg_msg_manager/infrastructure` does not import `tg_msg_manager.services`.
3. Add or extend architecture tests that verify service/core/infrastructure modules do not import `tg_msg_manager.cli` or CLI command modules.
4. Add a narrow test preventing new production code from importing broad storage compatibility interfaces where a narrow contract already exists; if a current exception exists, document it as an explicit allowlist in the test.
5. Keep all scans deterministic, local, and network-free.

## 5. REQUIRED DOCS

- Do not update user docs.
- Update architecture/development docs only if the new tests expose a documented rule mismatch.
- Create the required report in Russian.

## 6. TESTS / VERIFICATION

Run:

- `pytest tests/architecture`
- `python3 -m compileall tg_msg_manager`
- `ruff check tests/architecture`

If a command is unavailable, record the exact reason in the report.

## 7. REPORT

Create `docs/stages/reports/STAGE_5O_0_REFACTORING_GUARDRAILS_REPORT.md` in Russian with:

- files changed;
- guardrails added;
- any explicit allowlist and why it exists;
- commands run and results;
- confirmation that runtime behavior, CLI contracts, SQLite schema, and export formats were preserved.

## 8. COMPLETION CRITERIA

- Architecture guardrails are implemented as tests only.
- Required verification is run or exact blockers are documented.
- Required report exists.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Keep final response under 1200 characters unless the user asks otherwise.
