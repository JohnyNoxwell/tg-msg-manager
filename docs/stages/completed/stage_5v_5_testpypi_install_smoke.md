# STAGE 5V.5 — TESTPYPI INSTALL SMOKE

Status: completed
Stage: 5V.5
Type: public package install verification
Depends on:
`docs/stages/reports/STAGE_5V_3_TESTPYPI_TRUSTED_PUBLISHER_REGISTRATION_REPORT.md`
and `docs/stages/reports/STAGE_5V_4_TESTPYPI_WORKFLOW_PUBLISH_REPORT.md`
with `PASSED`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Apply stage-reviewer, architecture-guard, and
stage-completion-auditor from `.skills/`. Before execution, write a plan of at
most five bullets. This stage installs the already public TestPyPI package
`tg-msg-manager==0.1.0` into a fresh temporary venv and runs help-only CLI
smoke. It authorizes no publication, upload, workflow dispatch, or product
change. Stop if a required file is missing or prerequisite evidence is invalid.

## 1. PURPOSE

Verify that public TestPyPI package `tg-msg-manager==0.1.0` is installable with
PyPI used only as dependency fallback, has expected package metadata, and
passes safe CLI help smoke without Telegram access.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/stages/README.md`
- `pyproject.toml`
- `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`
- `docs/development/RELEASE_CANDIDATE_DECISION.md`
- `docs/stages/reports/STAGE_5V_3_TESTPYPI_TRUSTED_PUBLISHER_REGISTRATION_REPORT.md`
- `docs/stages/reports/STAGE_5V_4_TESTPYPI_WORKFLOW_PUBLISH_REPORT.md`
- `docs/stages/reports/STAGE_5U_8_RC2_ISOLATED_INSTALL_SMOKE_REPORT.md`

Writable repository paths are limited to
`docs/stages/reports/STAGE_5V_5_TESTPYPI_INSTALL_SMOKE_REPORT.md`,
`docs/stages/README.md` only for lifecycle state, and lifecycle movement of
this stage file. Temporary files are allowed only under
`/tmp/tg-msg-manager-5v5-*`. Do not inspect existing unrelated report files,
source, tests, private artifacts, credentials, Telegram sessions, exports,
logs, media, screenshots, databases, `.pypirc`, or shell history.

## 3. HARD PROHIBITIONS

- Do not change source, tests, CLI behavior, package metadata/version/
  dependencies, `pyproject.toml`, workflows, SQLite schema/migrations/
  `user_version`, dataset/export contracts, or unrelated docs.
- Do not publish/upload to TestPyPI or PyPI, rerun publishing workflows, start
  a PyPI publication stage, or create/delete/push tags or releases.
- Do not read credentials, tokens, secrets, `.pypirc`, shell history, private
  artifacts, Telegram sessions, or real exports/logs/media/screenshots/DBs.
- Do not run Telegram live commands or initialize a Telegram client.
- Do not use project, user, or global environments for installation.
- Do not leave temporary or install/build artifacts in the repository.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify the required files and prerequisite reports. Require 5V.3 and 5V.4
   status `PASSED` and their stated evidence: registered TestPyPI Trusted
   Publisher, GitHub Environment `testpypi`, configured workflow, successful
   build/publish jobs, public TestPyPI project/version/files, and no PyPI
   publication. Stop before install smoke if evidence is missing or ambiguous.
2. Record repository baseline with:
   `git status --short`, `git diff --check`,
   `git tag --list "v0.1.0-rc2"`, and
   `git ls-remote --tags origin "refs/tags/v0.1.0-rc2"`.
   Require the local tag and, unless network/auth prevents verification, the
   remote tag. Do not modify or discard existing worktree changes.
3. Query public JSON endpoints
   `https://test.pypi.org/pypi/tg-msg-manager/0.1.0/json` and
   `https://pypi.org/pypi/tg-msg-manager/json` with `urllib.request`.
   Require TestPyPI name/version `tg-msg-manager`/`0.1.0`, wheel and sdist, and
   main PyPI `404 NOT_FOUND`. Record concise output only, not full JSON.
4. Create `tmpdir="$(mktemp -d /tmp/tg-msg-manager-5v5-XXXXXX)"`, register
   failure-safe cleanup, create `$tmpdir/install-venv`, upgrade pip there, and
   install exactly:
   `"$tmpdir/install-venv/bin/python" -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ "tg-msg-manager==0.1.0"`.
   Never install into or create artifacts inside the repository.
5. In the temporary venv, verify `importlib.metadata.distribution` reports
   name `tg-msg-manager`, version `0.1.0`, `LICENSE` in `License-File`, and the
   MIT license classifier. Run only:
   `tg-msg-manager --help`, `tg-msg-manager target --help`,
   `tg-msg-manager target names --help`, and
   `python -m tg_msg_manager.cli --help`.
   Then run `python -m pip show tg-msg-manager` and `python -m pip freeze`;
   record only concise package/version, dependency-resolution, and temporary
   install-location evidence.
6. Remove the temporary root on success or failure and verify
   `test ! -e "$tmpdir"`. Run final repository checks, write the Russian
   factual report, apply stage-completion-auditor, and complete lifecycle
   cleanup only when status is `PASSED`. Do not start the next stage.

## 5. REQUIRED DOCS

Create only
`docs/stages/reports/STAGE_5V_5_TESTPYPI_INSTALL_SMOKE_REPORT.md`. Update
`docs/stages/README.md` only for lifecycle state. On `PASSED`, move this task
to `docs/stages/completed/stage_5v_5_testpypi_install_smoke.md`; on `FAILED`
or `PARTIAL`, leave it active.

## 6. TESTS / VERIFICATION

Run the exact baseline, public metadata, isolated install, metadata, help-only
CLI, origin, cleanup, and final repository checks specified above. Final
repository checks must include:

```bash
git status --short
git diff --check
find . -maxdepth 2 \( -name "dist" -o -name "build" -o -name "*.egg-info" -o -name ".venv*" \) -print
```

Classify `PARTIAL` only for external public network/index/dependency-resolution
failure or remote tag network/auth failure when no forbidden action occurred.
Classify `FAILED` for a missing required file, invalid prerequisites, missing
public TestPyPI package, unexpected main PyPI project, project-owned install/
metadata/CLI failure, cleanup failure, or any forbidden action. Do not claim a
check passed unless it was run. Record skipped commands and exact reasons.

## 7. REPORT

Write a compact Russian report containing: status; goal; prerequisite evidence;
TestPyPI metadata and PyPI absence checks; local/remote tag result; temporary
venv path; exact redacted-safe pip command shape; install and installed
metadata results; CLI smoke results; commands not run and reasons; cleanup;
files changed; no-publish/no-upload/no-workflow-rerun and no-tag/release
confirmations; preserved production/tests/CLI/SQLite/dataset/package/
dependency/version/workflow scope; no Telegram access/client initialization;
final recommendation; applied skill paths; and lifecycle notes. Do not include
full JSON, full help output, full dependency dumps, credentials, or secrets.

For `PASSED`, final recommendation is:
`Proceed to STAGE_5W_PYPI_PUBLISH_PREPARATION`.

## 8. COMPLETION CRITERIA

Status is `PASSED` only if prerequisites are valid, public TestPyPI
`tg-msg-manager==0.1.0` and its wheel/sdist are verified, main PyPI remains
absent, installation and expected metadata succeed in a fresh external venv,
all four help-only CLI commands pass, cleanup succeeds, final repository state
contains only allowed stage-owned changes, no forbidden action occurred, the
report exists, stage-completion-auditor passes, and lifecycle cleanup is
completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

Follow `AGENTS.md`. Keep interim output to blockers or required questions.
Final response must use the required `AGENTS.md` structure and stay within its
character limit. Do not print full diffs, JSON, help output, dependency dumps,
logs, credentials, secrets, or broad summaries.
