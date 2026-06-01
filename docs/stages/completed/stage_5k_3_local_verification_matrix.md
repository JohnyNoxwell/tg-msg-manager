# STAGE 5K.3 — LOCAL VERIFICATION MATRIX

Status: active task
Stage: 5K.3
Type: verification
Depends on: Stage 5K.0 release checklist scope and Stage 5J contract test reports if present

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.

Apply these skills before implementation:

- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md` after checks/report/cleanup

Do not execute Stage 5K.4.

This is not a bugfix stage.

## 1. PURPOSE

Define and, where safe, run the local verification matrix for the current repository state before a future release candidate decision.

If checks fail, record failures and recommend focused bugfix stages. Do not fix broad failures.

## 2. FILES TO INSPECT

Required:

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `Makefile`
- `pyproject.toml`
- `README.md`
- `docs/development/README.md`
- `docs/development/RELEASE_CHECKLIST_SCOPE.md` if present
- `docs/development/NON_CHANNEL_CONTRACT_TEST_PLAN.md`
- `docs/stages/reports/STAGE_5J_1_NON_CHANNEL_CONTRACT_TESTS_IMPLEMENTATION_REPORT.md` if present
- `docs/stages/reports/STAGE_5J_2_FIXTURE_TO_CONTRACT_VERIFICATION_REPORT.md` if present
- `docs/stages/README.md`

Inspect only as needed:

- `tests/`
- `tests/fixtures/`

Writable paths:

- `docs/stages/reports/STAGE_5K_3_LOCAL_VERIFICATION_MATRIX_REPORT.md`
- `docs/stages/README.md`
- `docs/stages/completed/stage_5k_3_local_verification_matrix.md`
- `docs/development/LOCAL_VERIFICATION_MATRIX.md` optional
- `docs/development/README.md` link-only if matrix doc is created

## 3. HARD PROHIBITIONS

- Do not publish a release, create tags, bump version, change package metadata, build/upload release artifacts, or claim a release occurred.
- Do not change runtime behavior, CLI behavior, tests, fixtures, Makefile, pyproject, SQLite/storage/services, or output formats.
- Do not fix test failures broadly.
- Do not require private artifacts, credentials, sessions, real exports, or network access.
- Do not claim live smoke checks passed unless actually run under explicit scope.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Inspect Makefile, docs, and available tests before editing.
2. Define required, optional, and manual/live verification commands.
3. Create `docs/development/LOCAL_VERIFICATION_MATRIX.md` only if a durable matrix doc is useful; otherwise keep report-only.
4. Run safe required local checks where the environment permits.
5. Record skipped commands and failures exactly; recommend focused follow-up stages without fixing unrelated code.
6. Create the Stage 5K.3 report in Russian.
7. Complete lifecycle cleanup according to `AGENTS.md`.

## 5. REQUIRED DOCS

Optional matrix doc must distinguish:

- required offline checks;
- optional local checks;
- manual/live checks requiring credentials or private data;
- checks that are never required for offline release checklist.

## 6. TESTS / VERIFICATION

Always run:

```bash
git diff --check
```

Run where environment permits:

```bash
make lint
make format-check
make test
make verify
python3 -m unittest discover tests -p '*non_channel*contract*.py'
```

Optional:

```bash
make pre-commit
python3 -m unittest tests.e2e.test_fixture_e2e -q
```

Record exact reason for every skipped or failed command.

## 7. REPORT

Create `docs/stages/reports/STAGE_5K_3_LOCAL_VERIFICATION_MATRIX_REPORT.md` in Russian.

Include status/outcome token, files inspected, matrix created or report-only, commands run, exact command results, skipped commands and exact reasons, failures/blockers, recommended follow-up bugfix stages if needed, no runtime/CLI/SQLite/output behavior changes confirmation, private artifact boundary confirmation, release/tag/version unchanged confirmation, `architecture-guard: applied from .skills/architecture-guard/SKILL.md`, and lifecycle notes.

Acceptable outcome tokens:

- `LOCAL_VERIFICATION_MATRIX_COMPLETE_ALL_REQUIRED_CHECKS_PASSED`
- `LOCAL_VERIFICATION_MATRIX_COMPLETE_WITH_SKIPPED_COMMANDS`
- `LOCAL_VERIFICATION_MATRIX_COMPLETE_FAILURES_RECORDED`
- `LOCAL_VERIFICATION_MATRIX_DOC_CREATED`
- `BLOCKED_ENVIRONMENT_NOT_READY`

## 8. COMPLETION CRITERIA

- Verification matrix is defined in report or docs.
- Required safe checks are run or exact inability is recorded.
- Failures are recorded without broad fixes.
- Required report exists.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md` final format.

Do not paste full diffs, large file excerpts, or broad summaries.
