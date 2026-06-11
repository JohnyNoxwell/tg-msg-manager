# STAGE 5W.0 — STABLE TAG v0.1.0 PLAN

Status: completed
Stage: 5W.0
Type: release decision / tag plan
Depends on:
`docs/stages/reports/STAGE_5W_PYPI_PUBLISH_PREPARATION_REPORT.md` with
`PASSED` and final decision `STABLE_TAG_REQUIRED_BEFORE_PYPI`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Apply stage-reviewer, architecture-guard, and
stage-completion-auditor from `.skills/`. Before execution, write a plan of at
most five bullets. This stage is planning-only: do not create or push a stable
tag, publish to PyPI/TestPyPI, create a GitHub Release, or start the next
stage. Stop if required evidence is missing, failed, or ambiguous.

## 1. PURPOSE

Verify that the repository has enough evidence to create stable tag `v0.1.0`.
Record the exact peeled target commit, tag contract, future commands, and the
separate next stage authorized to create and push the tag. Main PyPI
publication of package version `0.1.0` must use explicit stable tag `v0.1.0`,
not RC tag `v0.1.0-rc2`.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `pyproject.toml`
- `LICENSE`
- `README.md`
- `docs/stages/README.md`
- `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`
- `docs/development/RELEASE_CANDIDATE_DECISION.md`
- `docs/stages/reports/STAGE_5U_6_CREATE_RC2_TAG_REPORT.md`
- `docs/stages/reports/STAGE_5U_7_RC2_PACKAGE_ARTIFACT_VERIFICATION_REPORT.md`
- `docs/stages/reports/STAGE_5U_8_RC2_ISOLATED_INSTALL_SMOKE_REPORT.md`
- `docs/stages/reports/STAGE_5V_4_TESTPYPI_WORKFLOW_PUBLISH_REPORT.md`
- `docs/stages/reports/STAGE_5V_5_TESTPYPI_INSTALL_SMOKE_REPORT.md`
- `docs/stages/reports/STAGE_5W_PYPI_PUBLISH_PREPARATION_REPORT.md`

Writable repository paths are limited to
`docs/stages/reports/STAGE_5W_0_STABLE_TAG_V0_1_0_PLAN_REPORT.md`,
`docs/stages/README.md` only for lifecycle state, and lifecycle movement of
this stage file. Do not inspect source, tests, unrelated existing reports,
private artifacts, credentials, Telegram sessions, exports, logs, media,
screenshots, databases, `.pypirc`, or shell history.

## 3. HARD PROHIBITIONS

- Do not change production code, tests, CLI behavior, `pyproject.toml`,
  package metadata/version/dependencies/build backend, workflows, SQLite
  schema/migrations/`user_version`, dataset/export contracts, or unrelated
  docs.
- Do not publish/upload to PyPI or TestPyPI, rerun publishing workflows,
  create a GitHub Release, or create/delete/overwrite/push any git tag.
- Do not read credentials, tokens, secrets, `.pypirc`, shell history, private
  artifacts, Telegram sessions, or real exports/logs/media/screenshots/DBs.
- Do not run Telegram live commands, initialize a Telegram client, or start
  `STAGE_5W_0_1`, `STAGE_5W_1`, or any publishing stage.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify all required files exist. Require each prerequisite report to state
   `PASSED`; require Stage 5W final decision
   `STABLE_TAG_REQUIRED_BEFORE_PYPI`. Record exact report paths, statuses, and
   evidence for RC2 creation/push, artifact verification and `twine check`,
   isolated wheel/help smoke, TestPyPI publish, and TestPyPI install smoke.
2. Run baseline repository checks. Stop with `FAILED` if unrelated worktree
   changes exist; do not modify or discard them.
3. Inspect `pyproject.toml` with `tomllib`. Require name `tg-msg-manager`,
   version `0.1.0`, script
   `tg-msg-manager = tg_msg_manager.cli:main`, license-file metadata, MIT
   classifier, and unchanged runtime dependencies. Verify `LICENSE` contains
   `MIT License` and `Copyright (c) 2026 R.P.`.
4. Verify local and remote annotated tag `v0.1.0-rc2`. Record the local and
   remote tag objects and peeled target commits; require peeled targets to
   match and identify the stable-ready commit. Classify network/auth failure
   as `PARTIAL`.
5. Verify `v0.1.0` is absent locally and remotely. If it exists, stop with
   `FAILED`; do not delete or overwrite it.
6. Query public PyPI JSON for project `tg-msg-manager` and version `0.1.0`.
   Require both to be `404 NOT_FOUND`. Classify network failure as `PARTIAL`;
   block on unknown ownership or existing version `0.1.0`.
7. Record planned tag `v0.1.0` targeting the RC2 peeled commit, exact future
   create/push commands, and rollback commands as documentation only. On full
   success select exact final decision
   `READY_FOR_STAGE_5W_0_1_CREATE_STABLE_TAG_V0_1_0` and recommend only
   `STAGE_5W_0_1_CREATE_STABLE_TAG_V0_1_0`.
8. Run final checks, write the Russian factual report, apply
   stage-completion-auditor, and complete lifecycle cleanup only on `PASSED`.
   Do not start the recommended stage.

## 5. REQUIRED DOCS

Create only
`docs/stages/reports/STAGE_5W_0_STABLE_TAG_V0_1_0_PLAN_REPORT.md`. Update
`docs/stages/README.md` only for lifecycle state. On `PASSED`, move this task
to `docs/stages/completed/stage_5w_0_stable_tag_v0_1_0_plan.md`; on `FAILED`
or `PARTIAL`, leave it active.

## 6. TESTS / VERIFICATION

Run:

```bash
git status --short
git diff --check
python3 - <<'PY'
import pathlib
import tomllib

project = tomllib.loads(pathlib.Path("pyproject.toml").read_text())["project"]
for key in ("name", "version", "requires-python", "scripts", "license",
            "classifiers", "dependencies"):
    print(f"{key}:", project.get(key))
PY
python3 - <<'PY'
from pathlib import Path

text = Path("LICENSE").read_text()
print("has_mit_header:", "MIT License" in text)
print("has_holder:", "Copyright (c) 2026 R.P." in text)
PY
git tag --list "v0.1.0-rc2"
git cat-file -t refs/tags/v0.1.0-rc2
git rev-parse refs/tags/v0.1.0-rc2
git rev-parse refs/tags/v0.1.0-rc2^{}
git ls-remote --tags origin refs/tags/v0.1.0-rc2 'refs/tags/v0.1.0-rc2^{}'
git tag --list "v0.1.0"
git ls-remote --tags origin refs/tags/v0.1.0 'refs/tags/v0.1.0^{}'
python3 - <<'PY'
import urllib.error
import urllib.request

for url in (
    "https://pypi.org/pypi/tg-msg-manager/json",
    "https://pypi.org/pypi/tg-msg-manager/0.1.0/json",
):
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            print(url, response.status, "EXISTS")
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            print(url, exc.code, "NOT_FOUND")
        else:
            print(url, exc.code, "HTTP_ERROR")
            raise
PY
git status --short
git diff --check
```

The planned commands to record but never execute are:

```bash
git tag -a v0.1.0 <RC2_PEELED_TARGET_COMMIT> -m "tg-msg-manager v0.1.0"
git push origin v0.1.0
git tag -d v0.1.0
git push origin :refs/tags/v0.1.0
```

Do not claim a check passed unless it was run. Confirm final changes are
limited to the report and lifecycle docs, and no tag/release/publish action
occurred.

## 7. REPORT

Write a compact Russian report containing: status; goal; prerequisite report
paths/statuses/evidence; git state; package metadata and MIT license checks;
local/remote RC2 tag objects and peeled commits; stable-tag absence; main PyPI
project/version state; exact planned tag name and peeled target; future
create/push commands; rollback commands as documentation only; commands run
and skipped with reasons; files changed; confirmations of no publish/upload,
tag/release operation, credential/secret access, or
production/tests/CLI/SQLite/dataset/export/dependency/version/workflow change;
exact final decision; next recommended stage; applied skill paths; and
lifecycle notes.

## 8. COMPLETION CRITERIA

Status is `PASSED` only if all prerequisite reports and evidence are valid,
repository state is acceptable, metadata and MIT license checks pass,
`v0.1.0-rc2` exists locally/remotely with matching peeled target, `v0.1.0` is
absent locally/remotely, main PyPI state is checked and non-blocking, the
exact tag target/future commands/final decision are recorded, no forbidden
action occurred, the report exists, stage-completion-auditor passes, and
lifecycle cleanup is completed according to `AGENTS.md`.

Status is `PARTIAL` only for external network/auth/tooling failures while
local evidence is valid and no forbidden action occurred. Use `FAILED` for
invalid or missing prerequisites/metadata/license/tag evidence, blocking PyPI
state, forbidden actions, or changes outside allowed scope.

## 9. OUTPUT LIMITS

Follow `AGENTS.md`. Keep interim output to blockers or required questions.
Final response must use the required `AGENTS.md` structure and stay within its
character limit. Do not print full diffs, metadata dumps, HTTP bodies, logs,
credentials, secrets, or broad summaries.
