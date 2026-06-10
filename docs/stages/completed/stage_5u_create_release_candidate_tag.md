# Stage 5U - Create Release Candidate Tag

Status: completed
Type: release operation
Depends on: Stage 5P, 5Q.3, 5R.0, 5R.1, 5S, and 5T reports

## CODEX ENTRY CONTRACT

Read `AGENTS.md`, this task, and only the files listed below. Apply
`stage-reviewer`, `architecture-guard`, and `stage-completion-auditor`.

## PURPOSE

Create and push only the annotated release-candidate tag `v0.1.0-rc1`, then
record evidence. This is not a stable release, package publish, GitHub Release,
version bump, build, install, or post-RC smoke stage.

## FILES TO INSPECT

- `pyproject.toml`
- `docs/stages/README.md`
- `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`
- `docs/development/RELEASE_CANDIDATE_DECISION.md`
- `docs/stages/reports/STAGE_5P_POST_REFACTOR_FULL_VERIFICATION_REPORT.md`
- `docs/stages/reports/STAGE_5Q_RELEASE_CANDIDATE_CHECKLIST_REPORT.md`
- `docs/stages/reports/STAGE_5R_0_PACKAGE_BUILD_DRY_RUN_REPORT.md`
- `docs/stages/reports/STAGE_5R_BUILD_AND_INSTALL_DRY_RUN_REPORT.md`
- `docs/stages/reports/STAGE_5S_RELEASE_CANDIDATE_TAG_PLAN_REPORT.md`
- `docs/stages/reports/STAGE_5T_STABLE_RELEASE_DECISION_REPORT.md`

## HARD PROHIBITIONS

- Do not change production code, tests, package metadata, dependencies, version,
  CLI behavior, SQLite schema, dataset contracts, or unrelated docs.
- Do not build/install/publish packages, create a GitHub Release, create stable
  tag `v0.1.0`, delete/overwrite tags, read private artifacts, or start post-RC
  smoke.
- Git tag operations are limited to creating `v0.1.0-rc1` and pushing only
  `origin v0.1.0-rc1`.

## ATOMIC IMPLEMENTATION TASKS

1. Confirm all prerequisite evidence and package version `0.1.0`.
2. Confirm a clean working tree and absence of local/remote `v0.1.0-rc1`.
3. Record HEAD, create annotated tag `v0.1.0-rc1`, and verify it locally.
4. Push only that tag to origin and verify the remote tag.
5. Create the Russian evidence report and complete lifecycle cleanup.

## REQUIRED DOCS

- `docs/stages/reports/STAGE_5U_CREATE_RELEASE_CANDIDATE_TAG_REPORT.md`
- `docs/stages/README.md`
- Move this task to `docs/stages/completed/` after completion.

## TESTS / VERIFICATION

- Parse package identity/version/scripts from `pyproject.toml` using `tomllib`.
- Run `git status --short`, `git diff --check`, local/remote tag checks,
  `git rev-parse HEAD`, and limited `git log`.
- Verify the annotated local tag and exact remote tag after push.
- Do not claim a check passed unless it was run.

## REPORT

Write the required Russian report with status, prerequisite evidence, package
identity, commands/results, target commit, local/remote verification, push
result, changed files, preserved boundaries, rollback commands, applied skills,
lifecycle notes, and final recommendation.

## COMPLETION CRITERIA

Complete only when prerequisites pass, version is `0.1.0`, the tag was absent
before execution, the annotated local tag exists, push and remote verification
pass, the report exists, lifecycle cleanup is complete, and no forbidden change
occurred.

## OUTPUT LIMITS

Follow `AGENTS.md`; do not paste full diffs or large command output.
