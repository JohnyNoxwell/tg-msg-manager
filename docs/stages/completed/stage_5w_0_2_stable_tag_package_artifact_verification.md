# STAGE 5W.0.2 — STABLE TAG PACKAGE ARTIFACT VERIFICATION

Status: active task
Stage: 5W.0.2
Type: packaging verification
Depends on:
`docs/stages/reports/STAGE_5W_0_1_CREATE_STABLE_TAG_V0_1_0_REPORT.md` with
`PASSED` and final decision
`READY_FOR_STAGE_5W_0_2_STABLE_TAG_PACKAGE_ARTIFACT_VERIFICATION`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Apply stage-reviewer, architecture-guard, and
stage-completion-auditor from `.skills/`; record exact paths and verdicts in
the report. Before execution, write a plan of at most five bullets. Verify
artifacts built only from exact annotated stable tag `v0.1.0`; do not install
the package, publish, change tags, or start Stage 5W.0.3.

## 1. PURPOSE

Export exact `v0.1.0` source through `git archive`, build wheel and sdist in
an isolated temporary workspace, verify package structure/metadata/license/
entry point with structured readers and `twine check`, and record SHA-256
checksums without changing or publishing the package.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_5W_0_1_CREATE_STABLE_TAG_V0_1_0_REPORT.md`

Writable repository paths are limited to
`docs/stages/reports/STAGE_5W_0_2_STABLE_TAG_PACKAGE_ARTIFACT_VERIFICATION_REPORT.md`,
`docs/stages/README.md` only for lifecycle state, and lifecycle movement of
this stage file. Temporary source, tooling venv, build output, and inspection
files are allowed only under a fresh `/tmp/tg-msg-manager-5w02-*` workspace
and must be removed before completion. Do not inspect source or tests from the
working tree, existing reports unrelated to this stage, private artifacts,
credentials, Telegram sessions, exports, logs, media, screenshots, databases,
`.pypirc`, or shell history.

## 3. HARD PROHIBITIONS

- Do not edit production code, tests, `pyproject.toml`, package metadata,
  version, dependencies, workflows, CLI behavior, SQLite/schema/migrations,
  dataset/export contracts, changelog, release notes, or unrelated docs.
- Do not install the built package or wheel, run CLI/install smoke, run full
  tests, publish/upload to TestPyPI/PyPI, dispatch workflows, create a GitHub
  Release, or start the next stage.
- Do not create/delete/modify/push tags; do not run `git push`.
- Do not build from `HEAD`, `main`, or the repository working tree. Build only
  from source exported by `git archive` from exact `v0.1.0`.
- Do not read credentials, tokens, secrets, `.pypirc`, shell history, private
  artifacts, Telegram sessions, or real exports/logs/media/screenshots/DBs.
- Do not leave temporary/build artifacts in the repository or `/tmp`.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify prerequisite report, allowed worktree state, `git diff --check`,
   exact local/remote stable tag object and peeled target, shared RC2 peeled
   target, and distinct stable/RC2 tag objects. Stop before build on mismatch.
2. Create a fresh `/tmp/tg-msg-manager-5w02-*` workspace; export exact
   `v0.1.0` with `git archive`; confirm exported source has no `.git`; create
   an isolated tooling venv and install only `build` and `twine`.
3. Build wheel/sdist, require exactly the expected two artifacts, run
   `python -m twine check`, and use structured Python `zipfile`/`tarfile`/
   `email.parser` inspection to verify contents, metadata, license payload,
   console entry point, and runtime/dev dependency metadata.
4. Record SHA-256 checksums and non-blocking build warnings; write a Russian
   report draft; remove the temporary workspace; verify cleanup and final
   repository state.
5. Apply stage-completion-auditor, finalize the report, and complete lifecycle
   cleanup only on `PASSED`. Do not start Stage 5W.0.3.

## 5. REQUIRED DOCS

Create only
`docs/stages/reports/STAGE_5W_0_2_STABLE_TAG_PACKAGE_ARTIFACT_VERIFICATION_REPORT.md`.
Update `docs/stages/README.md` only for lifecycle state. On `PASSED`, move this
task to
`docs/stages/completed/stage_5w_0_2_stable_tag_package_artifact_verification.md`;
on `FAILED` or `BLOCKED`, leave it active. Do not change changelog or release
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

Use a fresh workspace matching `/tmp/tg-msg-manager-5w02-*`. Export and build:

```bash
git archive --format=tar --prefix=tg-msg-manager-v0.1.0/ v0.1.0 | tar -x -C "$WORKDIR"
test ! -d "$WORKDIR/tg-msg-manager-v0.1.0/.git"
python3 -m venv "$WORKDIR/tools"
"$WORKDIR/tools/bin/python" -m pip install --upgrade pip
"$WORKDIR/tools/bin/python" -m pip install build twine
cd "$WORKDIR/tg-msg-manager-v0.1.0"
"$WORKDIR/tools/bin/python" -m build
find dist -maxdepth 1 -type f -print | sort
"$WORKDIR/tools/bin/python" -m twine check dist/*
```

Require exactly:

```text
dist/tg_msg_manager-0.1.0-py3-none-any.whl
dist/tg_msg_manager-0.1.0.tar.gz
```

Use one structured Python verifier that fails non-zero on mismatch. It must:

- open wheel with `zipfile`, sdist with `tarfile`, and metadata with
  `email.parser`;
- require package files, wheel `METADATA`/`WHEEL`/`entry_points.txt` and
  dist-info license payload; require sdist `pyproject.toml`, `README.md`,
  `LICENSE`, package files, and `PKG-INFO`;
- require `Name: tg-msg-manager`, `Version: 0.1.0`, `Requires-Python: >=3.9`,
  `License-File: LICENSE`, MIT classifier, runtime requirements
  `telethon>=1.36.0`, `pydantic>=2.0.0`, `pydantic-settings>=2.0.0`, and
  `Provides-Extra: dev` in wheel metadata and sdist `PKG-INFO`;
- require entry point `tg-msg-manager = tg_msg_manager.cli:main`;
- require `MIT License` and `Copyright (c) 2026 R.P.` in wheel and sdist
  license payloads.

Compute and record SHA-256 for exactly both artifacts. Build timestamp or
metadata-related checksum differences from RC2 are not blockers. License
table/classifier deprecation warnings are non-blocking only when all required
checks pass; record them.

After report draft, remove the entire temporary workspace and verify it no
longer exists. Return to the repository and run:

```bash
git status --short
git diff --check
```

Do not claim a check passed unless it was run. Confirm final changes are
limited to required stage/lifecycle/report docs and no build artifacts remain.

## 7. REPORT

Write a compact Russian report containing: stage/status; prerequisite report;
working-tree preflight; local/remote stable tag evidence; stable/RC2
comparison; exact `git archive` source method and temporary path; confirmation
that build did not use working-tree/HEAD/main source; build environment/tool
details and command result; exact artifact filenames; twine results;
structured wheel/sdist contents and metadata results; license/entry-point
results; SHA-256 checksums; non-blocking warnings; temp cleanup evidence;
commands run and explicitly skipped; confirmations of no package install
smoke, tests, publish/upload, workflow dispatch, GitHub Release, tag operation,
credential/secret/private-artifact access, or out-of-scope changes; files
changed; skill evidence; lifecycle notes; exact final decision; and next
recommended stage.

On success use final decision
`READY_FOR_STAGE_5W_0_3_STABLE_TAG_ISOLATED_INSTALL_SMOKE` and recommend only
`STAGE_5W_0_3_STABLE_TAG_ISOLATED_INSTALL_SMOKE`: install a wheel built from
exact `v0.1.0` source in a fresh venv and run help-only CLI smoke.

## 8. COMPLETION CRITERIA

Status is `PASSED` only when tag/preflight evidence matches; exact `v0.1.0`
source is exported through `git archive`; isolated build creates exactly the
expected wheel/sdist; twine and structured contents/metadata/license/entry
point checks pass; checksums are recorded; temp cleanup passes; no forbidden
action or out-of-scope change occurred; the report exists;
stage-completion-auditor passes; and lifecycle cleanup is completed according
to `AGENTS.md`.

Use `BLOCKED` and leave the task active when prerequisite/tag/worktree/network
evidence fails, exact stable source cannot be used, or credential/private
artifact access would be required. Use `FAILED` and leave the task active when
build, expected artifact set, twine, structured inspection, metadata, license,
entry point, or cleanup verification fails. In either case, create the report
with exact evidence and skipped actions; do not publish/install/change tags.

## 9. OUTPUT LIMITS

Follow `AGENTS.md`. Keep interim output to blockers or required questions.
Final response must use the required `AGENTS.md` structure and stay within its
character limit. Do not print full build logs, archive listings, metadata
dumps, diffs, credentials, secrets, private artifacts, or broad summaries.
