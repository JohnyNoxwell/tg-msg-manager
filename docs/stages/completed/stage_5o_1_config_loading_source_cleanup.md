# STAGE 5O.1 — Config Loading Source Cleanup

Status: active task
Stage: 5O.1
Type: implementation
Depends on: completed Stage 5O.0 report and current `tg_msg_manager/core/config.py`

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` and this file before editing.
- Do not start unless `docs/stages/reports/STAGE_5O_0_REFACTORING_GUARDRAILS_REPORT.md` exists or the user explicitly overrides the dependency.
- Use `stage-reviewer` before implementation; if unavailable, read `.skills/stage-reviewer/SKILL.md` manually and state that in the report.
- Write a compact plan with no more than 5 bullets before edits.
- Do not read real `config.json`, `.env`, credentials, sessions, exports, logs, screenshots, media, or local databases.

## 1. PURPOSE

Remove the hidden process-environment mutation from config loading while preserving the existing settings names, defaults, aliases, and precedence behavior.

## 2. FILES TO INSPECT

- `tg_msg_manager/core/config.py`
- `tg_msg_manager/core/runtime.py` only if needed to understand path inputs
- `tests/core/test_config.py`
- `docs/development/PR_CHECKLIST.md`

May change:

- `tg_msg_manager/core/config.py`
- `tests/core/test_config.py`
- `docs/stages/reports/STAGE_5O_1_CONFIG_LOADING_SOURCE_CLEANUP_REPORT.md`
- lifecycle updates required by `AGENTS.md`

## 3. HARD PROHIBITIONS

- Do not change setting names, aliases, environment variable names, defaults, validation messages, or config file search behavior.
- Do not read or write real local config files outside pytest temp paths.
- Do not change CLI behavior, SQLite behavior, export formats, or runtime paths.
- Do not introduce new runtime dependencies.
- Do not read existing `docs/stages/reports/` files unrelated to this stage.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Add characterization tests that prove current precedence for explicit init values, environment values, config-file values, and defaults.
2. Add a test that calls `load_settings` with a temp config file and asserts no synthetic `TG_*` keys leak into `os.environ` after success and after validation failure.
3. Replace temporary `os.environ` injection with an explicit settings source or local value merge that keeps the same precedence and aliases.
4. Keep `load_settings(path)` and public `settings` access compatible.
5. Run focused tests and fix only regressions caused by this stage.

## 5. REQUIRED DOCS

- Update docs only if documented config precedence changes; behavior changes are not expected.
- Create the required report in Russian.

## 6. TESTS / VERIFICATION

Run:

- `pytest tests/core/test_config.py`
- `python3 -m compileall tg_msg_manager`
- `ruff check tg_msg_manager/core tests/core/test_config.py`

## 7. REPORT

Create `docs/stages/reports/STAGE_5O_1_CONFIG_LOADING_SOURCE_CLEANUP_REPORT.md` in Russian with:

- config behavior preserved;
- environment mutation removed or exact blocker documented;
- tests added/updated;
- commands run and results.

## 8. COMPLETION CRITERIA

- No real credentials or local config artifacts were read.
- Config precedence tests pass or blockers are documented.
- Required report exists.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Keep final response under 1200 characters unless the user asks otherwise.
