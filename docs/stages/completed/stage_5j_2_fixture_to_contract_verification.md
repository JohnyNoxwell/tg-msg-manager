# STAGE 5J.2 — FIXTURE-TO-CONTRACT VERIFICATION

Status: active task
Stage: 5J.2
Type: docs audit
Depends on: `docs/stages/reports/STAGE_5J_1_NON_CHANNEL_CONTRACT_TESTS_IMPLEMENTATION_REPORT.md`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.

Apply these skills before implementation:

- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md` after checks/report/cleanup

Do not execute Stage 5J.3.

## 1. PURPOSE

Verify the relationship:

```text
contract claim -> fixture evidence -> test coverage -> deferred/not covered
```

This stage is primarily audit/report/docs-fix work. It must not implement behavior.

## 2. FILES TO INSPECT

Required:

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/stages/reports/STAGE_5J_1_NON_CHANNEL_CONTRACT_TESTS_IMPLEMENTATION_REPORT.md`
- `docs/stages/reports/STAGE_5I_1_USER_DB_EXPORT_SYNTHETIC_FIXTURE_IMPLEMENTATION_REPORT.md`
- `docs/stages/reports/STAGE_5I_2_NON_CHANNEL_CONTRACT_TEST_PLAN_REPORT.md`
- `docs/stages/reports/STAGE_5I_3_NON_CHANNEL_EXPORT_CONTRACT_V1_DRAFT_REPORT.md`
- `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_V1.md`
- `docs/development/NON_CHANNEL_CONTRACT_TEST_PLAN.md`
- `docs/development/NON_CHANNEL_SYNTHETIC_FIXTURES_PLAN.md`
- `docs/architecture/TXT_RENDERING.md`
- `docs/architecture/PRIVATE_ARCHIVE_CONTRACT_DEFERRED_DECISION.md`
- `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`
- `docs/stages/README.md`
- `tests/fixtures/non_channel_export/`
- `tests/fixtures/db_export/`
- `tests/services/rendering/`
- `tests/services/db_export/`
- `tests/cli/`

Writable paths:

- `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_V1.md`
- `docs/development/NON_CHANNEL_CONTRACT_TEST_PLAN.md`
- `docs/development/NON_CHANNEL_SYNTHETIC_FIXTURES_PLAN.md`
- `docs/stages/reports/STAGE_5J_2_FIXTURE_TO_CONTRACT_VERIFICATION_REPORT.md`
- `docs/stages/README.md`
- `docs/stages/completed/stage_5j_2_fixture_to_contract_verification.md`

## 3. HARD PROHIBITIONS

- Do not change runtime behavior, CLI behavior, output formats, TXT rendering, JSONL schema, SQLite/storage/services, tests, fixture data, or expected outputs.
- Do not include `export-pm` in the non-channel contract.
- Do not read private artifacts or real exports.
- Do not claim unsupported coverage.
- Do not add or modify tests unless this stage is explicitly revised before execution.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Inspect contract claims, fixture files, and Stage 5J.1 tests before editing.
2. Map each meaningful contract section to fixture support, test support, and deferred/not-covered status.
3. Identify claims that are too strong and downgrade them only within allowed docs paths.
4. Verify JSONL key, TXT marker, `.writer_state`, `.export_state`, privacy, and `export-pm` boundaries.
5. Record missing coverage as future work; do not implement it.
6. Create the Stage 5J.2 report in Russian.
7. Complete lifecycle cleanup according to `AGENTS.md`.

## 5. REQUIRED DOCS

Update docs only when claims are inaccurate, overstated, stale, or missing deferred status.

Do not rewrite historical reports.

## 6. TESTS / VERIFICATION

Required:

```bash
git diff --check
```

Run the Stage 5J.1 focused contract tests again if they exist and can run without credentials:

```bash
python3 -m unittest discover tests -p '*non_channel*contract*.py'
```

If not run, record the exact reason. Do not claim tests passed unless actually run.

## 7. REPORT

Create `docs/stages/reports/STAGE_5J_2_FIXTURE_TO_CONTRACT_VERIFICATION_REPORT.md` in Russian.

Include:

- status and outcome token;
- files inspected;
- claim-to-fixture/test coverage matrix;
- claims downgraded or deferred;
- missing coverage;
- checks run;
- confirmation that runtime/tests/fixtures/output behavior did not change;
- private artifact boundary confirmation;
- `export-pm` exclusion confirmation;
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`;
- lifecycle notes.

Acceptable outcome tokens:

- `FIXTURE_TO_CONTRACT_VERIFICATION_COMPLETE`
- `FIXTURE_TO_CONTRACT_VERIFICATION_COMPLETE_AFTER_DOC_FIXES`
- `FIXTURE_TO_CONTRACT_VERIFICATION_FOUND_UNSUPPORTED_CLAIMS`
- `BLOCKED_TESTS_OR_FIXTURES_MISSING`

## 8. COMPLETION CRITERIA

- Claim-to-fixture/test/deferred mapping is complete in the report.
- Unsupported claims are downgraded or documented as blockers.
- Required checks are run or exact inability is recorded.
- No runtime/CLI/SQLite/output/test/fixture behavior changed.
- Required report exists.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md` final format.

Do not paste full diffs, large file excerpts, or broad summaries.
