# STAGE 5R.0 — PACKAGE BUILD DRY-RUN

Status: active task
Stage: 5R.0
Type: packaging verification
Depends on: Stage 5P `PASSED`; Stage 5Q checklist `PASSED` or non-blocking `PARTIAL`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Apply `.skills/stage-reviewer/SKILL.md`,
`.skills/architecture-guard/SKILL.md`, and
`.skills/stage-completion-auditor/SKILL.md` after report/cleanup.

Build only in an isolated temporary directory. Do not install or start 5R.1.

## 1. PURPOSE

Verify that the current source tree can produce local sdist/wheel artifacts
without changing repository package/version state or publishing.

## 2. FILES TO INSPECT

Required:

- `AGENTS.md`
- `pyproject.toml`
- `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`
- Stage 5P and Stage 5Q checklist reports
- `docs/stages/README.md`

Writable paths:

- `docs/stages/reports/STAGE_5R_0_PACKAGE_BUILD_DRY_RUN_REPORT.md`
- `docs/stages/README.md`
- lifecycle move of this stage file

Temporary writable paths outside the repository:

- a new `/tmp/tg-msg-manager-5r0-*` directory only

## 3. HARD PROHIBITIONS

- Do not write/keep `dist/`, `build/`, `*.egg-info`, or virtualenvs in the repo.
- Do not change production code, tests, docs, CLI behavior, SQLite schema,
  dataset/export contracts, dependencies, package metadata, version, tags, or publish state.
- Do not read private artifacts, sessions, credentials, real exports/logs/media/
  screenshots/DB files, or inject real Telegram data.
- Do not add analytics, OSINT, profiling, identity/media analysis, GUI/SaaS,
  or LLM-dependent core behavior.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify prerequisite reports, require a clean tracked working tree, and record
   source version before build.
2. Create an isolated temporary build directory and copy only tracked source files.
3. Install/resolve build tooling only inside the isolated environment if permitted.
4. Build sdist/wheel, record artifact names/checksums, and verify no install or publish occurred.
5. Remove the temporary directory, create the Russian report, and complete lifecycle cleanup.

## 5. REQUIRED DOCS

Report-only. If tooling/network is unavailable, record the exact blocker and
recommend a separate packaging-fix stage only when the failure is project-owned.

Rollback: remove temporary build artifacts/environment. Do not patch in this stage.
Always remove the stage-owned temporary root before reporting, including after failure.

## 6. TESTS / VERIFICATION

Required isolated flow:

```bash
tmpdir="$(mktemp -d /tmp/tg-msg-manager-5r0-XXXXXX)"
git status --short --untracked-files=no
git archive --format=tar HEAD | tar -xf - -C "$tmpdir"
python3 -m venv "$tmpdir/.venv-build"
"$tmpdir/.venv-build/bin/python" -m pip install --upgrade pip build
"$tmpdir/.venv-build/bin/python" -m build "$tmpdir" --outdir "$tmpdir/dist"
git diff --check
rm -rf "$tmpdir"
```

Wheel installation and CLI smoke belong only to Stage 5R.1. Record exact
inability if network/tool installation is unavailable.

## 7. REPORT

Create `docs/stages/reports/STAGE_5R_0_PACKAGE_BUILD_DRY_RUN_REPORT.md` in Russian.

Include: `PASSED`, `FAILED`, or `PARTIAL`; exact commands/results; failures;
commands not run and why; artifact names/checksums from temp only; cleanup
result; files changed; source version unchanged; no behavior/CLI/SQLite/dataset/
tag/publish change; final recommendation; applied skill paths; lifecycle notes.

## 8. COMPLETION CRITERIA

- Package sdist/wheel build succeeds.
- Tracked working tree was clean before the build.
- Temporary artifacts/environment are removed and repo package state is unchanged.
- Stage 5R.1 is allowed only when status is `PASSED`.
- Required report exists and lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md`. Do not paste build logs or artifact contents.
