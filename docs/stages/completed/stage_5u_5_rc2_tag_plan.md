# STAGE 5U.5 — RC2 TAG PLAN

Status: active task
Stage: 5U.5
Type: release decision
Depends on:
`docs/stages/reports/STAGE_5V_TESTPYPI_PUBLISH_PREPARATION_REPORT.md` with
`PASSED` and `NEW_RC_TAG_REQUIRED_BEFORE_TESTPYPI`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Apply stage-reviewer, architecture-guard, and
stage-completion-auditor from `.skills/`. This stage plans only; do not create
or push a tag and do not start Stage 5U.6.

## 1. PURPOSE

Select the exact commit and annotated tag contract for `v0.1.0-rc2` after
confirming that the commit contains approved MIT metadata.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `pyproject.toml`
- `LICENSE`
- `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`
- `docs/development/RELEASE_CANDIDATE_DECISION.md`
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_5V_TESTPYPI_PUBLISH_PREPARATION_REPORT.md`
- `docs/stages/reports/STAGE_5U_4_LICENSE_METADATA_PACKAGE_VERIFICATION_REPORT.md`

Writable paths: `docs/stages/reports/STAGE_5U_5_RC2_TAG_PLAN_REPORT.md`,
`docs/stages/README.md`, and lifecycle move of this stage file.

## 3. HARD PROHIBITIONS

- Do not edit code/docs/package metadata except required stage docs.
- Do not build/install/publish/upload or create/delete/push any tag.
- Do not change package version `0.1.0`; tag suffix `rc2` is tag identity, not
  package-version metadata.
- Do not access credentials, Telegram, or private artifacts.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify Stage 5V decision and clean repository state.
2. Inspect HEAD package identity, MIT metadata, and exact commit ID.
3. Verify local/remote `v0.1.0-rc2` is absent.
4. Record the exact tag plan and complete report/lifecycle cleanup.

## 5. REQUIRED DOCS

Create only `docs/stages/reports/STAGE_5U_5_RC2_TAG_PLAN_REPORT.md`; update the
stage index only for lifecycle state.

## 6. TESTS / VERIFICATION

Run `git status --short`, `git diff --check`, `git rev-parse HEAD`, structured
`tomllib` inspection, `git tag --list "v0.1.0-rc2"`, and exact
`git ls-remote --tags origin "refs/tags/v0.1.0-rc2"`.

## 7. REPORT

Write a Russian report with target commit, package/tag identity distinction,
metadata evidence, absence checks, commands/results, preserved scope, applied
skills, lifecycle notes, and recommendation `Proceed to STAGE_5U_6_CREATE_RC2_TAG`.

## 8. COMPLETION CRITERIA

Complete only if the exact eligible commit and tag contract are recorded,
`v0.1.0-rc2` is absent locally/remotely, no forbidden action occurred, and
lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

Follow `AGENTS.md`; do not paste full diffs or report bodies.
