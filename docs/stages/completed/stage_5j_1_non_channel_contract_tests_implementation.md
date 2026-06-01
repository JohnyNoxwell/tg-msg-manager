# STAGE 5J.1 — NON-CHANNEL CONTRACT TESTS IMPLEMENTATION

Status: active task
Stage: 5J.1
Type: test implementation
Depends on: `docs/stages/reports/STAGE_5J_0_POST_5I_CONSISTENCY_AUDIT_REPORT.md`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.

Apply these skills before implementation:

- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md` after checks/report/cleanup

Do not execute Stage 5J.2 or later.

## 1. PURPOSE

Add offline deterministic tests for fixture-backed non-channel user/group `export` and `db-export` contract surfaces.

Tests must use synthetic fixtures only and must not modify runtime behavior to make tests pass.

## 2. FILES TO INSPECT

Required:

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/stages/reports/STAGE_5J_0_POST_5I_CONSISTENCY_AUDIT_REPORT.md`
- `docs/stages/reports/STAGE_5I_1_USER_DB_EXPORT_SYNTHETIC_FIXTURE_IMPLEMENTATION_REPORT.md`
- `docs/stages/reports/STAGE_5I_2_NON_CHANNEL_CONTRACT_TEST_PLAN_REPORT.md`
- `docs/stages/reports/STAGE_5I_3_NON_CHANNEL_EXPORT_CONTRACT_V1_DRAFT_REPORT.md`
- `docs/development/NON_CHANNEL_CONTRACT_TEST_PLAN.md`
- `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_V1.md`
- `docs/architecture/TXT_RENDERING.md`
- `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`
- `README.md`
- `COMMANDS.md`
- `Makefile`
- `pyproject.toml`
- `docs/stages/README.md`
- `tests/fixtures/non_channel_export/`
- `tests/fixtures/db_export/`
- `tests/cli/`
- `tests/services/db_export/`
- `tests/services/rendering/`
- `tg_msg_manager/services/db_export/`
- `tg_msg_manager/services/rendering/`
- `tg_msg_manager/services/export/`
- `tg_msg_manager/infrastructure/storage/`
- `tg_msg_manager/cli_parser.py`

Writable paths:

- `tests/services/rendering/**`
- `tests/services/db_export/**`
- `tests/cli/**`
- `docs/stages/reports/STAGE_5J_1_NON_CHANNEL_CONTRACT_TESTS_IMPLEMENTATION_REPORT.md`
- `docs/stages/README.md`
- `docs/stages/completed/stage_5j_1_non_channel_contract_tests_implementation.md`
- `docs/development/NON_CHANNEL_CONTRACT_TEST_PLAN.md` only for test name/location links
- `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_V1.md` only for test name/location links

## 3. HARD PROHIBITIONS

- Do not change runtime behavior, CLI behavior, output formats, TXT rendering, JSONL schema, SQLite schema/storage behavior, exporter services, `db-export` services, or private archive services.
- Do not alter fixtures to hide runtime/test failures.
- Do not include `export-pm` in user/group + `db-export` contract tests.
- Do not require Telegram credentials, network access, or real data.
- Do not read private artifacts or real exports.
- Do not add brittle tests for exact rotation thresholds unless supported by the contract and fixtures.
- Do not claim full raw JSON profile coverage if deferred.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Inspect existing fixture files and current test organization before editing.
2. Add focused tests in the existing `tests/cli/`, `tests/services/rendering/`, or `tests/services/db_export/` layout.
3. Cover fixture parsing, README/privacy scan, stable JSONL key sets, context-readable TXT markers, legacy TXT markers, `expected_writer_state.json` shape, forbidden private markers, and `export-pm` exclusion.
4. Add generated-output tests only if existing helpers support them without runtime changes; otherwise defer them in the report.
5. Update optional docs links only if added test names/locations need to be recorded.
6. Create the Stage 5J.1 report in Russian.
7. Complete lifecycle cleanup according to `AGENTS.md`.

## 5. REQUIRED DOCS

Docs updates are optional and limited to linking actual test names/locations in:

- `docs/development/NON_CHANNEL_CONTRACT_TEST_PLAN.md`
- `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_V1.md`

Do not expand the contract beyond fixture-backed coverage.

## 6. TESTS / VERIFICATION

Required:

```bash
git diff --check
python3 -m unittest discover tests -p '*non_channel*contract*.py'
```

If the focused command does not match added test names, run the repository-appropriate focused command for the added tests and record the exact command.

Run `make test` if reasonable. If not run, record the exact reason.

Do not claim tests passed unless actually run.

## 7. REPORT

Create `docs/stages/reports/STAGE_5J_1_NON_CHANNEL_CONTRACT_TESTS_IMPLEMENTATION_REPORT.md` in Russian.

Include:

- status and outcome token;
- files inspected;
- tests added;
- assertions covered;
- assertions deferred;
- commands run and exact results;
- whether runtime code was unchanged;
- whether fixtures were unchanged or why they changed;
- private artifact boundary confirmation;
- `export-pm` exclusion confirmation;
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`;
- lifecycle notes.

Acceptable outcome tokens:

- `NON_CHANNEL_CONTRACT_TESTS_IMPLEMENTED_FOCUSED`
- `NON_CHANNEL_CONTRACT_TESTS_IMPLEMENTED_WITH_DOC_LINKS`
- `NON_CHANNEL_CONTRACT_TESTS_PARTIAL_DEFERRED_GENERATED_OUTPUTS`
- `BLOCKED_CONTRACT_OR_FIXTURE_MISMATCH`

## 8. COMPLETION CRITERIA

- Focused offline synthetic tests are added and pass, or exact blocker is reported.
- Runtime/CLI/SQLite/output/service behavior is unchanged.
- Fixture changes, if any, are justified as docs/format typo corrections only.
- Required checks are run or exact inability is recorded.
- Required report exists.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md` final format.

Do not paste full diffs, large file excerpts, or broad summaries.
