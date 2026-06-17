# STAGE 6A.0 — CLI Runtime Boundary Precheck

Status: active task
Stage: 6A.0
Type: docs/precheck
Depends on: current `CLIContext`, current architecture rules, and empty `docs/stages/active/` baseline

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` and this file before editing.
- Use `stage-reviewer` before implementation; if unavailable, read `.skills/stage-reviewer/SKILL.md` manually and state that in the report.
- Use `architecture-guard` because this stage evaluates CLI/runtime/service boundaries; if unavailable, read `.skills/architecture-guard/SKILL.md` manually and state that in the report.
- Write a compact plan with no more than 5 bullets before edits.
- This is an audit stage only. Do not implement the extraction.

## 1. PURPOSE

Create a factual baseline for reducing `CLIContext` from a CLI-owned composition root into a thin CLI adapter without changing behavior.

## 2. FILES TO INSPECT

- `tg_msg_manager/cli/__init__.py`
- `tg_msg_manager/cli_commands.py`
- `tg_msg_manager/cli_menu.py`
- `tg_msg_manager/cli_support.py`
- `tg_msg_manager/core/runtime.py`
- `tg_msg_manager/core/process.py`
- `tg_msg_manager/core/telegram/client.py`
- `tg_msg_manager/infrastructure/storage/sqlite.py`
- `tests/cli/test_cli.py`
- `tests/cli/`
- `docs/architecture/README.md`
- `docs/architecture/ARCHITECTURE_RULES.md`

May change:

- `docs/stages/reports/STAGE_6A_0_CLI_RUNTIME_BOUNDARY_PRECHECK_REPORT.md`
- lifecycle updates required by `AGENTS.md`

## 3. HARD PROHIBITIONS

- Do not edit runtime code.
- Do not edit tests.
- Do not change CLI commands, flags, defaults, prompts, output, exit codes, or import compatibility.
- Do not change SQLite schema, storage behavior, dataset formats, export layouts, state files, retry behavior, or scheduler behavior.
- Do not add analytics, OSINT, profiling, classification, OCR, STT, media analysis, GUI, SaaS, daemon mode, or LLM behavior.
- Do not read private artifacts, exported datasets, logs, sessions, credentials, local databases, archive prompts, or existing `docs/stages/reports/` files unrelated to this stage.

## 4. ATOMIC IMPLEMENTATION TASKS

1. List every object currently constructed by `CLIContext` and classify it as runtime resource, service, CLI renderer, or compatibility attribute.
2. List every command/menu/support path that reads `ctx.*`, grouped by required capability.
3. Identify the smallest safe extraction order for Stages 6A.1-6A.6.
4. Record exact behavior that later stages must preserve, including no-client command behavior and login error handling.
5. Create the precheck report in Russian.

## 5. REQUIRED DOCS

- Do not update user docs.
- Do not update architecture docs in this stage.
- Create the required report in Russian.

## 6. TESTS / VERIFICATION

Run:

- `git diff --check`

Do not run pytest unless runtime/test files are accidentally changed; if that happens, stop and report the scope violation.

## 7. REPORT

Create `docs/stages/reports/STAGE_6A_0_CLI_RUNTIME_BOUNDARY_PRECHECK_REPORT.md` in Russian with:

- current `CLIContext` construction/lifecycle inventory;
- `ctx.*` consumer inventory;
- proposed extraction order;
- preservation contract for CLI, SQLite, dataset/export, retry, scheduler, and login behavior;
- commands run and results;
- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md` if applied manually;
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md` if applied manually.

## 8. COMPLETION CRITERIA

- The factual report exists.
- No runtime code or tests changed.
- The report defines the exact next implementation boundary for Stage 6A.1.
- `git diff --check` was run and passed, or failure is documented with exact cause.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Keep final response under 1200 characters unless the user asks otherwise.
