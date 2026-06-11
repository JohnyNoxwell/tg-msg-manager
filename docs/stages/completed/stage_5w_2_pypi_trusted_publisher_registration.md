# STAGE 5W.2 — PYPI TRUSTED PUBLISHER REGISTRATION

Status: completed
Stage: 5W.2
Type: registration confirmation
Depends on:
`docs/stages/reports/STAGE_5W_1_PYPI_TRUSTED_PUBLISHING_SETUP_REPORT.md`
with `PASSED` and decision
`READY_FOR_STAGE_5W_2_PYPI_TRUSTED_PUBLISHER_REGISTRATION`; user attestation
that the exact main PyPI Trusted Publisher/Pending Publisher tuple was
registered manually

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Apply stage-reviewer before execution,
architecture-guard for boundary verification, and stage-completion-auditor
before claiming completion; record manual skill application in the report.
This is confirmation-only. Do not dispatch a workflow, publish, upload, create
a release, modify tags, or start Stage 5W.3.

## 1. PURPOSE

Record the user's manual main PyPI publisher registration and safely confirm
the repository, stable tag, workflow structure, and GitHub Environment `pypi`
without inspecting private PyPI account state.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `.github/workflows/pypi-publish.yml`
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_5W_1_PYPI_TRUSTED_PUBLISHING_SETUP_REPORT.md`

Writable paths are limited to
`docs/stages/reports/STAGE_5W_2_PYPI_TRUSTED_PUBLISHER_REGISTRATION_REPORT.md`,
`docs/stages/README.md`, and lifecycle movement of this task file. Do not
inspect unrelated existing reports, private PyPI pages, credentials, tokens,
secrets, `.pypirc`, shell history, browser storage/cookies, private artifacts,
Telegram/runtime files, or local databases.

## 3. HARD PROHIBITIONS

- Do not dispatch/run workflows or publish/upload to PyPI or TestPyPI.
- Do not create a GitHub Release; create/modify/delete/push tags; or run
  `git push`.
- Do not edit workflows, source, tests, package metadata/version/dependencies,
  CLI/runtime behavior, SQLite/schema/migrations, dataset/export contracts,
  changelog, or release notes.
- Do not create/change GitHub Environments or secrets, create PyPI tokens, use
  credentials, or inspect private PyPI account state.
- Do not run builds, installs, tests, package smoke, Telegram/live/runtime
  commands, or read private artifacts.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify worktree scope, prerequisite report, and exact local/remote annotated
   stable tag `v0.1.0`; stop on unrelated changes, diff failure, or mismatch.
2. Verify `.github/workflows/pypi-publish.yml` exists and passes all required
   and prohibited structural checks without editing it.
3. Verify GitHub Environment `pypi` read-only when available; optionally check
   public unauthenticated PyPI JSON state.
4. Record the exact user-attested publisher tuple and explicitly state that
   private PyPI UI state was not independently inspected.
5. Write the factual report, verify final scope, audit completion, and perform
   lifecycle cleanup only on `PASSED`.

## 5. REQUIRED DOCS

Create only
`docs/stages/reports/STAGE_5W_2_PYPI_TRUSTED_PUBLISHER_REGISTRATION_REPORT.md`.
Update `docs/stages/README.md` only for lifecycle state. On `PASSED`, move this
task to
`docs/stages/completed/stage_5w_2_pypi_trusted_publisher_registration.md`.

## 6. TESTS / VERIFICATION

Run:

```bash
git status --short
git diff --check
git cat-file -t v0.1.0
git rev-parse v0.1.0
git rev-parse v0.1.0^{}
git ls-remote --tags origin v0.1.0
test -f .github/workflows/pypi-publish.yml
gh api -H "Accept: application/vnd.github+json" "/repos/JohnyNoxwell/tg-msg-manager/environments/pypi"
git status --short
git diff --check
```

Require local/remote tag object
`0a1474402f6a95c96ed84f6ed627c4a62eb7e13c`, peeled target
`2f4ae2448d2e0b3217debd31f093127358215d7f`, and environment name `pypi`.
Verify required workflow controls: `workflow_dispatch`, required input `tag`,
exact tag checkout, peeled-target verification, build, twine check, artifact
handoff, separate publish job, environment `pypi`, `id-token: write`, and
`pypa/gh-action-pypi-publish@release/v1`. Require no automatic trigger,
TestPyPI endpoint, stored credential/token/secret reference, or `.pypirc`.
Public unauthenticated PyPI JSON checks are optional; HTTP 404 is expected
before publish, HTTP 200 is a blocker, and network failure is only a recorded
limitation. Do not claim tests passed because tests are prohibited.

## 7. REPORT

Write a compact Russian report containing stage/status; prerequisite,
worktree, local/remote tag, workflow, environment, and optional public PyPI
evidence; exact user attestation and tuple; statement that private PyPI UI was
not independently inspected; exact commands run and prohibited commands not
run; unchanged boundaries; files changed; skill evidence; lifecycle state;
final decision; and next stage.

On success use decision `READY_FOR_STAGE_5W_3_PYPI_WORKFLOW_PUBLISH` and
recommend `STAGE_5W_3_PYPI_WORKFLOW_PUBLISH`: controlled one-time manual
workflow dispatch for exact tag `v0.1.0`, followed by run evidence and public
PyPI artifact verification.

## 8. COMPLETION CRITERIA

`PASSED` requires exact local/remote tag evidence, passing workflow structural
verification, verified GitHub Environment `pypi`, recorded exact user
attestation, no forbidden action/access/change, report, passing completion
audit, and lifecycle cleanup completed according to `AGENTS.md`.

Use `BLOCKED` for unrelated worktree changes, tag mismatch, missing
environment, or required forbidden access/action. Use `FAILED` for workflow
structural failure or missing report. Do not start Stage 5W.3.

## 9. OUTPUT LIMITS

Follow `AGENTS.md`. Keep interim output to blockers or required questions.
Do not print full workflow/diffs, credentials, secrets, private artifacts, or
private account state.
