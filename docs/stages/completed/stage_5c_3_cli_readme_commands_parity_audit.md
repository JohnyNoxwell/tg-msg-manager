# STAGE 5C.3 — CLI / README / COMMANDS PARITY AUDIT

Status: completed
Stage: 5C.3
Type: documentation parity audit
Depends on: Stage 5C.1 complete; current CLI parser surface

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.

Execute Stage 5C.3 only.

Goal:
Audit and correct documentation parity between actual CLI parser behavior, `README.md`, `COMMANDS.md`, and `docs/development/CLI_CONTRACT.md`.

Do not start Stage 5C.4 or later stages.
Prefer docs-only corrections. Do not change CLI behavior unless a stage blocker proves docs cannot be corrected safely.
Use `AGENTS.md` compact output format.

## 1. PURPOSE

Ensure the documented CLI command and flag inventory matches the actual parser. Known target: `docs/development/CLI_CONTRACT.md` may lag behind `export-channel`.

## 2. FILES TO INSPECT

Required:
- `AGENTS.md`
- this stage file
- `tg_msg_manager/cli_parser.py`
- `tg_msg_manager/cli/__init__.py`
- `tg_msg_manager/cli/commands/channel_export.py`
- `tg_msg_manager/cli/commands/dataset.py`
- `README.md`
- `COMMANDS.md`
- `docs/development/CLI_CONTRACT.md`
- `tests/cli/test_cli.py`
- `tests/cli/test_channel_export_cli.py`
- `tests/services/dataset_validation/test_dataset_validation_contracts.py`

May change:
- `README.md`
- `COMMANDS.md`
- `docs/development/CLI_CONTRACT.md`
- `docs/stages/reports/STAGE_5C_3_CLI_README_COMMANDS_PARITY_AUDIT_REPORT.md`
- `docs/stages/README.md`
- this stage file location during lifecycle cleanup

Do not read or change:
- service internals unrelated to CLI docs;
- storage internals;
- archive files;
- ignored local artifacts.

## 3. HARD PROHIBITIONS

- Do not change command names, flags, defaults, parser behavior, output formats, exit codes, or handler behavior.
- Do not add new commands.
- Do not remove legacy aliases or menu compatibility.
- Do not update docs with aspirational behavior.
- Do not add analytics, OSINT, profiling, OCR, STT, media recognition, or LLM behavior.
- Do not change SQLite schema or dataset formats.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Capture actual CLI surface.
   - Read parser definitions.
   - Run `python3 -m tg_msg_manager.cli --help`.
   - Run help for commands that are missing or suspicious in docs.
   - Do not edit yet.

2. Compare docs.
   - Compare `README.md` quick references and advanced usage.
   - Compare `COMMANDS.md` command sections.
   - Compare `docs/development/CLI_CONTRACT.md` command inventory.

3. Patch only factual docs drift.
   - Prefer minimal edits.
   - If docs disagree with code, document current code behavior.
   - Do not normalize unrelated wording.

4. Run focused checks.
   - Use section 6 commands.
   - Record any baseline failure exactly.

5. Report and cleanup.
   - Create the Russian report.
   - Perform lifecycle cleanup after checks and report.

## 5. REQUIRED DOCS

Required:
- `docs/stages/reports/STAGE_5C_3_CLI_README_COMMANDS_PARITY_AUDIT_REPORT.md`
- `docs/stages/README.md` during lifecycle cleanup

Conditional:
- `README.md` if user-facing command examples are stale.
- `COMMANDS.md` if command reference is stale.
- `docs/development/CLI_CONTRACT.md` if parser inventory is stale.

## 6. TESTS / VERIFICATION

Run:
- `python3 -m tg_msg_manager.cli --help`
- `python3 -m tg_msg_manager.cli export-channel --help`
- `python3 -m tg_msg_manager.cli validate-dataset --help`
- `python3 -m tg_msg_manager.cli inspect-dataset --help`
- `python3 -m pytest tests/cli/test_cli.py tests/cli/test_channel_export_cli.py tests/services/dataset_validation/test_dataset_validation_contracts.py -q`
- `python3 -m compileall tg_msg_manager`
- `git diff --check`

## 7. REPORT

Create `docs/stages/reports/STAGE_5C_3_CLI_README_COMMANDS_PARITY_AUDIT_REPORT.md` in Russian.

Include:
- actual commands/flags checked;
- docs drift found;
- docs changed;
- checks run;
- confirmation that CLI runtime behavior was unchanged;
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`.

## 8. COMPLETION CRITERIA

- CLI docs match actual parser for audited commands.
- No runtime CLI code changes are made.
- Focused CLI tests pass or blockers are recorded.
- lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- No full diffs.
- No generated full help output in final response.
- No markdown tables in the final response.
