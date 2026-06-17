# STAGE 6A.3 — Service Bundle Factory Extraction

Status: active task
Stage: 6A.3
Type: implementation
Depends on: `docs/stages/reports/STAGE_6A_2_RUNTIME_RESOURCE_FACTORY_EXTRACTION_REPORT.md`

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` and this file before editing.
- Do not start unless the Stage 6A.2 report exists or the user explicitly overrides the dependency.
- Use `stage-reviewer` before implementation; if unavailable, read `.skills/stage-reviewer/SKILL.md` manually and state that in the report.
- Use `architecture-guard` because this stage moves service assembly out of CLI; if unavailable, read `.skills/architecture-guard/SKILL.md` manually and state that in the report.
- Write a compact plan with no more than 5 bullets before edits.

## 1. PURPOSE

Extract service construction from `CLIContext` into a typed application service bundle while preserving current service instances and CLI compatibility attributes.

## 2. FILES TO INSPECT

- `docs/stages/reports/STAGE_6A_2_RUNTIME_RESOURCE_FACTORY_EXTRACTION_REPORT.md`
- `tg_msg_manager/application/resources.py`
- `tg_msg_manager/cli/__init__.py`
- `tg_msg_manager/services/exporter.py`
- `tg_msg_manager/services/db_export/__init__.py`
- `tg_msg_manager/services/private_archive/__init__.py`
- `tg_msg_manager/services/channel_export/__init__.py`
- `tg_msg_manager/services/cleaner.py`
- `tg_msg_manager/services/retry_worker.py`
- `tg_msg_manager/services/alias_manager.py`
- `tests/cli/test_cli.py`
- `tests/architecture/`

May change:

- `tg_msg_manager/application/__init__.py`
- `tg_msg_manager/application/resources.py`
- `tg_msg_manager/application/services.py`
- `tg_msg_manager/cli/__init__.py` only for mechanical delegation and attribute assignment
- focused tests under `tests/cli/` or `tests/architecture/`
- `docs/stages/reports/STAGE_6A_3_SERVICE_BUNDLE_FACTORY_EXTRACTION_REPORT.md`
- lifecycle updates required by `AGENTS.md`

## 3. HARD PROHIBITIONS

- Do not change service constructor arguments except moving them into the factory.
- Do not change service behavior, event payloads, event sink rendering, retry behavior, cleaner artifact roots, export paths, or channel export options.
- Do not add service logic to `CLIContext`.
- Do not edit protected service facades except if a test import requires mechanical import adjustment; stop if more is needed.
- Do not change CLI output, prompts, exit codes, SQLite schema, storage SQL, dataset formats, or state files.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Create `tg_msg_manager/application/services.py` with a typed service bundle containing exporter, cleaner, db exporter, private archive, channel exporter, retry worker, and alias manager.
2. Create a service factory in `tg_msg_manager/application/services.py` that accepts already constructed resources, runtime paths/settings, `needs_client`, and the service event sink.
3. Replace `CLIContext` service construction with service bundle creation.
4. Keep existing `CLIContext.exporter`, `cleaner`, `db_exporter`, `private_archive`, `channel_exporter`, `retry_worker`, and `alias_manager` attributes for compatibility.
5. Add focused tests proving service constructors receive the same arguments as before.

## 5. REQUIRED DOCS

- Do not update user docs.
- Update architecture docs only if Stage 6A.1 boundary text becomes inaccurate.
- Create the required report in Russian.

## 6. TESTS / VERIFICATION

Run:

- `pytest tests/cli/test_cli.py`
- `pytest tests/architecture`
- `python3 -m compileall tg_msg_manager`
- `ruff check tg_msg_manager tests/cli tests/architecture`
- `git diff --check`

## 7. REPORT

Create `docs/stages/reports/STAGE_6A_3_SERVICE_BUNDLE_FACTORY_EXTRACTION_REPORT.md` in Russian with:

- service bundle fields;
- behavior-preservation evidence;
- tests/checks run and results;
- compatibility attributes intentionally retained;
- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md` if applied manually;
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md` if applied manually.

## 8. COMPLETION CRITERIA

- Service construction is delegated outside `CLIContext`.
- Existing CLI handlers still work through compatibility attributes.
- No service behavior changed.
- Required report exists.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Keep final response under 1200 characters unless the user asks otherwise.
