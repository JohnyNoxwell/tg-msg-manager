# STAGE 5U.1 — POST-RC TAG SMOKE FROM v0.1.0-rc1

Status: completed
Stage: 5U.1
Type: release verification
Depends on: `docs/stages/reports/STAGE_5U_CREATE_RELEASE_CANDIDATE_TAG_REPORT.md` with `PASSED`; existing local and remote annotated tag `v0.1.0-rc1`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md`, this task, and only the listed prerequisite files. Apply
`stage-reviewer`, `architecture-guard`, and `stage-completion-auditor` from
`.skills/`. Stop on missing prerequisite evidence, unrelated working-tree
changes, wrong tag metadata/target, or project-owned smoke failure.

## 1. PURPOSE

Verify that exact tag `v0.1.0-rc1` can be exported, built, installed, and
executed through safe help-only CLI commands in isolated temporary environments.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `docs/stages/README.md`
- `pyproject.toml`
- `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`
- `docs/development/RELEASE_CANDIDATE_DECISION.md`
- `docs/stages/reports/STAGE_5U_CREATE_RELEASE_CANDIDATE_TAG_REPORT.md`
- `docs/stages/reports/STAGE_5R_0_PACKAGE_BUILD_DRY_RUN_REPORT.md`
- `docs/stages/reports/STAGE_5R_BUILD_AND_INSTALL_DRY_RUN_REPORT.md`

Writable repository paths are limited to this task file, its lifecycle target,
`docs/stages/reports/STAGE_5U_1_POST_RC_TAG_SMOKE_FROM_TAG_REPORT.md`, and
`docs/stages/README.md` only when required for lifecycle state.

## 3. HARD PROHIBITIONS

- Do not change production code, tests, package metadata/version/dependencies,
  CLI behavior, SQLite schema, dataset/export contracts, or unrelated docs.
- Do not create, push, delete, or modify tags; do not publish to TestPyPI/PyPI,
  create a GitHub Release, or create a stable release.
- Do not access credentials, Telegram sessions, private artifacts, real
  exports/logs/media/screenshots/DB files, or initialize a Telegram client.
- Do not start the next stage.
- Keep all build/install artifacts under a new `/tmp/tg-msg-manager-5u1-*`
  directory and remove it before completion.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify Stage 5U evidence, clean working tree, and exact local/remote annotated
   tag target `2a3b57deed5be899a27577b43e02904123f85823`.
2. Export exact tag source with `git archive` and verify package name, version,
   and console-script metadata.
3. Build sdist/wheel in an isolated build venv, record names/checksums, install
   the wheel in a separate fresh venv, and run only the four scoped help commands.
4. Remove the temporary workspace and verify repository/tag state.
5. Write the Russian report and complete lifecycle cleanup.

## 5. REQUIRED DOCS

Create or refresh
`docs/stages/reports/STAGE_5U_1_POST_RC_TAG_SMOKE_FROM_TAG_REPORT.md`; update
`docs/stages/README.md` only for lifecycle state; move this task to
`docs/stages/completed/` after the final report exists.

## 6. TESTS / VERIFICATION

Run the exact local/remote tag checks, `git status --short`, `git diff --check`,
tag-source metadata inspection, isolated build/install, four help-only smoke
commands, SHA-256 checksums, cleanup verification, and final repository/tag
checks. Do not claim a check passed unless it ran.

## 7. REPORT

Write the required Russian report with status, prerequisite/tag evidence,
temporary path, source metadata, commands/results, artifact names/checksums,
install/smoke/cleanup results, preserved boundaries, skipped commands, applied
skills, lifecycle notes, and final recommendation.

## 8. COMPLETION CRITERIA

Complete only if exact tag source builds and installs, all scoped help commands
pass, cleanup succeeds, local and remote tags remain correct, no repository
artifacts or forbidden changes exist, the report exists, and lifecycle cleanup
is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

Follow `AGENTS.md`; do not paste full diffs, full help output, credentials, or
private data.
