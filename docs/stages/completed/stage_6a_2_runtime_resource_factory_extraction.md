# STAGE 6A.2 — Runtime Resource Factory Extraction

Status: active task
Stage: 6A.2
Type: implementation
Depends on: `docs/stages/reports/STAGE_6A_1_APPLICATION_RUNTIME_BOUNDARY_GUARDRAILS_REPORT.md`

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` and this file before editing.
- Do not start unless the Stage 6A.1 report exists or the user explicitly overrides the dependency.
- Use `stage-reviewer` before implementation; if unavailable, read `.skills/stage-reviewer/SKILL.md` manually and state that in the report.
- Use `architecture-guard` because this stage moves runtime construction out of CLI; if unavailable, read `.skills/architecture-guard/SKILL.md` manually and state that in the report.
- Write a compact plan with no more than 5 bullets before edits.

## 1. PURPOSE

Extract pure construction helpers for process, storage, and Telegram client resources from `CLIContext` without moving lifecycle behavior yet.

## 2. FILES TO INSPECT

- `docs/stages/reports/STAGE_6A_0_CLI_RUNTIME_BOUNDARY_PRECHECK_REPORT.md`
- `docs/stages/reports/STAGE_6A_1_APPLICATION_RUNTIME_BOUNDARY_GUARDRAILS_REPORT.md`
- `tg_msg_manager/cli/__init__.py`
- `tg_msg_manager/core/runtime.py`
- `tg_msg_manager/core/process.py`
- `tg_msg_manager/core/telegram/client.py`
- `tg_msg_manager/infrastructure/storage/sqlite.py`
- `tests/cli/test_cli.py`
- `tests/architecture/`

May change:

- `tg_msg_manager/application/__init__.py`
- `tg_msg_manager/application/resources.py`
- `tg_msg_manager/cli/__init__.py` only for mechanical delegation to the new factory
- focused tests under `tests/cli/` or `tests/architecture/`
- `docs/stages/reports/STAGE_6A_2_RUNTIME_RESOURCE_FACTORY_EXTRACTION_REPORT.md`
- lifecycle updates required by `AGENTS.md`

## 3. HARD PROHIBITIONS

- Do not move connect/disconnect, lock acquire/release, storage start/close, stdout/stderr rendering, login error rendering, or emergency export behavior in this stage.
- Do not change CLI commands, flags, defaults, prompts, output, exit codes, or no-client command behavior.
- Do not change SQLite schema, storage SQL, dataset/export formats, state files, retry behavior, or scheduler behavior.
- Do not import CLI modules from the new application/runtime module.
- Do not add feature logic to protected service facades or compatibility wrappers.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Create `tg_msg_manager/application/resources.py` with a focused factory for constructing `ProcessManager`, `SQLiteStorage`, and `TelethonClientWrapper` from `AppRuntime` and `needs_client`.
2. Preserve the current session path resolution exactly.
3. Update `CLIContext.__init__` or `initialize` only to call the factory while keeping existing public attributes.
4. Add focused tests proving the factory is used and the constructed paths/options match current behavior.
5. Confirm no-client commands still avoid Telegram client construction.

## 5. REQUIRED DOCS

- Do not update user docs.
- Update architecture docs only if the implementation must deviate from Stage 6A.1.
- Create the required report in Russian.

## 6. TESTS / VERIFICATION

Run:

- `pytest tests/cli/test_cli.py`
- `pytest tests/architecture`
- `python3 -m compileall tg_msg_manager`
- `ruff check tg_msg_manager tests/cli tests/architecture`
- `git diff --check`

## 7. REPORT

Create `docs/stages/reports/STAGE_6A_2_RUNTIME_RESOURCE_FACTORY_EXTRACTION_REPORT.md` in Russian with:

- factory created;
- exact behavior preserved;
- tests/checks run and results;
- any deliberate compatibility attributes left on `CLIContext`;
- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md` if applied manually;
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md` if applied manually.

## 8. COMPLETION CRITERIA

- Runtime resource construction is delegated outside `CLIContext`.
- Lifecycle remains unchanged.
- CLI behavior and no-client behavior are preserved by tests.
- Required report exists.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Keep final response under 1200 characters unless the user asks otherwise.
