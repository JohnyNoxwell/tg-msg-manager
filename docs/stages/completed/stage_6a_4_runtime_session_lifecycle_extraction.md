# STAGE 6A.4 — Runtime Session Lifecycle Extraction

Status: active task
Stage: 6A.4
Type: implementation
Depends on: `docs/stages/reports/STAGE_6A_3_SERVICE_BUNDLE_FACTORY_EXTRACTION_REPORT.md`

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` and this file before editing.
- Do not start unless the Stage 6A.3 report exists or the user explicitly overrides the dependency.
- Use `stage-reviewer` before implementation; if unavailable, read `.skills/stage-reviewer/SKILL.md` manually and state that in the report.
- Use `architecture-guard` because this stage moves lifecycle ownership out of CLI; if unavailable, read `.skills/architecture-guard/SKILL.md` manually and state that in the report.
- Write a compact plan with no more than 5 bullets before edits.

## 1. PURPOSE

Move lock, storage, Telegram connection, and shutdown lifecycle into an application runtime session while keeping CLI rendering and public behavior unchanged.

## 2. FILES TO INSPECT

- `docs/stages/reports/STAGE_6A_3_SERVICE_BUNDLE_FACTORY_EXTRACTION_REPORT.md`
- `tg_msg_manager/application/resources.py`
- `tg_msg_manager/application/services.py`
- `tg_msg_manager/cli/__init__.py`
- `tg_msg_manager/core/logging.py`
- `tg_msg_manager/core/process.py`
- `tg_msg_manager/core/telemetry.py`
- `tg_msg_manager/infrastructure/storage/sqlite.py`
- `tests/cli/test_cli.py`
- `tests/core/test_concurrency.py`
- `tests/architecture/`

May change:

- `tg_msg_manager/application/__init__.py`
- `tg_msg_manager/application/resources.py`
- `tg_msg_manager/application/services.py`
- `tg_msg_manager/application/session.py`
- `tg_msg_manager/cli/__init__.py` only for delegation and CLI rendering callbacks
- focused tests under `tests/cli/`, `tests/core/`, or `tests/architecture/`
- `docs/stages/reports/STAGE_6A_4_RUNTIME_SESSION_LIFECYCLE_EXTRACTION_REPORT.md`
- lifecycle updates required by `AGENTS.md`

## 3. HARD PROHIBITIONS

- Do not change visible CLI messages, login error wording, lock behavior, signal behavior, storage start/close order, client connect/disconnect order, or shutdown idempotency.
- Do not move terminal rendering into services, core, or infrastructure.
- Do not import CLI modules from application/runtime modules.
- Do not change command routing, no-client command behavior, SQLite schema, storage SQL, dataset/export formats, retry behavior, or scheduler behavior.
- Do not add daemon mode, headless API features, background workers, analytics, or GUI behavior.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Create `tg_msg_manager/application/session.py` with an application runtime session object that owns initialize/shutdown for process manager, storage, optional Telegram client, and service bundle.
2. Keep CLI-specific status output in `CLIContext` or CLI callbacks; the session must not import CLI modules.
3. Make `CLIContext.initialize()` and `shutdown()` delegate lifecycle to the session.
4. Preserve `CLIContext` compatibility attributes by reading them from the session after initialization.
5. Add focused tests for initialization order, shutdown order, lock failure behavior, login error exit behavior, and no-client behavior.

## 5. REQUIRED DOCS

- Do not update user docs.
- Update architecture docs only if the lifecycle boundary differs from Stage 6A.1.
- Create the required report in Russian.

## 6. TESTS / VERIFICATION

Run:

- `pytest tests/cli/test_cli.py`
- `pytest tests/core/test_concurrency.py`
- `pytest tests/architecture`
- `python3 -m compileall tg_msg_manager`
- `ruff check tg_msg_manager tests/cli tests/core tests/architecture`
- `git diff --check`

## 7. REPORT

Create `docs/stages/reports/STAGE_6A_4_RUNTIME_SESSION_LIFECYCLE_EXTRACTION_REPORT.md` in Russian with:

- lifecycle ownership moved;
- initialization/shutdown order preservation evidence;
- tests/checks run and results;
- compatibility attributes retained;
- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md` if applied manually;
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md` if applied manually.

## 8. COMPLETION CRITERIA

- Lifecycle ownership is outside `CLIContext`.
- CLI output and error behavior are preserved.
- Focused lifecycle tests pass.
- Required report exists.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Keep final response under 1200 characters unless the user asks otherwise.
