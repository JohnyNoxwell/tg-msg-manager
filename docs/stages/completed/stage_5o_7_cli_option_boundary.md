# STAGE 5O.7 — CLI Option Boundary

Status: active task
Stage: 5O.7
Type: implementation
Depends on: completed Stage 5O.0 report and current CLI contract

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` and this file before editing.
- Do not start unless `docs/stages/reports/STAGE_5O_0_REFACTORING_GUARDRAILS_REPORT.md` exists or the user explicitly overrides the dependency.
- Use `stage-reviewer` before implementation; if unavailable, read `.skills/stage-reviewer/SKILL.md` manually and state that in the report.
- Use `architecture-guard` because this stage touches CLI/service boundaries; if unavailable, read `.skills/architecture-guard/SKILL.md` manually and state that in the report.
- Write a compact plan with no more than 5 bullets before edits.

## 1. PURPOSE

Remove duplicated command option construction between parser-driven CLI handlers and interactive menu paths without changing command names, flags, defaults, help text, or output behavior.

## 2. FILES TO INSPECT

- `tg_msg_manager/cli/__init__.py`
- `tg_msg_manager/cli_parser.py`
- `tg_msg_manager/cli_menu.py`
- `tg_msg_manager/cli/commands/`
- `tg_msg_manager/cli_support.py`
- `tests/cli/`
- `docs/development/CLI_CONTRACT.md`

May change:

- CLI modules listed above
- new small CLI-only option/helper module under `tg_msg_manager/cli/` if needed
- focused tests under `tests/cli/`
- CLI docs only if an existing documented mismatch is found
- `docs/stages/reports/STAGE_5O_7_CLI_OPTION_BOUNDARY_REPORT.md`
- lifecycle updates required by `AGENTS.md`

## 3. HARD PROHIBITIONS

- Do not change any CLI command name, flag name, default value, prompt meaning, output format, exit code contract, or legacy behavior.
- Do not move CLI imports into services/core/infrastructure.
- Do not initialize Telegram or SQLite for local-only commands that currently avoid it.
- Do not change dataset/export/storage behavior.
- Do not read existing `docs/stages/reports/` files unrelated to this stage.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Identify one duplicated option-construction path with highest drift risk, starting with channel export menu/CLI parity.
2. Create a CLI-only builder or typed options object that can be used by both argparse handler and menu handler.
3. Replace only the selected duplicated path; leave unrelated commands unchanged.
4. Add or update tests proving CLI and menu produce equivalent service options for the selected path.
5. Confirm local-only commands still bypass full `CLIContext` initialization.

## 5. REQUIRED DOCS

- Update `docs/development/CLI_CONTRACT.md` only if it currently contradicts implementation; do not change the contract.
- Create the required report in Russian.

## 6. TESTS / VERIFICATION

Run:

- `pytest tests/cli`
- `python3 -m compileall tg_msg_manager`
- `ruff check tg_msg_manager/cli tg_msg_manager/cli_parser.py tg_msg_manager/cli_menu.py tests/cli`

## 7. REPORT

Create `docs/stages/reports/STAGE_5O_7_CLI_OPTION_BOUNDARY_REPORT.md` in Russian with:

- duplicated path removed;
- contract-preservation evidence;
- commands run and results;
- any CLI path intentionally left unchanged.

## 8. COMPLETION CRITERIA

- One CLI/menu option duplication is removed or a blocker is documented.
- CLI behavior is preserved by focused tests.
- Required report exists.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Keep final response under 1200 characters unless the user asks otherwise.
