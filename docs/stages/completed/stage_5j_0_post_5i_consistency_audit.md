# STAGE 5J.0 — POST-5I CONSISTENCY AUDIT

Status: active task
Stage: 5J.0
Type: docs audit
Depends on: Stage 5I reports, non-channel fixture docs, non-channel contract/test-plan docs

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.

Apply these skills before implementation:

- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md` after checks/report/cleanup

Do not execute Stage 5J.1 or later.

## 1. PURPOSE

Audit consistency across Stage 5I fixtures, reports, contract docs, test plan, architecture indexes, stage index, and user-facing docs.

Fix only small documentation/index/link inconsistencies.

Do not implement tests or change runtime behavior.

## 2. FILES TO INSPECT

Required:

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/stages/reports/STAGE_5I_0_NON_CHANNEL_SYNTHETIC_FIXTURES_STAGE_FILES_REPORT.md`
- `docs/stages/reports/STAGE_5I_1_USER_DB_EXPORT_SYNTHETIC_FIXTURE_IMPLEMENTATION_REPORT.md`
- `docs/stages/reports/STAGE_5I_2_NON_CHANNEL_CONTRACT_TEST_PLAN_REPORT.md`
- `docs/stages/reports/STAGE_5I_3_NON_CHANNEL_EXPORT_CONTRACT_V1_DRAFT_REPORT.md`
- `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_V1.md`
- `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_DESIGN.md`
- `docs/development/NON_CHANNEL_SYNTHETIC_FIXTURES_PLAN.md`
- `docs/development/NON_CHANNEL_CONTRACT_TEST_PLAN.md`
- `docs/architecture/PRIVATE_ARCHIVE_CONTRACT_DEFERRED_DECISION.md`
- `docs/architecture/TXT_RENDERING.md`
- `docs/architecture/DATASET_CONTRACT_V1.md`
- `docs/architecture/DATASET_FORMAT.md`
- `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`
- `docs/architecture/README.md`
- `docs/development/README.md`
- `docs/stages/README.md`
- `README.md`
- `COMMANDS.md`
- `tests/fixtures/non_channel_export/`
- `tests/fixtures/db_export/`

Inspect only if command/format parity requires it:

- `tg_msg_manager/cli_parser.py`
- `tg_msg_manager/services/db_export/`
- `tg_msg_manager/services/rendering/`

Writable paths:

- `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_V1.md`
- `docs/architecture/README.md`
- `docs/development/NON_CHANNEL_CONTRACT_TEST_PLAN.md`
- `docs/development/NON_CHANNEL_SYNTHETIC_FIXTURES_PLAN.md`
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_5J_0_POST_5I_CONSISTENCY_AUDIT_REPORT.md`
- `docs/stages/completed/stage_5j_0_post_5i_consistency_audit.md`
- `tests/fixtures/non_channel_export/README.md`
- `tests/fixtures/db_export/README.md`

## 3. HARD PROHIBITIONS

- Do not implement tests.
- Do not change runtime, CLI, output formats, TXT rendering, JSONL schema, SQLite/storage/services, or fixture data.
- Do not change fixture expected output files.
- Do not include `export-pm` / private archive in the non-channel user/group + `db-export` contract.
- Do not read private artifacts, real exports, real sessions, real credentials, real logs, real DB files, or real media.
- Do not create release artifacts, tags, package uploads, or version changes.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Inspect the required reports/docs/fixtures and record consistency findings before editing.
2. Verify actual fixture paths, fixture README privacy wording, and `export-pm` exclusion against the contract and test plan.
3. Verify `.export_state` remains deferred/legacy fallback and `.writer_state` matches fixture coverage.
4. Verify docs indexes and user-facing command references do not contain stale post-5I claims.
5. Apply only small docs/index/README corrections needed to remove inconsistency.
6. Create the Stage 5J.0 report in Russian.
7. Complete lifecycle cleanup according to `AGENTS.md`.

## 5. REQUIRED DOCS

Update docs only when the audit finds an inconsistency in an allowed writable path.

Do not rewrite historical reports.

## 6. TESTS / VERIFICATION

Required:

```bash
git diff --check
```

If command examples change, verify them against:

- `tg_msg_manager/cli_parser.py`
- `README.md`
- `COMMANDS.md`

Runtime tests are not required for audit-only scope. Do not claim tests passed unless actually run.

## 7. REPORT

Create `docs/stages/reports/STAGE_5J_0_POST_5I_CONSISTENCY_AUDIT_REPORT.md` in Russian.

Include:

- status and outcome token;
- files inspected;
- fixture/contract/test-plan consistency findings;
- docs fixes made, if any;
- unsupported or risky claims found;
- checks run;
- confirmation that no runtime/tests/fixture-data/output behavior changed;
- private artifact boundary confirmation;
- `export-pm` exclusion confirmation;
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`;
- lifecycle notes.

Acceptable outcome tokens:

- `POST_5I_CONSISTENCY_CONFIRMED`
- `POST_5I_CONSISTENCY_CONFIRMED_AFTER_DOC_FIXES`
- `POST_5I_CONSISTENCY_BLOCKED_FIXTURE_OR_CONTRACT_MISMATCH`

## 8. COMPLETION CRITERIA

- Consistency questions are answered in the report.
- Required docs fixes, if any, are complete.
- Required checks are run or exact inability is recorded.
- No runtime/CLI/SQLite/output/test/fixture-data behavior changed.
- Required report exists.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md` final format.

Do not paste full diffs, large file excerpts, or broad summaries.
