# STAGE 5X.1 — GITHUB RELEASE CREATION

Status: completed
Stage: 5X.1
Type: GitHub Release creation
Depends on: `docs/stages/reports/STAGE_5X_GITHUB_RELEASE_OR_RELEASE_CHAIN_CLOSEOUT_DECISION_REPORT.md` with `PASSED` and `READY_FOR_STAGE_5X_1_GITHUB_RELEASE_CREATION`; exact annotated stable tag `v0.1.0`; public main PyPI `tg-msg-manager==0.1.0`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md`, this task, the prerequisite report, lifecycle index, and
mandatory skills from `.skills/`. Stop before release creation on unrelated
tree changes, tag mismatch, unverified PyPI state, existing GitHub Release, or
GitHub auth/permission/network failure.

## 1. PURPOSE

Create and verify one deterministic non-draft, non-prerelease GitHub Release
for existing stable tag `v0.1.0`, then close release-chain `0.1.0`.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_5X_GITHUB_RELEASE_OR_RELEASE_CHAIN_CLOSEOUT_DECISION_REPORT.md`

Writable repository paths are limited to this task and its completed lifecycle
target, `docs/stages/reports/STAGE_5X_1_GITHUB_RELEASE_CREATION_REPORT.md`, and
`docs/stages/README.md`. A temporary release-notes file outside the repository
is allowed and must be removed.

## 3. HARD PROHIBITIONS

- Do not create/modify/delete/push tags, run `git push`, publish/upload to
  PyPI/TestPyPI, dispatch workflows, or upload GitHub Release assets.
- Do not edit production code, tests, workflows, package metadata/version/
  dependencies, CLI behavior, SQLite, or dataset/export contracts.
- Do not build, install, run tests/package smoke, Telegram/live/runtime
  commands, or read credentials, tokens, secrets, `.pypirc`, shell history,
  private artifacts, sessions, exports, logs, media, or local databases.
- Do not use `gh release edit/upload/delete`, `--generate-notes`, `--target`,
  draft, or prerelease options.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify allowed tree, `git diff --check`, and exact local/remote annotated
   `v0.1.0` object and peeled target; do not create the release yet.
2. Verify public PyPI project/version, artifact filenames, and SHA-256 against
   the prerequisite report; stop if unavailable or mismatched.
3. Confirm the GitHub Release is absent, create deterministic temporary notes,
   and create exactly one release for existing tag `v0.1.0`.
4. Verify structured release fields/body, confirm local/remote tag evidence is
   unchanged, and remove the temporary notes file.
5. Write the Russian report and complete lifecycle cleanup.

## 5. REQUIRED DOCS

Create `docs/stages/reports/STAGE_5X_1_GITHUB_RELEASE_CREATION_REPORT.md`;
update `docs/stages/README.md` only for lifecycle state and release-chain
closure; move this task to `docs/stages/completed/` after the final report
exists.

## 6. TESTS / VERIFICATION

Run working-tree/diff checks, exact local/remote tag checks before and after,
public PyPI JSON verification, GitHub Release absence check, exact
`gh release create v0.1.0 --repo JohnyNoxwell/tg-msg-manager --title
"tg-msg-manager v0.1.0" --notes-file "$NOTES"`, structured release verification,
temporary-file cleanup check, and final scope/lifecycle checks. Do not run
build/install/tests/package smoke or claim checks passed unless actually run.

## 7. REPORT

Write a Russian report containing prerequisite/tree/tag/PyPI evidence,
pre-check, notes method, exact create command, release URL and structured
verification, post-create tag evidence, executed and explicitly omitted
actions, no-assets confirmation, preserved boundaries, changed files,
mandatory skills, final decision `RELEASE_CHAIN_0_1_0_CLOSED`, and next stage
`NONE`.

## 8. COMPLETION CRITERIA

Complete only if all prerequisite evidence matches, the release was absent
before creation, the verified release has the exact tag/title/body checks and
is neither draft nor prerelease, tags remain unchanged, no forbidden action or
change occurs, the report exists, and lifecycle cleanup is completed according
to `AGENTS.md`.

## 9. OUTPUT LIMITS

Follow `AGENTS.md`; do not print private data, full API bodies, full command
logs, full release notes, or full diffs.
