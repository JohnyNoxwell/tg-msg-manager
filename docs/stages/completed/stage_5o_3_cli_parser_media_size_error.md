# STAGE 5O.3 — CLI Parser Media Size Error

Status: active task
Stage: 5O.3
Type: implementation
Depends on: completed Stage 5O.0 report and current `tg_msg_manager/cli_parser.py`

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` and this file before editing.
- Do not start unless `docs/stages/reports/STAGE_5O_0_REFACTORING_GUARDRAILS_REPORT.md` exists or the user explicitly overrides the dependency.
- Use `stage-reviewer` before implementation; if unavailable, read `.skills/stage-reviewer/SKILL.md` manually and state that in the report.
- Use `architecture-guard` because this stage touches CLI parsing; if unavailable, read `.skills/architecture-guard/SKILL.md` manually and state that in the report.
- Write a compact plan with no more than 5 bullets before edits.

## 1. PURPOSE

Replace the parser-local `assert` path for media size parsing with an explicit argparse error path while preserving all accepted inputs and public CLI behavior.

## 2. FILES TO INSPECT

- `tg_msg_manager/cli_parser.py`
- `tests/cli/` parser or channel export CLI tests
- `docs/development/CLI_CONTRACT.md`

May change:

- `tg_msg_manager/cli_parser.py`
- focused tests under `tests/cli/`
- `docs/stages/reports/STAGE_5O_3_CLI_PARSER_MEDIA_SIZE_ERROR_REPORT.md`
- lifecycle updates required by `AGENTS.md`

## 3. HARD PROHIBITIONS

- Do not add, remove, rename, or change defaults for CLI flags.
- Do not change accepted media size syntax.
- Do not change channel export behavior, dataset format, or media download behavior.
- Do not change menu behavior except if a shared parser helper requires identical error handling.
- Do not read existing `docs/stages/reports/` files unrelated to this stage.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Add or extend focused tests for valid and invalid `--max-media-size` inputs.
2. Replace the `assert` fallback in `_parse_media_size_argument` with explicit `argparse.ArgumentTypeError` or equivalent current-parser error handling.
3. Ensure optimized Python mode would not bypass the error path.
4. Keep error text stable unless current tests require a clearer deterministic message.

## 5. REQUIRED DOCS

- Update CLI docs only if help text or documented errors change; this stage should avoid that.
- Create the required report in Russian.

## 6. TESTS / VERIFICATION

Run:

- `pytest tests/cli`
- `python3 -m compileall tg_msg_manager`
- `ruff check tg_msg_manager/cli_parser.py tests/cli`

## 7. REPORT

Create `docs/stages/reports/STAGE_5O_3_CLI_PARSER_MEDIA_SIZE_ERROR_REPORT.md` in Russian with:

- parser behavior preserved;
- tests added/updated;
- commands run and results.

## 8. COMPLETION CRITERIA

- No CLI contract changed.
- Invalid media size input uses an explicit parser error path.
- Required report exists.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Keep final response under 1200 characters unless the user asks otherwise.
