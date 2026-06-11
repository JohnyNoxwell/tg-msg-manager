# STAGE 5W.0.3 — STABLE TAG ISOLATED INSTALL SMOKE

Status: completed
Stage: 5W.0.3
Type: release verification
Depends on:
`docs/stages/reports/STAGE_5W_0_2_STABLE_TAG_PACKAGE_ARTIFACT_VERIFICATION_REPORT.md`
with `PASSED` and final decision
`READY_FOR_STAGE_5W_0_3_STABLE_TAG_ISOLATED_INSTALL_SMOKE`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Apply stage-reviewer, architecture-guard, and
stage-completion-auditor from `.skills/`; record exact paths and verdicts in
the report. Before execution, write a plan of at most five bullets. Build from
exact annotated stable tag `v0.1.0`, install its wheel into a separate fresh
venv, and run only the scoped help commands. Do not publish or start Stage
5W.1.

## 1. PURPOSE

Verify that a wheel built from exact `v0.1.0` source installs in a fresh
isolated virtualenv, exposes correct installed metadata and console entry
point, and passes help-only CLI smoke without Telegram/runtime-data access.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_5W_0_2_STABLE_TAG_PACKAGE_ARTIFACT_VERIFICATION_REPORT.md`

Writable repository paths are limited to
`docs/stages/reports/STAGE_5W_0_3_STABLE_TAG_ISOLATED_INSTALL_SMOKE_REPORT.md`,
`docs/stages/README.md` only for lifecycle state, and lifecycle movement of
this stage file. Temporary source, build/install venvs, and artifacts are
allowed only under a fresh `/tmp/tg-msg-manager-5w03-*` workspace and must be
removed before completion. Do not inspect source/tests from the working tree,
existing reports unrelated to this stage, private artifacts, credentials,
Telegram sessions, exports, logs, media, screenshots, databases, `.pypirc`,
or shell history.

## 3. HARD PROHIBITIONS

- Do not edit production code, tests, `pyproject.toml`, package metadata,
  version, dependencies, workflows, CLI behavior, SQLite/schema/migrations,
  dataset/export contracts, changelog, release notes, or unrelated docs.
- Do not run full tests, integration/live Telegram commands, or commands that
  require config, API credentials, sessions, DBs, exports, logs, media, or
  runtime artifacts.
- Do not publish/upload to TestPyPI/PyPI, dispatch workflows, create a GitHub
  Release, create/delete/modify/push tags, or run `git push`.
- Do not build from `HEAD`, `main`, or the repository working tree. Build only
  from source exported by `git archive` from exact `v0.1.0`.
- Do not read credentials, tokens, secrets, `.pypirc`, shell history, private
  artifacts, Telegram sessions, or real exports/logs/media/screenshots/DBs.
- Do not leave temporary/build/install artifacts in the repository or `/tmp`.

Remote-tag verification and package-index access needed to install build
tooling and wheel dependencies are allowed. Telegram/runtime network or API
access is forbidden.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify prerequisite report, allowed worktree state, `git diff --check`,
   exact local/remote stable tag object and peeled target, shared RC2 peeled
   target, and distinct stable/RC2 tag objects. Stop before build on mismatch.
2. Create a fresh `/tmp/tg-msg-manager-5w03-*` workspace; export exact
   `v0.1.0` with `git archive`; confirm no `.git`; create a build venv and
   build only the expected wheel.
3. Create a separate fresh install venv; install the local wheel; verify
   freeze/show output, installed metadata/license/entry point, dependency
   versions, imports, and only the four scoped help commands.
4. Write a Russian report draft; remove the temporary workspace; verify
   cleanup and final repository state.
5. Apply stage-completion-auditor, finalize the report, and complete lifecycle
   cleanup only on `PASSED`. Do not start Stage 5W.1.

## 5. REQUIRED DOCS

Create only
`docs/stages/reports/STAGE_5W_0_3_STABLE_TAG_ISOLATED_INSTALL_SMOKE_REPORT.md`.
Update `docs/stages/README.md` only for lifecycle state. On `PASSED`, move this
task to
`docs/stages/completed/stage_5w_0_3_stable_tag_isolated_install_smoke.md`; on
`FAILED` or `BLOCKED`, leave it active. Do not change changelog or release
notes.

## 6. TESTS / VERIFICATION

Run preflight before export/build:

```bash
git status --short
git diff --check
git cat-file -t v0.1.0
git rev-parse v0.1.0
git rev-parse v0.1.0^{}
git ls-remote --tags origin refs/tags/v0.1.0 'refs/tags/v0.1.0^{}'
git rev-parse v0.1.0-rc2
git rev-parse v0.1.0-rc2^{}
```

Require stable type `tag`; stable object
`0a1474402f6a95c96ed84f6ed627c4a62eb7e13c`; stable/RC2 peeled target
`2f4ae2448d2e0b3217debd31f093127358215d7f`; matching local/remote stable
evidence; and stable tag object different from RC2 object
`962f3e413cd87d443ab5775e59e9539e84dfe57f`.

Use a fresh workspace matching `/tmp/tg-msg-manager-5w03-*`:

```bash
git archive --format=tar --prefix=tg-msg-manager-v0.1.0/ v0.1.0 | tar -x -C "$WORKDIR"
test ! -d "$WORKDIR/tg-msg-manager-v0.1.0/.git"
cd "$WORKDIR/tg-msg-manager-v0.1.0"
python3 -m venv .venv-build
.venv-build/bin/python -m pip install --upgrade pip
.venv-build/bin/python -m pip install build
.venv-build/bin/python -m build --wheel
test -f dist/tg_msg_manager-0.1.0-py3-none-any.whl
python3 -m venv .venv-install
.venv-install/bin/python -m pip install --upgrade pip
.venv-install/bin/python -m pip install dist/tg_msg_manager-0.1.0-py3-none-any.whl
.venv-install/bin/python -m pip freeze
.venv-install/bin/python -m pip show tg-msg-manager
```

Require sorted freeze evidence including exactly
`tg-msg-manager==0.1.0`. Record Python, pip, build, package, and installed
dependency versions. Do not require new artifact checksums to match Stage
5W.0.2 because build timestamps/metadata may differ.

Run a structured `importlib.metadata` verifier that fails non-zero unless:

- name/version/Requires-Python are `tg-msg-manager`/`0.1.0`/`>=3.9`;
- MIT classifier and `License-File: LICENSE` are present;
- installed files include `LICENSE`;
- requirements include `telethon>=1.36.0`, `pydantic>=2.0.0`, and
  `pydantic-settings>=2.0.0`;
- console script `tg-msg-manager = tg_msg_manager.cli:main` is present.

Run only:

```bash
.venv-install/bin/tg-msg-manager --help
.venv-install/bin/tg-msg-manager target --help
.venv-install/bin/tg-msg-manager target names --help
.venv-install/bin/python -m tg_msg_manager.cli --help
```

All must exit zero and print help without Telegram client initialization or
runtime-data access. A minimal import of `tg_msg_manager` and
`tg_msg_manager.cli` is allowed; do not require `tg_msg_manager.__version__`.
Do not run tests or `twine check`.

After report draft, remove the entire temporary workspace and verify it no
longer exists. Return to the repository and run:

```bash
git status --short
git diff --check
```

Confirm final changes are limited to required stage/lifecycle/report docs and
no build artifacts remain.

## 7. REPORT

Write a compact Russian report containing: stage/status; prerequisite report;
working-tree preflight; local/remote stable tag evidence; stable/RC2
comparison; exact `git archive` source method and temporary path; confirmation
that build did not use working-tree/HEAD/main source; separate build/install
venv details; wheel build and local install results; wheel filename; sorted
dependency freeze and `pip show` summary; installed metadata/license/entry
point verification; each help command and exit status; optional import result;
confirmation of no Telegram client/runtime network/API/session/runtime-data
access; permitted package-index access; temp cleanup; final repository checks;
commands run and explicitly skipped; confirmations of no tests, publish/upload,
workflow dispatch, GitHub Release, tag operation, credential/secret/private-
artifact access, or out-of-scope changes; files changed; skill evidence;
lifecycle notes; exact final decision; and next recommended stage.

On success use final decision
`READY_FOR_STAGE_5W_1_PYPI_TRUSTED_PUBLISHING_SETUP` and recommend only
`STAGE_5W_1_PYPI_TRUSTED_PUBLISHING_SETUP`: create/verify the manual PyPI
Trusted Publishing workflow and GitHub Environment `pypi` without publishing.

## 8. COMPLETION CRITERIA

Status is `PASSED` only when tag/preflight evidence matches; exact `v0.1.0`
source is exported through `git archive`; isolated build creates the expected
wheel; a separate fresh venv installs that local wheel; freeze/show,
structured installed metadata/license/entry point, imports if run, and all
four help-only commands pass; no forbidden action or access occurred; temp
cleanup and final repository checks pass; the report exists;
stage-completion-auditor passes; and lifecycle cleanup is completed according
to `AGENTS.md`.

Use `BLOCKED` and leave the task active when prerequisite/tag/worktree/network
evidence fails, exact stable source cannot be used, or credential/private
artifact access would be required. Use `FAILED` and leave the task active when
build, wheel creation, fresh install, freeze/show, installed metadata/license/
entry point, help smoke, or cleanup verification fails. In either case,
create the report with exact evidence and skipped actions; do not publish,
change tags, or continue to Stage 5W.1.

## 9. OUTPUT LIMITS

Follow `AGENTS.md`. Keep interim output to blockers or required questions.
Final response must use the required `AGENTS.md` structure and stay within its
character limit. Do not print full build/install/help logs, dependency dumps,
metadata dumps, diffs, credentials, secrets, private artifacts, or broad
summaries.
