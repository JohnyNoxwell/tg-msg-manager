# STAGE 5W.4 — PYPI INSTALL SMOKE

Status: completed
Stage: 5W.4
Type: post-publish install verification
Depends on: `docs/stages/reports/STAGE_5W_3_PYPI_WORKFLOW_PUBLISH_REPORT.md` with `PASSED`; exact annotated stable tag `v0.1.0`; public main PyPI version `tg-msg-manager==0.1.0`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md`, this task, the prerequisite report, and the mandatory skills
from `.skills/`. Stop before install on any preflight, tag, tree, PyPI identity,
or artifact checksum mismatch. Use only a fresh temporary virtualenv and
help-only CLI commands.

## 1. PURPOSE

Install published `tg-msg-manager==0.1.0` strictly from main PyPI in a fresh
isolated virtualenv, verify installed metadata, and run help-only CLI smoke.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_5W_3_PYPI_WORKFLOW_PUBLISH_REPORT.md`

Writable repository paths are limited to this task and its completed lifecycle
target, `docs/stages/reports/STAGE_5W_4_PYPI_INSTALL_SMOKE_REPORT.md`, and
`docs/stages/README.md`.

## 3. HARD PROHIBITIONS

- Do not edit production code, tests, workflows, package metadata/version/
  dependencies, CLI behavior, SQLite, dataset/export contracts, or tags.
- Do not run tests, live Telegram/runtime commands, workflow dispatch,
  publish/upload, GitHub Release creation, git push, or tag operations.
- Do not use TestPyPI, extra indexes, local wheels, `--find-links`, editable
  installs, or repository source for the install.
- Do not read credentials, tokens, secrets, `.pypirc`, shell history, private
  artifacts, Telegram sessions/data, exports, logs, media, or local databases.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify clean allowed tree, `git diff --check`, and exact local/remote
   annotated `v0.1.0` object and peeled target from the prerequisite report.
2. Verify public main PyPI project/version, exact wheel/sdist filenames, and
   SHA-256 against Stage 5W.3.
3. Create a fresh temporary virtualenv, upgrade pip, install only with
   `python -m pip install --index-url https://pypi.org/simple/ --no-cache-dir
   "tg-msg-manager==0.1.0"`, and record pip freeze/show.
4. Verify installed metadata, console script, LICENSE, optional imports, and
   run only the four scoped help commands; then remove the temporary workspace.
5. Write the Russian report and complete lifecycle cleanup.

## 5. REQUIRED DOCS

Create `docs/stages/reports/STAGE_5W_4_PYPI_INSTALL_SMOKE_REPORT.md`; update
`docs/stages/README.md` only for lifecycle state; move this task to
`docs/stages/completed/` after the final report exists.

## 6. TESTS / VERIFICATION

Run exact local/remote tag checks, public PyPI JSON verification, fresh main
PyPI install, pip freeze/show, installed metadata assertions, optional import
sanity, `tg-msg-manager --help`, `tg-msg-manager target --help`,
`tg-msg-manager target names --help`, `python -m tg_msg_manager.cli --help`,
temporary workspace deletion check, `git status --short`, and
`git diff --check`. Do not run tests or claim checks passed unless run.

## 7. REPORT

Write a Russian report containing prerequisite/tag/PyPI evidence, artifact
checksums, temporary path and cleanup, pip/install details, freeze/show and
metadata results, each help command exit status, preserved boundaries,
executed and explicitly omitted actions, files changed, mandatory skills,
final decision
`READY_FOR_OPTIONAL_GITHUB_RELEASE_OR_RELEASE_CHAIN_CLOSEOUT`, and recommended
next stage `STAGE_5X_GITHUB_RELEASE_OR_RELEASE_CHAIN_CLOSEOUT_DECISION`.

## 8. COMPLETION CRITERIA

Complete only if all exact tag and public PyPI evidence matches, fresh install
from main PyPI succeeds, freeze/show and installed metadata pass, all scoped
help commands exit zero without Telegram/runtime-data access, the temporary
workspace is removed, no forbidden action/change occurs, the report exists,
and lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

Follow `AGENTS.md`; do not print private data, full help output, full pip logs,
full API bodies, or full diffs.
