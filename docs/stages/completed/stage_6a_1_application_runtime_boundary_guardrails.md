# STAGE 6A.1 — Application Runtime Boundary Guardrails

Status: active task
Stage: 6A.1
Type: docs/tests
Depends on: `docs/stages/reports/STAGE_6A_0_CLI_RUNTIME_BOUNDARY_PRECHECK_REPORT.md`

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` and this file before editing.
- Do not start unless the Stage 6A.0 report exists or the user explicitly overrides the dependency.
- Use `stage-reviewer` before implementation; if unavailable, read `.skills/stage-reviewer/SKILL.md` manually and state that in the report.
- Use `architecture-guard` because this stage defines CLI/application/service boundaries; if unavailable, read `.skills/architecture-guard/SKILL.md` manually and state that in the report.
- Write a compact plan with no more than 5 bullets before edits.

## 1. PURPOSE

Define and guard the new application runtime assembly boundary before moving code out of `CLIContext`.

## 2. FILES TO INSPECT

- `docs/stages/reports/STAGE_6A_0_CLI_RUNTIME_BOUNDARY_PRECHECK_REPORT.md`
- `docs/architecture/README.md`
- `docs/architecture/ARCHITECTURE_RULES.md`
- `tests/architecture/`
- `tg_msg_manager/` only through deterministic static import scans

May change:

- `docs/architecture/README.md`
- `docs/architecture/ARCHITECTURE_RULES.md`
- `tests/architecture/`
- `docs/stages/reports/STAGE_6A_1_APPLICATION_RUNTIME_BOUNDARY_GUARDRAILS_REPORT.md`
- lifecycle updates required by `AGENTS.md`

## 3. HARD PROHIBITIONS

- Do not edit runtime code under `tg_msg_manager/` except architecture tests.
- Do not create the application runtime implementation in this stage.
- Do not change CLI behavior, SQLite schema, storage behavior, dataset/export formats, retry behavior, scheduler behavior, or package metadata.
- Do not allow services, core, or infrastructure to import CLI modules.
- Do not add business logic to compatibility wrappers or protected service facades.
- Do not read existing `docs/stages/reports/` files unrelated to Stage 6A.0 or this stage.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Add architecture documentation for `tg_msg_manager/application/` as the application/runtime assembly layer that may wire core, infrastructure, services, and Telegram adapters.
2. State that CLI remains an adapter: parse args, render output, call the application runtime/session.
3. Add or extend architecture tests that prevent `tg_msg_manager.services`, `tg_msg_manager.core`, and `tg_msg_manager.infrastructure` from importing `tg_msg_manager.cli`, `cli_commands`, `cli_menu`, or `cli_parser`.
4. Add a test allowlist/expectation for the `tg_msg_manager/application/` package boundary without creating implementation code.
5. Create the stage report in Russian.

## 5. REQUIRED DOCS

- Update architecture docs only for the new application runtime boundary.
- Do not update README, COMMANDS, CHANGELOG, or user docs.
- Create the required report in Russian.

## 6. TESTS / VERIFICATION

Run:

- `pytest tests/architecture`
- `git diff --check`

If a command is unavailable, record the exact reason in the report.

## 7. REPORT

Create `docs/stages/reports/STAGE_6A_1_APPLICATION_RUNTIME_BOUNDARY_GUARDRAILS_REPORT.md` in Russian with:

- boundary documented;
- architecture guardrails added or confirmed;
- files changed;
- commands run and results;
- confirmation that runtime behavior, CLI behavior, SQLite schema, and dataset/export formats were preserved;
- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md` if applied manually;
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md` if applied manually.

## 8. COMPLETION CRITERIA

- Application runtime boundary is documented.
- Architecture tests guard CLI import direction.
- No runtime behavior changed.
- Required report exists.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Keep final response under 1200 characters unless the user asks otherwise.
