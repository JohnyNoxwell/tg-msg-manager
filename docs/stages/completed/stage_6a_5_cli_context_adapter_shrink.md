# STAGE 6A.5 — CLIContext Adapter Shrink

Status: completed
Stage: 6A.5
Type: implementation
Depends on: `docs/stages/reports/STAGE_6A_4_RUNTIME_SESSION_LIFECYCLE_EXTRACTION_REPORT.md`

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` and this file before editing.
- Do not start unless the Stage 6A.4 report exists or the user explicitly overrides the dependency.
- Use `stage-reviewer` before implementation; if unavailable, read `.skills/stage-reviewer/SKILL.md` manually and state that in the report.
- Use `architecture-guard` because this stage changes CLI adapter boundaries; if unavailable, read `.skills/architecture-guard/SKILL.md` manually and state that in the report.
- Write a compact plan with no more than 5 bullets before edits.

## 1. PURPOSE

Reduce `CLIContext` to a compatibility adapter over the application runtime session, with no direct resource or service construction.

## 2. FILES TO INSPECT

- `docs/stages/reports/STAGE_6A_4_RUNTIME_SESSION_LIFECYCLE_EXTRACTION_REPORT.md`
- `tg_msg_manager/application/resources.py`
- `tg_msg_manager/application/services.py`
- `tg_msg_manager/application/session.py`
- `tg_msg_manager/cli/__init__.py`
- `tg_msg_manager/cli_commands.py`
- `tg_msg_manager/cli_menu.py`
- `tg_msg_manager/cli_support.py`
- `tests/cli/test_cli.py`
- `tests/cli/`
- `tests/architecture/`

May change:

- `tg_msg_manager/cli/__init__.py`
- `tg_msg_manager/application/resources.py` only for missing adapter accessors
- `tg_msg_manager/application/services.py` only for missing adapter accessors
- `tg_msg_manager/application/session.py` only for missing adapter accessors
- focused tests under `tests/cli/` or `tests/architecture/`
- `docs/stages/reports/STAGE_6A_5_CLI_CONTEXT_ADAPTER_SHRINK_REPORT.md`
- lifecycle updates required by `AGENTS.md`

## 3. HARD PROHIBITIONS

- Do not remove `CLIContext` or rename its public attributes in this stage.
- Do not rewrite command/menu handlers beyond minimal compatibility adjustments.
- Do not change CLI behavior, no-client command behavior, login behavior, emergency export behavior, output text, prompts, exit codes, or command routing.
- Do not change SQLite schema, storage SQL, dataset/export formats, state files, retry behavior, scheduler behavior, or package metadata.
- Do not add feature logic to CLI, services, protected facades, or compatibility wrappers.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Remove direct construction of process manager, storage, Telegram client, and services from `CLIContext`.
2. Make `CLIContext` hold the application runtime session and expose compatibility attributes from that session.
3. Keep `active_uid` and emergency export behavior working exactly as before.
4. Add a focused architecture or CLI test that fails if `CLIContext` constructs the extracted runtime/service classes directly again.
5. Update existing CLI tests to assert behavior rather than duplicated construction internals where needed.

## 5. REQUIRED DOCS

- Do not update user docs.
- Update architecture docs only if Stage 6A.1 boundary text becomes inaccurate.
- Create the required report in Russian.

## 6. TESTS / VERIFICATION

Run:

- `pytest tests/cli`
- `pytest tests/architecture`
- `python3 -m compileall tg_msg_manager`
- `ruff check tg_msg_manager tests/cli tests/architecture`
- `git diff --check`

## 7. REPORT

Create `docs/stages/reports/STAGE_6A_5_CLI_CONTEXT_ADAPTER_SHRINK_REPORT.md` in Russian with:

- direct construction removed from `CLIContext`;
- compatibility attributes retained;
- behavior-preservation evidence;
- tests/checks run and results;
- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md` if applied manually;
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md` if applied manually.

## 8. COMPLETION CRITERIA

- `CLIContext` is a thin adapter over the application runtime session.
- Existing command/menu handlers continue to work.
- Direct construction regression guard exists.
- Required report exists.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Keep final response under 1200 characters unless the user asks otherwise.
