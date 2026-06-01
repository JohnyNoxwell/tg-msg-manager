# STAGE 5I.3 — Non-Channel Export Contract V1 Draft

Status: active task
Stage: 5I.3
Type: docs
Depends on: docs/stages/reports/STAGE_5I_1_USER_DB_EXPORT_SYNTHETIC_FIXTURE_IMPLEMENTATION_REPORT.md and docs/stages/reports/STAGE_5I_2_NON_CHANNEL_CONTRACT_TEST_PLAN_REPORT.md

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Then read `.skills/stage-reviewer/SKILL.md`, `.skills/architecture-guard/SKILL.md`, `.skills/stage-completion-auditor/SKILL.md`, and this stage file. Use `stage-reviewer` before implementation, `architecture-guard` before reporting, and `stage-completion-auditor` before claiming completion.

Do not start future stages.

## 1. PURPOSE

Draft `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_V1.md` for user/group `export` and `db-export` outputs under `DB_EXPORTS/` only when synthetic fixtures and contract test planning support the claims.

The contract documents existing behavior. It must not force or imply runtime changes.

## 2. FILES TO INSPECT

Required docs:

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/stages/reports/STAGE_5H_1_NON_CHANNEL_EXPORT_CONTRACT_DESIGN_PRECHECK_REPORT.md`
- `docs/stages/reports/STAGE_5H_2_USER_DB_EXPORT_SYNTHETIC_FIXTURES_PLAN_REPORT.md`
- `docs/stages/reports/STAGE_5I_1_USER_DB_EXPORT_SYNTHETIC_FIXTURE_IMPLEMENTATION_REPORT.md`
- `docs/stages/reports/STAGE_5I_2_NON_CHANNEL_CONTRACT_TEST_PLAN_REPORT.md`
- `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_DESIGN.md`
- `docs/development/NON_CHANNEL_SYNTHETIC_FIXTURES_PLAN.md`
- `docs/development/NON_CHANNEL_CONTRACT_TEST_PLAN.md`
- `docs/architecture/TXT_RENDERING.md`
- `docs/architecture/DATASET_CONTRACT_V1.md`
- `docs/architecture/DATASET_FORMAT.md`
- `docs/architecture/PRIVATE_ARCHIVE_CONTRACT_DEFERRED_DECISION.md`
- `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`
- `README.md`
- `COMMANDS.md`
- `docs/stages/README.md`

Allowed to create or edit:

- `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_V1.md`
- `docs/architecture/README.md`
- `docs/stages/reports/STAGE_5I_3_NON_CHANNEL_EXPORT_CONTRACT_V1_DRAFT_REPORT.md`
- `docs/stages/README.md`
- `docs/stages/completed/stage_5i_3_non_channel_export_contract_v1_draft.md`

Optional link-only updates if justified:

- `README.md`
- `COMMANDS.md`
- `docs/development/NON_CHANNEL_SYNTHETIC_FIXTURES_PLAN.md`
- `docs/development/NON_CHANNEL_CONTRACT_TEST_PLAN.md`

## 3. HARD PROHIBITIONS

- Do not change runtime code, tests, fixtures, CLI behavior, output formats, TXT rendering, JSONL schema, SQLite schema, storage behavior, services, or protected files.
- Do not add runtime dependencies.
- Do not create fixtures or tests.
- Do not include `export-pm`, private archive outputs, direct channel export Dataset Contract V1 internals, real Telegram data, media binaries, private artifacts, OSINT, analytics, profiling, OCR, STT, media recognition, or LLM behavior.
- Do not claim unsupported guarantees, exact rotation thresholds, full raw JSON profile behavior, SQLite schema contract status, release readiness, publish/tag/version changes, or behavior not backed by fixtures/test plan/current docs.
- Do not use real examples or realistic private conversations.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify whether 5I.1 fixture and 5I.2 test-plan prerequisites exist; block or downgrade to precheck if they are absent or insufficient.
2. Create `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_V1.md` only if claims can be mapped to fixture/test-plan/current-doc support.
3. Cover purpose, scope, non-goals, Dataset Contract V1 relationship, TXT rendering relationship, user/group `export`, `db-export`, shared TXT projection rules, `context-readable`, `legacy`, compact JSONL, filenames/directories, part files, `.export_state`, `.writer_state`, fixtures, tests, privacy constraints, known limitations, deferred areas, and `export-pm` exclusion.
4. Mark unsupported or unstable areas as deferred instead of inventing guarantees.
5. Update architecture index and optional docs with short links only if the contract file is created.

## 5. REQUIRED DOCS

Create the stage report. If the contract is created, update `docs/architecture/README.md` with a link. Optional docs may receive link-only updates. Update `docs/stages/README.md` during lifecycle cleanup.

## 6. TESTS / VERIFICATION

Run:

```bash
git diff --check
```

Runtime tests are not required for docs-only scope.

Verify:

- The contract is supported by 5I.1 fixtures and 5I.2 test plan, or unsupported areas are deferred.
- No private or real data is included.
- `export-pm` is excluded.
- Dataset Contract V1 and post-processing boundaries are preserved.
- No runtime changes are required or implied.

## 7. REPORT

Create `docs/stages/reports/STAGE_5I_3_NON_CHANNEL_EXPORT_CONTRACT_V1_DRAFT_REPORT.md` in Russian. Include status/outcome token, files inspected, prerequisite status, contract file created or not, sections included, areas deferred, fixture/test-plan support mapping, no runtime/CLI/SQLite/output behavior changes, private artifact boundary confirmation, `export-pm` exclusion, checks run, and lifecycle notes.

Allowed outcome tokens:

- `NON_CHANNEL_EXPORT_CONTRACT_V1_DRAFT_CREATED`
- `NON_CHANNEL_EXPORT_CONTRACT_V1_DRAFT_CREATED_WITH_DEFERRED_AREAS`
- `NON_CHANNEL_EXPORT_CONTRACT_V1_DRAFT_BLOCKED_WAITING_FOR_FIXTURES_OR_TEST_PLAN`
- `NON_CHANNEL_EXPORT_CONTRACT_V1_DRAFT_DOWNGRADED_TO_PRECHECK`

## 8. COMPLETION CRITERIA

- Prerequisites are satisfied or missing support is handled by block/downgrade.
- Contract claims are backed by fixtures/test plan/current docs or marked deferred.
- Required report exists.
- `git diff --check` was run or failure is recorded.
- No runtime/tests/fixtures/CLI/SQLite/output behavior changed.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md`, be in Russian, avoid full diffs, and mention only changed files, checks, preservation, notes, and stage status.
