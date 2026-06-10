# Stage 5U.1 - Post-RC Tag Smoke From Tag

Status: completed
Type: release verification
Depends on: Stage 5U PASSED and tag `v0.1.0-rc1`

## CODEX ENTRY CONTRACT

Read `AGENTS.md`, this task, and only listed prerequisite docs. Apply
`stage-reviewer`, `architecture-guard`, and `stage-completion-auditor`.

## PURPOSE

Export, build, install, and run safe help-only CLI smoke from the exact existing
tag `v0.1.0-rc1` in an isolated temporary workspace.

## FILES TO INSPECT

- `pyproject.toml`
- `docs/stages/README.md`
- `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`
- `docs/development/RELEASE_CANDIDATE_DECISION.md`
- `docs/stages/reports/STAGE_5U_CREATE_RELEASE_CANDIDATE_TAG_REPORT.md`
- `docs/stages/reports/STAGE_5R_0_PACKAGE_BUILD_DRY_RUN_REPORT.md`
- `docs/stages/reports/STAGE_5R_BUILD_AND_INSTALL_DRY_RUN_REPORT.md`

## HARD PROHIBITIONS

- Do not change code, tests, package metadata/version/dependencies, CLI, SQLite,
  dataset contracts, or unrelated docs.
- Do not create/delete/push tags, publish packages, create a GitHub Release or
  stable release, access Telegram/private artifacts, or start the next stage.
- Build/install artifacts may exist only under `/tmp/tg-msg-manager-5u1-*` and
  must be removed before completion.

## ATOMIC IMPLEMENTATION TASKS

1. Verify Stage 5U evidence, working tree, and local/remote annotated tag.
2. Export exact tag source to a new temporary directory and inspect metadata.
3. Build sdist/wheel, install wheel into a fresh venv, and run help-only smoke.
4. Record artifacts/checksums/results and remove the temporary workspace.
5. Create the Russian report and complete lifecycle cleanup.

## REQUIRED DOCS

- `docs/stages/reports/STAGE_5U_1_POST_RC_TAG_SMOKE_FROM_TAG_REPORT.md`
- `docs/stages/README.md`
- Move this task to `docs/stages/completed/` after completion.

## TESTS / VERIFICATION

- Verify local/remote `v0.1.0-rc1` and target commit.
- Export with `git archive`, inspect exported `pyproject.toml`, build sdist and
  wheel, install wheel in a fresh venv, run the four scoped help commands.
- Verify cleanup, repository artifact absence, `git status`, and
  `git diff --check`. Do not claim checks not run.

## REPORT

Write the required Russian report with evidence, commands/results, temp path,
artifacts/checksums, preserved boundaries, applied skills, and lifecycle notes.

## COMPLETION CRITERIA

Complete only if exact tag source builds and installs, all scoped help commands
pass, temp cleanup succeeds, no repository artifacts or forbidden changes
exist, the report exists, and lifecycle cleanup is complete.

## OUTPUT LIMITS

Follow `AGENTS.md`; do not paste full diffs or full help output.
