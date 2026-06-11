# STAGE 5V.3 — TESTPYPI TRUSTED PUBLISHER REGISTRATION

Status: completed
Stage: 5V.3
Type: external release configuration
Depends on:
`docs/stages/reports/STAGE_5V_2_TESTPYPI_TRUSTED_PUBLISHING_SETUP_REPORT.md`
with `PASSED`; `.github/workflows/testpypi-publish.yml` present on the GitHub
default branch

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Apply stage-reviewer and stage-completion-auditor from
`.skills/`. This stage configures only the GitHub `testpypi` Environment and
the TestPyPI pending publisher. It must not run the publish workflow.

## 1. PURPOSE

Register the exact OIDC trust relationship required for the existing TestPyPI
workflow, without building or publishing package artifacts.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `.github/workflows/testpypi-publish.yml`
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_5V_2_TESTPYPI_TRUSTED_PUBLISHING_SETUP_REPORT.md`

Writable paths: `docs/stages/reports/STAGE_5V_3_TESTPYPI_TRUSTED_PUBLISHER_REGISTRATION_REPORT.md`,
`docs/stages/README.md`, lifecycle move of this stage file, the GitHub
Environment `testpypi`, and the TestPyPI pending publisher for
`tg-msg-manager`.

## 3. HARD PROHIBITIONS

- Do not run or dispatch any workflow; do not build, upload, or publish to
  TestPyPI or PyPI.
- Do not edit workflows, source, tests, package metadata/version/dependencies,
  tags, releases, secrets, unrelated docs, or unrelated external settings.
- Do not create API tokens, repository/environment secrets, `.pypirc`, or
  username/password credentials.
- Do not register a tuple that differs from the exact contract below.
- Stop if the workflow is absent from the GitHub default branch, TestPyPI
  project/version state changed unexpectedly, or ownership/account identity is
  unresolved.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify Stage 5V.2 prerequisite, exact local workflow contract, repository
   identity `JohnyNoxwell/tg-msg-manager`, and that
   `.github/workflows/testpypi-publish.yml` exists on the GitHub default branch;
   do not change external settings yet.
2. Recheck public TestPyPI state for project/version `tg-msg-manager`/`0.1.0`;
   stop if it already exists or differs from the Stage 5V.1 baseline.
3. Check or create only the GitHub Environment named `testpypi`; do not add
   secrets or alter unrelated environment settings.
4. In the authenticated TestPyPI account, register exactly one pending
   publisher with project `tg-msg-manager`, owner `JohnyNoxwell`, repository
   `tg-msg-manager`, workflow `testpypi-publish.yml`, and environment
   `testpypi`. Never inspect or record credentials.
5. Verify the exact tuple through authenticated TestPyPI UI evidence or explicit
   user confirmation, verify no workflow run/upload occurred, write the report,
   and complete lifecycle cleanup.

## 5. REQUIRED DOCS

Create only
`docs/stages/reports/STAGE_5V_3_TESTPYPI_TRUSTED_PUBLISHER_REGISTRATION_REPORT.md`;
update the stage index only for lifecycle state.

## 6. TESTS / VERIFICATION

Run exact local workflow syntax/scope checks, GitHub default-branch workflow
existence check, GitHub Environment `testpypi` check, public TestPyPI JSON
check before and after registration, workflow-run absence check, and
`git diff --check`. Record exact commands and redacted results. Do not claim
the pending publisher is registered without authenticated evidence or explicit
user confirmation.

## 7. REPORT

Write a Russian report with prerequisite evidence, default-branch workflow
evidence, GitHub Environment result, exact pending-publisher tuple,
authenticated confirmation method, public TestPyPI state, no-run/no-upload
confirmation, preserved scope, applied skills, and lifecycle notes. Do not
include credentials, cookies, tokens, or full HTTP bodies.

## 8. COMPLETION CRITERIA

Complete only if the workflow exists on the GitHub default branch, Environment
`testpypi` exists, the exact pending publisher is registered and confirmed,
public TestPyPI still has no published `0.1.0`, no workflow run/upload occurred,
and the report exists.
Lifecycle cleanup is completed according to `AGENTS.md`.
Do not start Stage 5V.4 or dispatch the workflow.

## 9. OUTPUT LIMITS

Follow `AGENTS.md`; never print credentials, full HTTP bodies, or broad external
account details.
