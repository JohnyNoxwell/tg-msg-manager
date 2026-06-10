# STAGE 5V — TESTPYPI PUBLISH SOURCE DECISION

Status: active task
Stage: 5V
Type: release preparation decision
Depends on: `docs/stages/reports/STAGE_5U_CREATE_RELEASE_CANDIDATE_TAG_REPORT.md`,
`docs/stages/reports/STAGE_5U_1_POST_RC_TAG_SMOKE_FROM_TAG_REPORT.md`,
`docs/stages/reports/STAGE_5U_2_LICENSE_METADATA_DECISION_REPORT.md`,
`docs/stages/reports/STAGE_5U_3_LICENSE_METADATA_APPLICATION_REPORT.md`, and
`docs/stages/reports/STAGE_5U_4_LICENSE_METADATA_PACKAGE_VERIFICATION_REPORT.md`
with `PASSED`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Apply `.skills/stage-reviewer/SKILL.md` before work,
`.skills/architecture-guard/SKILL.md` for scope confirmation, and
`.skills/stage-completion-auditor/SKILL.md` after report/cleanup.

This stage decides whether `v0.1.0-rc1` is an eligible TestPyPI source. Do not
run name/auth preparation, build artifacts, create a replacement tag, or start
any later stage.

## 1. PURPOSE

Compare current approved package metadata with exact `v0.1.0-rc1` source and
record whether a new RC tag is required before TestPyPI preparation continues.

## 2. FILES TO INSPECT

Required:

- `AGENTS.md`
- `pyproject.toml`
- `LICENSE`
- `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_5U_CREATE_RELEASE_CANDIDATE_TAG_REPORT.md`
- `docs/stages/reports/STAGE_5U_1_POST_RC_TAG_SMOKE_FROM_TAG_REPORT.md`
- `docs/stages/reports/STAGE_5U_2_LICENSE_METADATA_DECISION_REPORT.md`
- `docs/stages/reports/STAGE_5U_3_LICENSE_METADATA_APPLICATION_REPORT.md`
- `docs/stages/reports/STAGE_5U_4_LICENSE_METADATA_PACKAGE_VERIFICATION_REPORT.md`

Writable repository paths:

- `docs/stages/reports/STAGE_5V_TESTPYPI_PUBLISH_PREPARATION_REPORT.md`
- `docs/stages/README.md`
- lifecycle move of this stage file

## 3. HARD PROHIBITIONS

- Do not edit package/public metadata, source, tests, CLI, SQLite, dataset/
  export contracts, dependencies, build backend, package name, or version.
- Do not build/install/upload/publish, query package indexes, inspect/read
  credentials, create/delete/push tags, or create a GitHub Release.
- Do not initialize Telegram, run live commands, or read private artifacts.
- Do not start Stage 5U.5 or any TestPyPI upload stage.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify every prerequisite report exists and has `PASSED`.
2. Verify allowed repository state, exact local/remote `v0.1.0-rc1`, absence
   of local/remote stable tag `v0.1.0`, and absence of GitHub Releases for
   `v0.1.0-rc1` and `v0.1.0`.
3. Inspect current and tagged `pyproject.toml` with `tomllib`; compare name,
   version, script, license, and classifiers.
4. Write the Russian decision report, then complete lifecycle cleanup.

## 5. REQUIRED DOCS

Create only
`docs/stages/reports/STAGE_5V_TESTPYPI_PUBLISH_PREPARATION_REPORT.md`.
Update `docs/stages/README.md` only for lifecycle state.

## 6. TESTS / VERIFICATION

Required:

```bash
git status --short
git diff --check
git tag --list "v0.1.0-rc1"
git ls-remote --tags origin "refs/tags/v0.1.0-rc1"
git tag --list "v0.1.0"
git ls-remote --tags origin "refs/tags/v0.1.0"
gh release view v0.1.0-rc1
gh release view v0.1.0
git show v0.1.0-rc1:pyproject.toml
```

Use `tomllib` for current/tag metadata comparison. For `gh release view`,
classify explicit not-found as absence and network/auth errors as external
blockers. Do not claim unrun checks.

## 7. REPORT

Write the required Russian report with prerequisite statuses; current/local/
remote tag state; stable-tag/GitHub-Release absence; current and tagged
metadata; deferred package-index/auth checks; no-publish/no-tag confirmation;
changed files; commands/results; applied skills; lifecycle notes; and exact
final decision:

`NEW_RC_TAG_REQUIRED_BEFORE_TESTPYPI`

Record that `v0.1.0-rc1` predates final MIT metadata and must not be published.
Recommend only `STAGE_5U_5_RC2_TAG_PLAN`.

## 8. COMPLETION CRITERIA

- `PASSED`: prerequisites and tag checks pass, mismatch is recorded, final
  decision is exact, no forbidden action occurred, report exists, and
  lifecycle cleanup is completed according to `AGENTS.md`.
- `PARTIAL`: only exact remote/GitHub network verification is externally
  blocked.
- `FAILED`: prerequisite evidence is invalid, metadata is inconsistent beyond
  the known tag mismatch, or a forbidden action occurred.

## 9. OUTPUT LIMITS

Follow `AGENTS.md`. Do not paste full reports, diffs, or metadata dumps.
