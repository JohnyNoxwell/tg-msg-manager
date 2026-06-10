# STAGE 5R.1 — ISOLATED WHEEL INSTALL / CLI SMOKE

Status: active task
Stage: 5R.1
Type: packaging verification
Depends on: `docs/stages/reports/STAGE_5R_0_PACKAGE_BUILD_DRY_RUN_REPORT.md` with `PASSED`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Apply `.skills/stage-reviewer/SKILL.md`,
`.skills/architecture-guard/SKILL.md`, and
`.skills/stage-completion-auditor/SKILL.md` after report/cleanup.

Use a fresh temporary virtualenv and wheel. Do not use the current project env,
Telegram credentials, or start Stage 5S.

## 1. PURPOSE

Verify that the built wheel installs in isolation and exposes the documented
console script/module help surfaces without Telegram access.

## 2. FILES TO INSPECT

Required:

- `AGENTS.md`
- `pyproject.toml`
- `COMMANDS.md`
- `docs/development/CLI_CONTRACT.md`
- Stage 5R.0 report
- `docs/stages/README.md`

Writable paths:

- `docs/stages/reports/STAGE_5R_BUILD_AND_INSTALL_DRY_RUN_REPORT.md`
- `docs/stages/README.md`
- lifecycle move of this stage file

Temporary writable paths outside the repository:

- a new `/tmp/tg-msg-manager-5r1-*` directory only

## 3. HARD PROHIBITIONS

- Do not install into the project/current/user/global environment.
- Do not keep build artifacts or virtualenvs in the repo.
- Do not change production code, tests, docs, CLI contracts, SQLite schema,
  dataset/export contracts, package metadata/version/dependencies, tags, or publish state.
- Do not read private artifacts, sessions, credentials, real exports/logs/media/
  screenshots/DB files, or inject real Telegram data.
- Do not add analytics, OSINT, profiling, identity/media analysis, GUI/SaaS,
  or LLM-dependent core behavior.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify the 5R.0 report, require a clean tracked working tree, and reproduce
   its build in a fresh temporary source copy.
2. Create a separate fresh install virtualenv in the same temporary root.
3. Install the wheel and run only safe help commands.
4. Record entrypoint results and confirm no Telegram/client initialization.
5. Remove the temporary root, create the Russian report, and complete lifecycle cleanup.

## 5. REQUIRED DOCS

Report-only. Documentation mismatch is a blocker for a separate docs-fix stage;
do not edit docs here.

Rollback: remove the temporary root. Do not patch build/install failures here.
Always remove the stage-owned temporary root before reporting, including after failure.

## 6. TESTS / VERIFICATION

Required isolated commands:

```bash
tmpdir="$(mktemp -d /tmp/tg-msg-manager-5r1-XXXXXX)"
git status --short --untracked-files=no
mkdir -p "$tmpdir/source"
git archive --format=tar HEAD | tar -xf - -C "$tmpdir/source"
python3 -m venv "$tmpdir/build-venv"
"$tmpdir/build-venv/bin/python" -m pip install --upgrade pip build
"$tmpdir/build-venv/bin/python" -m build "$tmpdir/source" --outdir "$tmpdir/dist"
python3 -m venv "$tmpdir/install-venv"
"$tmpdir/install-venv/bin/python" -m pip install "$tmpdir"/dist/*.whl
"$tmpdir/install-venv/bin/tg-msg-manager" --help
"$tmpdir/install-venv/bin/tg-msg-manager" target --help
"$tmpdir/install-venv/bin/tg-msg-manager" target names --help
"$tmpdir/install-venv/bin/python" -m tg_msg_manager.cli --help
git diff --check
rm -rf "$tmpdir"
```

Use actual unique paths in the report. Record exact inability if tooling/network
is unavailable. Do not run commands that access Telegram.

## 7. REPORT

Create `docs/stages/reports/STAGE_5R_BUILD_AND_INSTALL_DRY_RUN_REPORT.md` in Russian.

Include: `PASSED`, `FAILED`, or `PARTIAL`; commands/results; failures; entrypoint
outcomes; commands not run and why; cleanup result; files changed; no Telegram access; no
behavior/CLI/SQLite/dataset/version/tag/publish change; final recommendation;
applied skill paths; lifecycle notes.

## 8. COMPLETION CRITERIA

- Fresh wheel install and all required help commands pass.
- Tracked working tree was clean before the build/install smoke.
- Temporary artifacts/environment are removed.
- Stage 5S is allowed only when status is `PASSED`.
- Required report exists and lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md`. Do not paste full help/build output.
