# STAGE 5X — GITHUB RELEASE OR RELEASE-CHAIN CLOSEOUT DECISION

Status: completed
Stage: 5X
Type: release-chain decision only
Depends on: `docs/stages/reports/STAGE_5W_4_PYPI_INSTALL_SMOKE_REPORT.md` with `PASSED` and `READY_FOR_OPTIONAL_GITHUB_RELEASE_OR_RELEASE_CHAIN_CLOSEOUT`; exact annotated stable tag `v0.1.0`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md`, this task, the prerequisite report, lifecycle index, and
mandatory skills from `.skills/`. Preserve existing allowed Stage 5W.4
lifecycle/report changes. Stop on unrelated tree changes, tag mismatch, PyPI
404, or artifact checksum mismatch.

## 1. PURPOSE

Choose and record whether to recommend a separate GitHub Release creation
stage for `v0.1.0` or close the `0.1.0` release-chain without GitHub Release.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_5W_4_PYPI_INSTALL_SMOKE_REPORT.md`

Writable repository paths are limited to this task and its completed lifecycle
target, `docs/stages/reports/STAGE_5X_GITHUB_RELEASE_OR_RELEASE_CHAIN_CLOSEOUT_DECISION_REPORT.md`,
and `docs/stages/README.md`. Existing allowed Stage 5W.4 files must be
preserved unchanged.

## 3. HARD PROHIBITIONS

- Do not create/edit/upload a GitHub Release or create release notes.
- Do not publish/upload, run workflows, push, or create/modify/delete tags.
- Do not edit production code, tests, workflows, package metadata/version/
  dependencies, CLI behavior, SQLite, or dataset/export contracts.
- Do not build, install, run tests/package smoke, Telegram/live/runtime
  commands, or read credentials, tokens, secrets, `.pypirc`, shell history,
  private artifacts, sessions, exports, logs, media, or local databases.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify the allowed working tree, `git diff --check`, and exact local/remote
   annotated `v0.1.0` object and peeled target; do not edit yet.
2. Verify public main PyPI project/version, artifact filenames, and SHA-256
   against Stage 5W.4.
3. Perform only a read-only GitHub Release existence check; record any
   availability/auth/network limitation without reading credentials.
4. Apply the decision logic: absent explicit owner opt-out, recommend a
   separate Stage 5X.1 if the release does not already exist.
5. Write the Russian report and complete lifecycle cleanup.

## 5. REQUIRED DOCS

Create
`docs/stages/reports/STAGE_5X_GITHUB_RELEASE_OR_RELEASE_CHAIN_CLOSEOUT_DECISION_REPORT.md`;
update `docs/stages/README.md` only for lifecycle state; move this task to
`docs/stages/completed/` after the final report exists.

## 6. TESTS / VERIFICATION

Run working-tree/diff checks, exact local/remote tag checks, public PyPI JSON
verification, read-only GitHub Release existence check when available, and
final scope/lifecycle checks. Do not run build/install/tests/package smoke or
claim checks passed unless actually run.

## 7. REPORT

Write a Russian report with prerequisite/tree/tag/PyPI evidence, GitHub Release
existence result or limitation, options considered, selected decision and
reason, exact executed and omitted actions, preserved boundaries, changed
files, mandatory skills, final decision, and next recommended stage.

## 8. COMPLETION CRITERIA

Complete only if tag and PyPI publication evidence are verified, GitHub
Release state is checked or a limitation is recorded, one decision is selected
and justified, no forbidden action/change occurs, the report exists, and
lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

Follow `AGENTS.md`; do not print private data, full API bodies, full command
logs, release notes, or full diffs.
