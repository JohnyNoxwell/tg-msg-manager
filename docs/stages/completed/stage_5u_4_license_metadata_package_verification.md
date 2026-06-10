# STAGE 5U.4 — LICENSE METADATA PACKAGE VERIFICATION

Status: active task
Stage: 5U.4
Type: packaging verification
Depends on: `docs/stages/reports/STAGE_5U_3_LICENSE_METADATA_APPLICATION_REPORT.md`
with `PASSED`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Apply `.skills/stage-reviewer/SKILL.md` before
verification, `.skills/architecture-guard/SKILL.md` for scope confirmation, and
`.skills/stage-completion-auditor/SKILL.md` after report/cleanup.

Stop with `FAILED` if Stage 5U.3 is absent/not `PASSED` or metadata is not in
the approved state. Do not start Stage 5V or publish packages.

## 1. PURPOSE

Build and inspect package artifacts containing the approved MIT metadata, run
twine validation, clean repository artifacts, and decide whether TestPyPI
publishing preparation may start.

## 2. FILES TO INSPECT

Required:

- `AGENTS.md`
- `LICENSE`
- `pyproject.toml`
- `README.md`
- `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`
- `docs/stages/reports/STAGE_5U_2_LICENSE_METADATA_DECISION_REPORT.md`
- `docs/stages/reports/STAGE_5U_3_LICENSE_METADATA_APPLICATION_REPORT.md`
- `docs/stages/README.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`

Writable repository paths:

- `docs/stages/reports/STAGE_5U_4_LICENSE_METADATA_PACKAGE_VERIFICATION_REPORT.md`
- `docs/stages/README.md`
- lifecycle move of this stage file
- temporary repository build artifacts, which must be removed before completion

## 3. HARD PROHIBITIONS

- Do not edit LICENSE/package/public metadata, production code, tests, CLI/
  runtime behavior, SQLite, dataset/export contracts, dependencies,
  build-system requirements, package name, or version.
- Do not create/delete/push tags, publish to TestPyPI/PyPI, create a GitHub
  Release or stable tag, or start Stage 5V.
- Do not initialize Telegram, run live commands, or read private artifacts,
  sessions, credentials, real exports/logs/media/screenshots/DB files.
- Do not leave `dist/`, `build/`, or generated `*.egg-info` artifacts.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify Stage 5U.2-5U.3 reports and current approved license metadata.
2. Record pre-build repository artifact/status state.
3. Run `python3 -m build`; classify a project-owned failure as `FAILED`. If
   `build` is unavailable, install it only in a temporary isolated tooling venv
   when policy/network permits; otherwise record the exact external blocker and
   classify the stage `PARTIAL`.
4. Run `python3 -m twine check dist/*`. If `twine` is unavailable, install it
   only in the temporary isolated tooling venv when policy/network permits;
   otherwise record the exact external blocker and classify the stage `PARTIAL`.
5. Verify built sdist/wheel metadata reports MIT licensing and unchanged name
   `tg-msg-manager` and version `0.1.0`.
6. Create a Russian report draft before cleanup.
7. Remove only generated repository build artifacts, verify cleanup/status,
   finalize the report with cleanup results, then complete lifecycle cleanup.

## 5. REQUIRED DOCS

Create only
`docs/stages/reports/STAGE_5U_4_LICENSE_METADATA_PACKAGE_VERIFICATION_REPORT.md`.
Do not update package/public docs in this verification stage.

## 6. TESTS / VERIFICATION

Required:

```bash
git diff --check
python3 - <<'PY'
import pathlib
import tomllib

data = tomllib.loads(pathlib.Path("pyproject.toml").read_text())
print(data["project"]["name"])
print(data["project"]["version"])
print(data["project"].get("license"))
print(data["project"].get("license-files"))
print(data["project"].get("classifiers", []))
PY
python3 -m build
python3 -m twine check dist/*
rm -rf dist build tg_msg_manager.egg-info
git status --short
git diff --check
```

Use a structured package-metadata reader or archive inspection for built
artifacts; do not rely on ad hoc binary/string searching. Record and remove any
temporary tooling venv after checks. Do not publish.

## 7. REPORT

Create the required report in Russian. Include: `PASSED`, `FAILED`, or
`PARTIAL`; goal; prerequisite evidence; license decision; files changed by
prior application stage; metadata before/after summary; unchanged identity/
version/dependencies confirmation; exact commands/results; commands not run
and why; build result; twine result; built metadata result; cleanup result;
preserved production/tests/CLI/SQLite/dataset/export/dependency/version scope;
no tag/release/publish confirmation; final recommendation; applied skill paths;
and lifecycle notes.

For `PASSED`, final recommendation:
`Proceed to STAGE_5V_TESTPYPI_PUBLISH_PREPARATION`.

## 8. COMPLETION CRITERIA

- `PASSED`: build and twine checks pass, built metadata is correct, artifacts
  and temporary tooling venv are cleaned, report exists, and lifecycle cleanup
  is complete.
- `PARTIAL`: metadata is correct but build or twine cannot complete solely due
  to an exact external tooling/network blocker; do not authorize Stage 5V.
- `FAILED`: prerequisite/metadata is invalid, a project-owned build/check fails,
  protected scope changed, or a forbidden action occurred.
- Lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

Follow `AGENTS.md`. Do not paste full build output, metadata dumps, diffs, or
report bodies.
