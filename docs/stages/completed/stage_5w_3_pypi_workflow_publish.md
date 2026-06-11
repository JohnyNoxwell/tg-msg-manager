# STAGE 5W.3 — PYPI WORKFLOW PUBLISH

Status: completed
Stage: 5W.3
Type: controlled package publication
Depends on: `docs/stages/reports/STAGE_5W_2_PYPI_TRUSTED_PUBLISHER_REGISTRATION_REPORT.md` with `PASSED` and `READY_FOR_STAGE_5W_3_PYPI_WORKFLOW_PUBLISH`; `.github/workflows/pypi-publish.yml` on default branch; exact stable tag `v0.1.0`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md`, this task, and only listed prerequisite files. Apply
`stage-reviewer`, `architecture-guard`, and `stage-completion-auditor` from
`.skills/`. Dispatch exactly once only after all preflight checks pass. Stop
without retrying publication if a workflow run was already dispatched or the
public PyPI project/version already exists.

## 1. PURPOSE

Publish exact stable tag `v0.1.0` once to main PyPI through the prepared Trusted
Publishing workflow, then verify the terminal GitHub Actions run and public
PyPI artifacts.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `.github/workflows/pypi-publish.yml`
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_5W_0_1_CREATE_STABLE_TAG_V0_1_0_REPORT.md`
- `docs/stages/reports/STAGE_5W_0_2_STABLE_TAG_PACKAGE_ARTIFACT_VERIFICATION_REPORT.md`
- `docs/stages/reports/STAGE_5W_0_3_STABLE_TAG_ISOLATED_INSTALL_SMOKE_REPORT.md`
- `docs/stages/reports/STAGE_5W_1_PYPI_TRUSTED_PUBLISHING_SETUP_REPORT.md`
- `docs/stages/reports/STAGE_5W_2_PYPI_TRUSTED_PUBLISHER_REGISTRATION_REPORT.md`

Writable repository paths are limited to this task file, its lifecycle target,
`docs/stages/reports/STAGE_5W_3_PYPI_WORKFLOW_PUBLISH_REPORT.md`, and
`docs/stages/README.md` for lifecycle state.

## 3. HARD PROHIBITIONS

- Do not edit production code, tests, workflows, package metadata/version/
  dependencies, CLI behavior, SQLite, dataset/export contracts, or tags.
- Do not publish to TestPyPI, create GitHub Releases, create/delete/push tags,
  rerun or dispatch the workflow more than once, or publish any tag except
  exact `v0.1.0`.
- Do not access credentials, tokens, secrets, private PyPI pages/artifacts,
  Telegram sessions/data, or initialize Telegram clients.
- Do not start a post-publish stage.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify prerequisites, clean tree, exact local/remote annotated tag target,
   workflow on default branch, Environment `pypi`, no prior workflow runs, and
   public PyPI project/version absence; do not dispatch yet.
2. Dispatch exactly once:
   `gh workflow run pypi-publish.yml --repo JohnyNoxwell/tg-msg-manager --ref main -f tag=v0.1.0`.
3. Identify the single new run, wait for terminal state, and inspect run/jobs;
   never rerun or redispatch after failure.
4. Verify public PyPI project/version, exact wheel/sdist names and SHA-256;
   record results without downloading private artifacts.
5. Write the Russian report and complete lifecycle cleanup.

## 5. REQUIRED DOCS

Create `docs/stages/reports/STAGE_5W_3_PYPI_WORKFLOW_PUBLISH_REPORT.md`;
update `docs/stages/README.md` only for lifecycle state; move this task to
`docs/stages/completed/` after the final report exists.

## 6. TESTS / VERIFICATION

Run exact local/remote tag checks, workflow/default-branch/Environment checks,
pre/post run listings, terminal run/job inspection, public PyPI JSON artifact
verification, `git status --short`, and `git diff --check`. Do not claim checks
passed unless actually run.

## 7. REPORT

Write a Russian report with prerequisite/pre-upload evidence, exact dispatch
command, run/job IDs and terminal results, public PyPI project/version,
artifact filenames/SHA-256, no-repeat confirmation, preserved boundaries,
applied skills, files changed, and lifecycle notes.

## 8. COMPLETION CRITERIA

Complete only if exactly one workflow dispatch succeeds, build/publish jobs
succeed, public PyPI exposes `tg-msg-manager==0.1.0` with wheel and sdist,
no forbidden changes/actions occur, the report exists, and lifecycle cleanup
is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

Follow `AGENTS.md`; do not print credentials, full workflow logs, full API
bodies, or full diffs.
