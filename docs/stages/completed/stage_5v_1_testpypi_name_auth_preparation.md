# STAGE 5V.1 — TESTPYPI NAME AND AUTH PREPARATION

Status: active task
Stage: 5V.1
Type: publish preparation decision
Depends on: `docs/stages/reports/STAGE_5U_8_RC2_ISOLATED_INSTALL_SMOKE_REPORT.md`
with `PASSED`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Apply stage-reviewer, architecture-guard, and
stage-completion-auditor from `.skills/`. This is a network metadata/auth-plan
stage only; do not read a token, build artifacts, upload, or start Stage 5V.2.

## 1. PURPOSE

Classify TestPyPI/PyPI name and version state and record the safe manual-token
contract for one later TestPyPI upload.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `pyproject.toml`
- `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_5U_8_RC2_ISOLATED_INSTALL_SMOKE_REPORT.md`

Writable paths: `docs/stages/reports/STAGE_5V_1_TESTPYPI_NAME_AUTH_PREPARATION_REPORT.md`,
`docs/stages/README.md`, and lifecycle move of this stage file.

## 3. HARD PROHIBITIONS

- Do not edit source/tests/package metadata/version/dependencies or unrelated
  docs; do not build/install/upload/publish or change tags/releases.
- Do not read/print/store/test credentials, environment token values, shell
  history, or `.pypirc`; do not create a publishing workflow.
- Do not treat public package-index metadata as proof of account ownership.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify prerequisite, clean state, and package name/version.
2. Query public JSON metadata for `tg-msg-manager` on TestPyPI and PyPI;
   separately classify project existence and version `0.1.0` existence.
3. Record immediate auth strategy: manual TestPyPI token via
   `TEST_PYPI_API_TOKEN`; defer Trusted Publishing to a separate future stage.
4. Write the Russian decision report and complete lifecycle cleanup.

## 5. REQUIRED DOCS

Create only
`docs/stages/reports/STAGE_5V_1_TESTPYPI_NAME_AUTH_PREPARATION_REPORT.md`;
update the stage index only for lifecycle state.

## 6. TESTS / VERIFICATION

Run safe public HTTPS JSON checks, `git status --short`, and `git diff --check`.
A `404` is only a point-in-time availability indication. If project exists,
ownership requires manual account confirmation. If version `0.1.0` exists,
block upload because package-index files are immutable.

## 7. REPORT

Write a Russian report with index/project/version classifications, ownership
limits, external network blockers, auth strategy, requirement for
`TEST_PYPI_API_TOKEN` in Stage 5V.2 without reading it, no-publish
confirmation, applied skills, lifecycle notes, and exact decision:

- `READY_FOR_STAGE_5V_2_TESTPYPI_PUBLISH`, or
- `BLOCKED_BY_TESTPYPI_PROJECT_OR_VERSION_STATE`.

## 8. COMPLETION CRITERIA

Complete only if index state is classified, auth contract is recorded, no
credential/forbidden action occurred, and report exists. Lifecycle cleanup is completed according to `AGENTS.md`.
Network failure produces `PARTIAL` and does not authorize Stage 5V.2.

## 9. OUTPUT LIMITS

Follow `AGENTS.md`; never print token/environment values or full HTTP bodies.
