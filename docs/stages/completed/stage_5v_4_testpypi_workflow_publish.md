# STAGE 5V.4 — TESTPYPI WORKFLOW PUBLISH

Status: completed
Stage: 5V.4
Type: TestPyPI release operation
Depends on:
`docs/stages/reports/STAGE_5V_3_TESTPYPI_TRUSTED_PUBLISHER_REGISTRATION_REPORT.md`
with `PASSED` and `READY_FOR_STAGE_5V_4_TESTPYPI_WORKFLOW_PUBLISH`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Apply stage-reviewer, architecture-guard, and
stage-completion-auditor from `.skills/`. This stage authorizes exactly one
GitHub Actions dispatch that publishes exact tag `v0.1.0-rc2` to TestPyPI
through Trusted Publishing. It does not authorize PyPI publication.

## 1. PURPOSE

Dispatch the approved TestPyPI workflow once for exact tag `v0.1.0-rc2`,
monitor the run, verify the published `tg-msg-manager` version `0.1.0` and
files, and record immutable publication evidence.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `.github/workflows/testpypi-publish.yml`
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_5U_7_RC2_PACKAGE_ARTIFACT_VERIFICATION_REPORT.md`
- `docs/stages/reports/STAGE_5U_8_RC2_ISOLATED_INSTALL_SMOKE_REPORT.md`
- `docs/stages/reports/STAGE_5V_3_TESTPYPI_TRUSTED_PUBLISHER_REGISTRATION_REPORT.md`

Writable paths: `docs/stages/reports/STAGE_5V_4_TESTPYPI_WORKFLOW_PUBLISH_REPORT.md`,
`docs/stages/README.md`, lifecycle move of this stage file, one authorized
GitHub Actions workflow run, and its authorized TestPyPI upload.

## 3. HARD PROHIBITIONS

- Do not edit workflows, source, tests, package metadata/version/dependencies,
  tags, releases, secrets, environments, publisher settings, or unrelated docs.
- Do not publish to PyPI, use API tokens/passwords, create `.pypirc`, or expose
  OIDC/security output.
- Do not dispatch any ref except `main` or any input except
  `tag=v0.1.0-rc2`; do not dispatch more than once.
- Do not dispatch if TestPyPI project/version `tg-msg-manager`/`0.1.0` already
  exists, the exact tag/workflow/publisher/environment contract differs, or a
  prior matching workflow run exists.
- Do not retry after failed, cancelled, timed-out, ambiguous, or partially
  successful dispatch until the run and public TestPyPI state are classified.
  TestPyPI files and versions are immutable.
- Preserve CLI/runtime behavior, SQLite schema, dataset formats, and package
  contents.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify Stage 5V.3 prerequisite, clean understood worktree, GitHub auth,
   workflow on default branch `main`, Environment `testpypi`, exact local and
   remote `v0.1.0-rc2` tag target, and zero prior matching workflow runs.
2. Immediately before dispatch, verify public TestPyPI project/version
   `tg-msg-manager`/`0.1.0` is absent and PyPI is not targeted; stop on any
   mismatch.
3. Dispatch exactly once:
   `gh workflow run testpypi-publish.yml --repo JohnyNoxwell/tg-msg-manager --ref main -f tag=v0.1.0-rc2`.
   Identify the resulting run ID without dispatching again.
4. Monitor that run to terminal state; verify build and publish jobs succeeded,
   exact input/tag evidence is present, and artifact names/metadata match Stage
   5U.7 expectations. Record artifact checksums as publication evidence without
   requiring reproducible equality to prior local-build checksums.
5. Verify public TestPyPI JSON for project `tg-msg-manager`, version `0.1.0`,
   wheel and sdist filenames/checksums, and no PyPI publication; write the
   report and complete lifecycle cleanup.

## 5. REQUIRED DOCS

Create only
`docs/stages/reports/STAGE_5V_4_TESTPYPI_WORKFLOW_PUBLISH_REPORT.md`; update the
stage index only for lifecycle state.

## 6. TESTS / VERIFICATION

Run exact tag/local/remote checks, workflow/default-branch/environment checks,
pre-dispatch and post-dispatch run listings, pre-upload and post-upload
TestPyPI JSON checks, post-run job/conclusion inspection, public filename and
SHA-256 verification, PyPI absence check, and `git diff --check`. Record exact
commands and concise redacted results. Never claim success from dispatch
acceptance alone; require terminal successful run and public TestPyPI evidence.

## 7. REPORT

Write a Russian report with prerequisites, pre-upload state, exact single
dispatch command, run ID/URL/event/ref/input/conclusion/jobs, published
project/version/files/checksums, public TestPyPI evidence, PyPI absence,
no-retry confirmation, preserved scope, applied skills, and lifecycle notes.
Do not include credentials, OIDC output, full logs, or full HTTP bodies.

## 8. COMPLETION CRITERIA

Complete only if exactly one authorized workflow run succeeds, exact
`tg-msg-manager` version `0.1.0` wheel and sdist are publicly verified on
TestPyPI, PyPI remains untouched, the report exists, and no ambiguity remains.
Lifecycle cleanup is completed according to `AGENTS.md`.
Any failed or ambiguous run blocks completion and retry until a separate
explicit recovery decision is recorded.

## 9. OUTPUT LIMITS

Follow `AGENTS.md`; never print credentials, OIDC/security output, full workflow
logs, full HTTP bodies, or broad diffs.
