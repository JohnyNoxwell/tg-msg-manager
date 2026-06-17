# STAGE 6A.6 — Headless Runtime Contract

Status: active task
Stage: 6A.6
Type: implementation/docs
Depends on: `docs/stages/reports/STAGE_6A_5_CLI_CONTEXT_ADAPTER_SHRINK_REPORT.md`

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` and this file before editing.
- Do not start unless the Stage 6A.5 report exists or the user explicitly overrides the dependency.
- Use `stage-reviewer` before implementation; if unavailable, read `.skills/stage-reviewer/SKILL.md` manually and state that in the report.
- Use `architecture-guard` because this stage exposes the non-CLI runtime boundary; if unavailable, read `.skills/architecture-guard/SKILL.md` manually and state that in the report.
- Write a compact plan with no more than 5 bullets before edits.

## 1. PURPOSE

Document and test the non-CLI application runtime entrypoint so external integrations can use runtime/session assembly without importing CLI modules.

## 2. FILES TO INSPECT

- `docs/stages/reports/STAGE_6A_5_CLI_CONTEXT_ADAPTER_SHRINK_REPORT.md`
- `tg_msg_manager/application/__init__.py`
- `tg_msg_manager/application/resources.py`
- `tg_msg_manager/application/services.py`
- `tg_msg_manager/application/session.py`
- `tg_msg_manager/cli/__init__.py`
- `docs/architecture/README.md`
- `docs/architecture/ARCHITECTURE_RULES.md`
- `docs/development/CLI_CONTRACT.md`
- `tests/architecture/`
- `tests/cli/`

May change:

- `tg_msg_manager/application/__init__.py` only if needed for stable non-CLI import
- `docs/architecture/README.md`
- `docs/architecture/ARCHITECTURE_RULES.md`
- `docs/development/CLI_CONTRACT.md` only to state the CLI remains an adapter
- focused tests under `tests/architecture/` or `tests/cli/`
- `docs/stages/reports/STAGE_6A_6_HEADLESS_RUNTIME_CONTRACT_REPORT.md`
- lifecycle updates required by `AGENTS.md`

## 3. HARD PROHIBITIONS

- Do not add daemon mode, background scheduler changes, new commands, GUI, web UI, SaaS behavior, analytics, OSINT, profiling, classification, OCR, STT, media analysis, or LLM behavior.
- Do not change CLI commands, flags, defaults, prompts, output, exit codes, or existing command routing.
- Do not change SQLite schema, storage SQL, dataset/export formats, state files, retry behavior, scheduler behavior, or package metadata.
- Do not make services, core, or infrastructure import CLI modules.
- Do not create broad public APIs beyond the runtime/session boundary already implemented.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Define the stable non-CLI import path for building the application runtime session.
2. Add or update architecture tests proving the non-CLI runtime entrypoint imports without importing CLI modules.
3. Add a focused smoke test that constructs the runtime/session in no-client mode without Telegram client construction.
4. Update architecture/development docs to state the headless boundary and its limits.
5. Create the stage report in Russian.

## 5. REQUIRED DOCS

- Update only architecture/development docs needed to describe the non-CLI runtime boundary.
- Do not update README, COMMANDS, CHANGELOG, or user feature docs unless they currently contradict the implementation.
- Create the required report in Russian.

## 6. TESTS / VERIFICATION

Run:

- `pytest tests/architecture`
- `pytest tests/cli`
- `python3 -m compileall tg_msg_manager`
- `ruff check tg_msg_manager tests/architecture tests/cli`
- `git diff --check`

## 7. REPORT

Create `docs/stages/reports/STAGE_6A_6_HEADLESS_RUNTIME_CONTRACT_REPORT.md` in Russian with:

- stable non-CLI entrypoint;
- import-boundary evidence;
- no-client smoke evidence;
- docs updated;
- tests/checks run and results;
- confirmation that no daemon/GUI/SaaS/product behavior was added;
- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md` if applied manually;
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md` if applied manually.

## 8. COMPLETION CRITERIA

- Non-CLI runtime/session entrypoint is documented and tested.
- CLI remains an adapter.
- No new product behavior is added.
- Required report exists.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Keep final response under 1200 characters unless the user asks otherwise.
