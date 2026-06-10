# STAGE 5V.2 — TESTPYPI TRUSTED PUBLISHING SETUP

Status: completed
Stage: 5V.2
Type: release workflow implementation
Depends on:
`docs/stages/reports/STAGE_5V_1_TESTPYPI_NAME_AUTH_PREPARATION_REPORT.md` with
`PASSED` and exact package identity `tg-msg-manager`; GitHub repository
`JohnyNoxwell/tg-msg-manager`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Apply stage-reviewer, architecture-guard, and
stage-completion-auditor from `.skills/`. This stage prepares GitHub Actions
Trusted Publishing only. It does not configure TestPyPI externally or publish.

## 1. PURPOSE

Create a narrowly scoped, manually triggered GitHub Actions workflow that can
build an explicitly selected release tag and publish its artifacts to TestPyPI
through OIDC. Record the exact TestPyPI pending-publisher contract required by
the next stage.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `.github/workflows/ci.yml`
- `pyproject.toml`
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_5U_7_RC2_PACKAGE_ARTIFACT_VERIFICATION_REPORT.md`
- `docs/stages/reports/STAGE_5V_1_TESTPYPI_NAME_AUTH_PREPARATION_REPORT.md`

Writable paths: `.github/workflows/testpypi-publish.yml`,
`docs/stages/reports/STAGE_5V_2_TESTPYPI_TRUSTED_PUBLISHING_SETUP_REPORT.md`,
`docs/stages/README.md`, and lifecycle move of this stage file.

## 3. HARD PROHIBITIONS

- Do not upload to TestPyPI or PyPI; do not create/configure a TestPyPI
  publisher, GitHub Environment, secret, tag, release, commit, or push.
- Do not use API tokens, repository secrets, `.pypirc`, password inputs, or
  `TWINE_USERNAME`/`TWINE_PASSWORD`.
- Do not edit source, tests, package metadata/version/dependencies, CI workflow,
  unrelated docs, or existing reports unrelated to this stage.
- Do not permit branch builds, arbitrary refs, automatic push/tag/release
  triggers, PyPI targets, or artifact mutation after build.
- Preserve CLI/runtime behavior, SQLite schema, dataset formats, and package
  contents.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Inspect current workflow conventions, package build command, exact repository
   identity, and Stage 5U.7 artifact expectations; do not edit yet.
2. Create `.github/workflows/testpypi-publish.yml` with `workflow_dispatch`,
   required string input `tag`, separate build and publish jobs, environment
   `testpypi` on the publish job, and no stored credentials.
3. Give the build job only `contents: read`; validate that input matches `v*`,
   checkout the exact tag, verify `HEAD` equals the peeled tag target, build
   once, run `python -m twine check dist/*`, and transfer only `dist/` through
   `actions/upload-artifact` and `actions/download-artifact`.
4. Give the publish job only `id-token: write`; require the successful build
   job and publish the downloaded artifacts once through
   `pypa/gh-action-pypi-publish@release/v1` with
   `repository-url: https://test.pypi.org/legacy/`.
5. Record the exact pending-publisher tuple:
   owner `JohnyNoxwell`, repository `tg-msg-manager`, workflow
   `testpypi-publish.yml`, environment `testpypi`; verify workflow syntax and
   scope, write the report, then complete lifecycle cleanup.

## 5. REQUIRED DOCS

Create only
`docs/stages/reports/STAGE_5V_2_TESTPYPI_TRUSTED_PUBLISHING_SETUP_REPORT.md`;
update the stage index only for lifecycle state.

## 6. TESTS / VERIFICATION

Run:

```bash
git diff --check
python3 -c "import pathlib; p=pathlib.Path('.github/workflows/testpypi-publish.yml'); assert p.is_file() and p.read_text().strip()"
ruby -e "require 'yaml'; YAML.load_file('.github/workflows/testpypi-publish.yml')"
rg -n "workflow_dispatch|contents: read|id-token: write|environment: testpypi|actions/upload-artifact|actions/download-artifact|test.pypi.org/legacy|pypa/gh-action-pypi-publish@release/v1" .github/workflows/testpypi-publish.yml
rg -n "TWINE_PASSWORD|TWINE_USERNAME|password:|upload.pypi.org|push:|release:" .github/workflows/testpypi-publish.yml
```

The positive `rg` must find all required controls. The prohibited-pattern `rg`
must return no matches. Do not claim checks passed unless actually run.

## 7. REPORT

Write a Russian report with workflow trigger, permissions, exact-tag checks,
build/check/publish flow, pending-publisher tuple, exact verification commands,
preserved boundaries, applied skills, and lifecycle notes. Explicitly record
that no publisher was configured and no upload/publish occurred.

## 8. COMPLETION CRITERIA

Complete only if the workflow is syntax-valid, manually triggered,
least-privilege, OIDC-only, TestPyPI-only, exact-tag constrained, and the report
records the pending-publisher tuple and verification evidence.
Lifecycle cleanup is completed according to `AGENTS.md`.
Do not start publisher registration or TestPyPI upload; those require a separate
explicit stage.

## 9. OUTPUT LIMITS

Follow `AGENTS.md`; do not print full workflow contents or broad diffs.
