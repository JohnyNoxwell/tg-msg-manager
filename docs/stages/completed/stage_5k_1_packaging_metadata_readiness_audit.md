# STAGE 5K.1 — PACKAGING METADATA READINESS AUDIT

Status: active task
Stage: 5K.1
Type: docs audit
Depends on: `docs/stages/reports/STAGE_5K_0_RELEASE_CHECKLIST_SCOPE_NO_PUBLISH_BOUNDARY_REPORT.md`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.

Apply these skills before implementation:

- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md` after checks/report/cleanup

Do not execute Stage 5K.2 or later.

If `docs/development/RELEASE_CHECKLIST_SCOPE.md` is absent, record it and continue or block based on whether packaging boundaries are still clear.

## 1. PURPOSE

Audit package identity, metadata, build configuration, dependency declarations, console script entrypoints, and release policy docs.

This is audit-only unless small docs-only fixes are needed.

## 2. FILES TO INSPECT

Required:

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `pyproject.toml`
- `README.md`
- `COMMANDS.md`
- `CHANGELOG.md`
- `Makefile`
- `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`
- `docs/development/RELEASE_CHECKLIST_SCOPE.md` if present
- `docs/development/README.md`
- `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`
- `docs/stages/README.md`

Inspect only as needed:

- `tg_msg_manager/`
- `run.py`

Writable paths:

- `README.md`
- `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`
- `docs/development/README.md`
- `docs/stages/reports/STAGE_5K_1_PACKAGING_METADATA_READINESS_AUDIT_REPORT.md`
- `docs/stages/README.md`
- `docs/stages/completed/stage_5k_1_packaging_metadata_readiness_audit.md`

Default: do not edit `pyproject.toml`.

## 3. HARD PROHIBITIONS

- Do not bump version, publish, create tags, upload packages, build release artifacts, or claim a release occurred.
- Do not change package behavior, dependency behavior, console script behavior, runtime code, CLI behavior, tests, fixtures, SQLite/storage/services, or output formats.
- Do not add runtime `__version__`.
- Do not read private artifacts or real exports.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Inspect package metadata and docs before editing.
2. Audit distribution name, module root, console script docs/config, `python3 -m tg_msg_manager.cli`, version source, runtime version exposure, dependencies, build metadata, project metadata, package include/exclude expectations, and private artifact policy.
3. Record blockers and non-blocking gaps.
4. Apply only docs-only fixes in allowed paths if metadata docs are inaccurate.
5. Create the Stage 5K.1 report in Russian.
6. Complete lifecycle cleanup according to `AGENTS.md`.

## 5. REQUIRED DOCS

Prefer report-only.

Docs fixes must not change package behavior, version, dependencies, entrypoints, or release status.

## 6. TESTS / VERIFICATION

Required:

```bash
git diff --check
```

Optional safe metadata inspection:

```bash
python3 -c 'import pathlib, tomllib; data=tomllib.loads(pathlib.Path("pyproject.toml").read_text()); print(data.get("project", {}).get("name")); print(data.get("project", {}).get("version"))'
```

Do not run publish/upload commands. Do not run package build unless the stage is explicitly revised to allow a local dry-run.

## 7. REPORT

Create `docs/stages/reports/STAGE_5K_1_PACKAGING_METADATA_READINESS_AUDIT_REPORT.md` in Russian.

Include status/outcome token, files inspected, package identity summary, metadata findings, blockers, non-blocking gaps, docs fixes, whether `pyproject.toml` changed, version unchanged confirmation, no release/tag/publish confirmation, checks run, no runtime/CLI/SQLite/output behavior changes confirmation, private artifact boundary confirmation, `architecture-guard: applied from .skills/architecture-guard/SKILL.md`, and lifecycle notes.

Acceptable outcome tokens:

- `PACKAGING_METADATA_READY_FOR_RELEASE_CHECKLIST`
- `PACKAGING_METADATA_DOC_FIXES_NEEDED`
- `PACKAGING_METADATA_BLOCKERS_FOUND`
- `PACKAGING_METADATA_AUDIT_REPORT_ONLY`

## 8. COMPLETION CRITERIA

- Packaging metadata readiness is classified with evidence.
- Version remains unchanged.
- `pyproject.toml` is unchanged unless the stage is explicitly revised to allow metadata-only corrections.
- Required checks are run or exact inability is recorded.
- Required report exists.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md` final format.

Do not paste full diffs, large file excerpts, or broad summaries.
