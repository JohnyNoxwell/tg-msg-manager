# STAGE 5O.14 — Test Suite Component Split

Status: completed
Stage: 5O.14
Type: implementation
Depends on: completed Stage 5O.0 report and current test layout

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` and this file before editing.
- Do not start unless `docs/stages/reports/STAGE_5O_0_REFACTORING_GUARDRAILS_REPORT.md` exists or the user explicitly overrides the dependency.
- Use `stage-reviewer` before implementation; if unavailable, read `.skills/stage-reviewer/SKILL.md` manually and state that in the report.
- Write a compact plan with no more than 5 bullets before edits.

## 1. PURPOSE

Move one small cluster of omnibus tests into a focused component test file and remove one fragile temp-file pattern, without changing production behavior.

## 2. FILES TO INSPECT

- `tests/services/test_services.py`
- `tests/cli/test_cli.py`
- `tests/infrastructure/storage/test_storage_sqlite.py`
- `tests/services/sync/test_sync_system.py`
- `pyproject.toml` only if test discovery behavior must be verified

May change:

- one selected test file from the list above
- one new focused test file under the matching `tests/` subtree
- `docs/stages/reports/STAGE_5O_14_TEST_SUITE_COMPONENT_SPLIT_REPORT.md`
- lifecycle updates required by `AGENTS.md`

## 3. HARD PROHIBITIONS

- Do not rewrite the full test suite.
- Do not change production code.
- Do not weaken or delete behavioral assertions.
- Do not change pytest configuration unless the selected move proves it is required.
- Do not read private artifacts, exports, sessions, logs, media, or local databases.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Select exactly one small coherent test group from an omnibus file, preferably context resolver, sync scanner, CLI parser, or cleaner behavior.
2. Move that group into a focused test file with the same assertions and fixtures.
3. If touching `tests/services/sync/test_sync_system.py`, replace repo-root `test_sync.db` usage with `tmp_path` while preserving assertions.
4. Remove unnecessary `sys.path.append` only from files touched in this stage and only if imports still work.
5. Run the moved test file and the original file to prove no coverage was lost.

## 5. REQUIRED DOCS

- No user docs required.
- Create the required report in Russian.

## 6. TESTS / VERIFICATION

Run:

- focused pytest command for the new test file
- pytest command for the original touched test file
- `python3 -m compileall tg_msg_manager`
- `ruff check` for touched test files

## 7. REPORT

Create `docs/stages/reports/STAGE_5O_14_TEST_SUITE_COMPONENT_SPLIT_REPORT.md` in Russian with:

- selected test group;
- files moved/created;
- commands run and results;
- confirmation that production behavior was unchanged.

## 8. COMPLETION CRITERIA

- Exactly one coherent test group is moved or the stage reports a blocker.
- Original assertions remain present.
- Required report exists.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Keep final response under 1200 characters unless the user asks otherwise.
