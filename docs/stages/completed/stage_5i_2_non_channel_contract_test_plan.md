# STAGE 5I.2 — Non-Channel Contract Test Plan

Status: active task
Stage: 5I.2
Type: docs
Depends on: docs/stages/reports/STAGE_5H_2_USER_DB_EXPORT_SYNTHETIC_FIXTURES_PLAN_REPORT.md; optional prerequisite to inspect is docs/stages/reports/STAGE_5I_1_USER_DB_EXPORT_SYNTHETIC_FIXTURE_IMPLEMENTATION_REPORT.md

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Then read `.skills/stage-reviewer/SKILL.md`, `.skills/architecture-guard/SKILL.md`, `.skills/stage-completion-auditor/SKILL.md`, and this stage file. Use `stage-reviewer` before implementation, `architecture-guard` before reporting, and `stage-completion-auditor` before claiming completion.

Do not execute 5I.3.

## 1. PURPOSE

Define the test strategy for the future non-channel export contract covering user/group `export` and `db-export`.

Default scope is plan/report only. Do not implement tests unless this stage file is intentionally revised before execution.

## 2. FILES TO INSPECT

Required docs:

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/stages/reports/STAGE_5H_1_NON_CHANNEL_EXPORT_CONTRACT_DESIGN_PRECHECK_REPORT.md`
- `docs/stages/reports/STAGE_5H_2_USER_DB_EXPORT_SYNTHETIC_FIXTURES_PLAN_REPORT.md`
- `docs/stages/reports/STAGE_5I_1_USER_DB_EXPORT_SYNTHETIC_FIXTURE_IMPLEMENTATION_REPORT.md`
- `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_DESIGN.md`
- `docs/development/NON_CHANNEL_SYNTHETIC_FIXTURES_PLAN.md`
- `docs/architecture/TXT_RENDERING.md`
- `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`
- `README.md`
- `COMMANDS.md`
- `Makefile`
- `pyproject.toml`
- `docs/stages/README.md`

Inspect for path realism only:

- `tests/`
- `tests/fixtures/`
- `tests/cli/`
- `tests/services/db_export/`
- `tests/services/rendering/`
- `tests/services/private_archive/`
- `tg_msg_manager/services/export/`
- `tg_msg_manager/services/db_export/`
- `tg_msg_manager/services/rendering/`
- `tg_msg_manager/infrastructure/storage/`

Allowed to create or edit:

- `docs/stages/reports/STAGE_5I_2_NON_CHANNEL_CONTRACT_TEST_PLAN_REPORT.md`
- `docs/stages/README.md`
- `docs/stages/completed/stage_5i_2_non_channel_contract_test_plan.md`

Optional docs-only plan:

- `docs/development/NON_CHANNEL_CONTRACT_TEST_PLAN.md`

## 3. HARD PROHIBITIONS

- Do not change runtime code, tests, fixtures, CLI behavior, output formats, TXT rendering, JSONL schema, SQLite schema, storage behavior, services, or protected files.
- Do not add runtime dependencies.
- Do not create final contract docs.
- Do not include `export-pm` in the user/group + `db-export` contract test scope.
- Do not read private artifacts, real exports, sessions, credentials, ignored DB files, logs, screenshots, or media.
- Do not require Telegram credentials, network access, or real data.
- Do not claim tests exist unless they already exist.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Check whether the 5I.1 fixture report and fixture paths exist; decide whether to continue from 5I.1, plan from 5H.2 only, or block.
2. Decide whether future tests should use golden files, generated-output comparisons, or both.
3. Recommend exact test locations for user/group `export`, `db-export`, shared TXT rendering, and compact JSONL.
4. Define assertion categories for filenames, extensions, TXT markers, compact JSONL key sets, omitted null/empty values, reply fields, media metadata-only fields, part file paths, `.export_state`, `.writer_state`, synthetic-data scanning, and `export-pm` exclusion.
5. Define execution expectations: offline, deterministic, no Telegram credentials, temporary SQLite only when DB behavior is tested, and inclusion in `make test` if appropriate.
6. Create `docs/development/NON_CHANNEL_CONTRACT_TEST_PLAN.md` only if a durable docs plan is justified; otherwise keep the plan in the report.

## 5. REQUIRED DOCS

Create the stage report. If `docs/development/NON_CHANNEL_CONTRACT_TEST_PLAN.md` is created, mark it as a plan and not an implemented suite. Update `docs/stages/README.md` during lifecycle cleanup.

## 6. TESTS / VERIFICATION

Run:

```bash
git diff --check
```

Runtime tests are not required for plan-only scope. If existing tests are inspected or run, record exact commands and results.

Verify any test-plan doc:

- Does not claim tests exist unless they do.
- Requires no Telegram credentials or network access.
- Uses synthetic/offline fixtures only.
- Excludes `export-pm` except as explicitly deferred or out of scope.

## 7. REPORT

Create `docs/stages/reports/STAGE_5I_2_NON_CHANNEL_CONTRACT_TEST_PLAN_REPORT.md` in Russian. Include status/outcome token, files inspected, whether 5I.1 fixtures exist, recommended test locations, assertion categories, tests to implement later, tests deferred, whether a test plan doc was created, no runtime/CLI/SQLite/output behavior changes, private artifact boundary confirmation, checks run, and lifecycle notes.

Allowed outcome tokens:

- `CONTRACT_TEST_PLAN_COMPLETE_DOC_CREATED`
- `CONTRACT_TEST_PLAN_COMPLETE_REPORT_ONLY`
- `CONTRACT_TEST_PLAN_WAITING_FOR_FIXTURES`
- `BLOCKED_INSUFFICIENT_CONTEXT`

## 8. COMPLETION CRITERIA

- Plan/report answers all required test scope, location, assertion, and execution questions.
- Optional docs-only plan is accurate if created.
- Required report exists.
- `git diff --check` was run or failure is recorded.
- No runtime/tests/fixtures/CLI/SQLite/output behavior changed.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md`, be in Russian, avoid full diffs, and mention only changed files, checks, preservation, notes, and stage status.
