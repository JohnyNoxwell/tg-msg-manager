# STAGE 5U.6 — CREATE RC2 TAG

Status: active task
Stage: 5U.6
Type: release operation
Depends on: `docs/stages/reports/STAGE_5U_5_RC2_TAG_PLAN_REPORT.md` with
`PASSED`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Apply stage-reviewer, architecture-guard, and
stage-completion-auditor from `.skills/`. This stage may create and push only
the planned annotated tag `v0.1.0-rc2`.

## 1. PURPOSE

Create and push `v0.1.0-rc2` on the exact commit approved by Stage 5U.5.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `pyproject.toml`
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_5U_5_RC2_TAG_PLAN_REPORT.md`

Writable paths: `docs/stages/reports/STAGE_5U_6_CREATE_RC2_TAG_REPORT.md`,
`docs/stages/README.md`, lifecycle move of this stage file, and the authorized
local/remote tag ref `v0.1.0-rc2`.

## 3. HARD PROHIBITIONS

- Do not edit production/tests/package metadata/version/dependencies/CLI/
  SQLite/dataset contracts or unrelated docs.
- Do not build/install/publish/upload, create GitHub Release/stable tag, or
  create/delete/overwrite/push any tag except new `v0.1.0-rc2`.
- Do not access credentials, Telegram, or private artifacts.
- Do not start Stage 5U.7.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify planned commit, clean state, and local/remote tag absence.
2. Create annotated `v0.1.0-rc2` on the exact approved commit.
3. Push only `origin v0.1.0-rc2` and verify exact remote tag/peeled target.
4. Write the Russian report and complete lifecycle cleanup.

## 5. REQUIRED DOCS

Create only `docs/stages/reports/STAGE_5U_6_CREATE_RC2_TAG_REPORT.md`; update
the stage index only for lifecycle state.

## 6. TESTS / VERIFICATION

Run exact status/diff, commit, local annotated-tag, peeled-target, push, and
remote-tag checks. Do not use `git push --tags`.

## 7. REPORT

Record prerequisite evidence, exact target/tag IDs, commands/results, push and
remote verification, no-publish confirmation, preserved scope, rollback
commands as documentation only, applied skills, lifecycle notes, and
recommendation `Proceed to STAGE_5U_7_RC2_PACKAGE_ARTIFACT_VERIFICATION`.

## 8. COMPLETION CRITERIA

Complete only when the exact annotated tag exists locally/remotely on the
approved commit, no other tag/action occurred, and report exists.
Lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

Follow `AGENTS.md`; do not paste full git output or report bodies.
