# STAGE 5W — PYPI PUBLISH PREPARATION

Status: completed
Stage: 5W
Type: release preparation audit
Depends on:
`docs/stages/reports/STAGE_5U_6_CREATE_RC2_TAG_REPORT.md`,
`docs/stages/reports/STAGE_5U_7_RC2_PACKAGE_ARTIFACT_VERIFICATION_REPORT.md`,
`docs/stages/reports/STAGE_5U_8_RC2_ISOLATED_INSTALL_SMOKE_REPORT.md`,
`docs/stages/reports/STAGE_5V_3_TESTPYPI_TRUSTED_PUBLISHER_REGISTRATION_REPORT.md`,
`docs/stages/reports/STAGE_5V_4_TESTPYPI_WORKFLOW_PUBLISH_REPORT.md`, and
`docs/stages/reports/STAGE_5V_5_TESTPYPI_INSTALL_SMOKE_REPORT.md`
with `PASSED`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Apply stage-reviewer, architecture-guard, and
stage-completion-auditor from `.skills/`. Before execution, write a plan of at
most five bullets. This is a preparation-only audit for main PyPI publication
of `tg-msg-manager==0.1.0`. It authorizes no upload, publication, workflow
creation or dispatch, tag operation, GitHub Release, credential access, or
product change. Stop if a required file is missing or prerequisite evidence is
missing, failed, or ambiguous.

## 1. PURPOSE

Verify prerequisite release evidence, current package metadata, TestPyPI state,
main PyPI name/version availability, and the contract for a later Trusted
Publishing workflow. Decide whether a stable `v0.1.0` tag is required before
main PyPI publication. Do not perform publication or create the workflow/tag.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/stages/README.md`
- `pyproject.toml`
- `README.md`
- `LICENSE`
- `.github/workflows/testpypi-publish.yml`
- `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`
- `docs/development/RELEASE_CANDIDATE_DECISION.md`
- `docs/stages/reports/STAGE_5U_6_CREATE_RC2_TAG_REPORT.md`
- `docs/stages/reports/STAGE_5U_7_RC2_PACKAGE_ARTIFACT_VERIFICATION_REPORT.md`
- `docs/stages/reports/STAGE_5U_8_RC2_ISOLATED_INSTALL_SMOKE_REPORT.md`
- `docs/stages/reports/STAGE_5V_3_TESTPYPI_TRUSTED_PUBLISHER_REGISTRATION_REPORT.md`
- `docs/stages/reports/STAGE_5V_4_TESTPYPI_WORKFLOW_PUBLISH_REPORT.md`
- `docs/stages/reports/STAGE_5V_5_TESTPYPI_INSTALL_SMOKE_REPORT.md`

Writable repository paths are limited to
`docs/stages/reports/STAGE_5W_PYPI_PUBLISH_PREPARATION_REPORT.md`,
`docs/stages/README.md` only for lifecycle state, and lifecycle movement of
this stage file. Do not inspect existing unrelated report files, source, tests,
private artifacts, credentials, Telegram sessions, exports, logs, media,
screenshots, databases, `.pypirc`, or shell history.

## 3. HARD PROHIBITIONS

- Do not change production code, tests, CLI behavior, `pyproject.toml`,
  package metadata/version/dependencies/build backend, workflows, SQLite
  schema/migrations/`user_version`, dataset/export contracts, or unrelated
  docs.
- Do not publish/upload to PyPI or TestPyPI, dispatch/rerun publishing
  workflows, start a PyPI publishing stage, or create/delete/overwrite/push
  tags or releases.
- Do not create `.github/workflows/pypi-publish.yml`; record its exact future
  contract and recommend a separate setup stage.
- Do not read credentials, tokens, secrets, `.pypirc`, shell history, private
  artifacts, Telegram sessions, or real exports/logs/media/screenshots/DBs.
- Do not run Telegram live commands, initialize a Telegram client, build
  packages, install packages, or leave temporary/package artifacts.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify every required file exists. Require all six prerequisite reports to
   state `PASSED` and confirm their exact evidence: local/remote
   `v0.1.0-rc2`, verified RC2 artifacts and `twine check`, isolated RC2 install
   and help smoke, TestPyPI Trusted Publisher registration, successful
   Trusted Publishing workflow, and public TestPyPI install smoke. Stop before
   further preparation if any evidence is invalid or ambiguous.
2. Record repository baseline with:
   `git status --short`, `git diff --check`,
   `git tag --list "v0.1.0-rc2"`, and
   `git ls-remote --tags origin "refs/tags/v0.1.0-rc2"`.
   Require the local tag and, unless network/auth blocks verification, the
   remote tag. Do not modify or discard existing worktree changes; require
   that only allowed stage-owned changes remain at completion.
3. Inspect `pyproject.toml` with `tomllib` and record project name, version,
   `requires-python`, scripts, license metadata, classifiers, and runtime
   dependencies. Require name `tg-msg-manager`, version `0.1.0`, console script
   `tg-msg-manager = tg_msg_manager.cli:main`, license-file metadata, MIT
   classifier, and dependencies consistent with prerequisite evidence.
4. Query concise public JSON evidence with `urllib.request` for
   `https://test.pypi.org/pypi/tg-msg-manager/0.1.0/json`,
   `https://pypi.org/pypi/tg-msg-manager/json`, and
   `https://pypi.org/pypi/tg-msg-manager/0.1.0/json`.
   Require TestPyPI name/version plus wheel and sdist. Classify main PyPI
   project and version `404 NOT_FOUND` as available at check time. If the
   project exists with unknown ownership or version `0.1.0` exists, decide
   `BLOCKED_BEFORE_PYPI`.
5. Inspect the TestPyPI workflow and record the deferred PyPI Trusted
   Publishing contract: project `tg-msg-manager`, owner `JohnyNoxwell`,
   repository `tg-msg-manager`, workflow `pypi-publish.yml`, environment
   `pypi`; manual `workflow_dispatch` only with required string tag input;
   exact tag checkout and peeled-target verification; build once; `twine
   check`; environment `pypi`; `id-token: write`;
   `pypa/gh-action-pypi-publish@release/v1`; no TestPyPI URL, passwords,
   secrets, `.pypirc`, or automatic triggers. Recommend
   `STAGE_5W_1_PYPI_TRUSTED_PUBLISHING_SETUP`.
6. Use project policy and verified evidence to choose exactly one final
   decision: `PYPI_CAN_PUBLISH_FROM_v0.1.0-rc2_TAG`,
   `STABLE_TAG_REQUIRED_BEFORE_PYPI`, or `BLOCKED_BEFORE_PYPI`. Use the
   conservative `STABLE_TAG_REQUIRED_BEFORE_PYPI` unless policy explicitly
   permits stable package publication from the RC tag; then recommend
   `STAGE_5W_0_STABLE_TAG_V0_1_0_PLAN` before PyPI workflow setup/publish.
7. Run final repository checks, write the Russian factual report, apply
   stage-completion-auditor, and complete lifecycle cleanup only when status is
   `PASSED`. Do not start any recommended next stage.

## 5. REQUIRED DOCS

Create only
`docs/stages/reports/STAGE_5W_PYPI_PUBLISH_PREPARATION_REPORT.md`. Update
`docs/stages/README.md` only for lifecycle state. On `PASSED`, move this task
to `docs/stages/completed/stage_5w_pypi_publish_preparation.md`; on `FAILED`
or `PARTIAL`, leave it active.

## 6. TESTS / VERIFICATION

Run the exact prerequisite, git, metadata, public JSON, workflow-contract, and
final checks specified above. Use this exact metadata inspection command:

```bash
python3 - <<'PY'
import pathlib
import tomllib

project = tomllib.loads(pathlib.Path("pyproject.toml").read_text())["project"]
for key in ("name", "version", "requires-python", "scripts", "license",
            "classifiers", "dependencies"):
    print(f"{key}:", project.get(key))
PY
```

Final repository checks:

```bash
git status --short
git diff --check
find . -maxdepth 2 \( -name "dist" -o -name "build" -o -name "*.egg-info" -o -name ".venv*" \) -print
```

Classify `PARTIAL` only when external network/auth/tooling blocks TestPyPI,
PyPI, remote-tag, or external metadata verification while no forbidden action
occurred. Classify `FAILED` for invalid prerequisites/metadata, blocking PyPI
state, forbidden action, or changes outside allowed scope. Do not claim a
check passed unless it was run. Record skipped commands and exact reasons.

## 7. REPORT

Write a compact Russian report containing: status; goal; each prerequisite
report path/status/evidence; current git state; local/remote RC2 tag result;
package metadata summary; TestPyPI and main PyPI project/version/files state;
name/version availability classification; selected Trusted Publishing
strategy and exact tuple; deferred PyPI workflow contract; stable-tag
decision; commands run; commands not run and reasons; files changed;
confirmation of no publish/upload/workflow dispatch, no tag/release operation,
no product/tests/CLI/SQLite/dataset/export/dependency/version/workflow change,
and no credentials/tokens/secrets access or storage; exact final decision;
next recommended stage; applied skill paths; and lifecycle notes. Do not
include full JSON, credentials, secrets, or broad command output.

## 8. COMPLETION CRITERIA

Status is `PASSED` only if all prerequisite reports and evidence are valid,
repository state is acceptable, local/remote `v0.1.0-rc2` are verified,
package metadata is valid, TestPyPI evidence remains valid, main PyPI
project/version state is checked and non-blocking, Trusted Publishing and
stable-tag decisions are explicit, no forbidden action occurred, the report
exists, stage-completion-auditor passes, and lifecycle cleanup is completed
according to `AGENTS.md`.

## 9. OUTPUT LIMITS

Follow `AGENTS.md`. Keep interim output to blockers or required questions.
Final response must use the required `AGENTS.md` structure and stay within its
character limit. Do not print full diffs, JSON, logs, credentials, secrets, or
broad summaries.
