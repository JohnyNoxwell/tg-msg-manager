# STAGE 5I.0 — Non-Channel Synthetic Fixtures Stage Files

Status: active task
Stage: 5I.0
Type: docs
Depends on: docs/stages/reports/STAGE_5H_1_NON_CHANNEL_EXPORT_CONTRACT_DESIGN_PRECHECK_REPORT.md, docs/stages/reports/STAGE_5H_2_USER_DB_EXPORT_SYNTHETIC_FIXTURES_PLAN_REPORT.md, docs/stages/reports/STAGE_5H_3_PRIVATE_ARCHIVE_CONTRACT_DEFERRED_DECISION_REPORT.md

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Then read `.skills/stage-reviewer/SKILL.md`, `.skills/architecture-guard/SKILL.md`, `.skills/stage-completion-auditor/SKILL.md`, and the stage-writer skill if available. Use `stage-reviewer` before accepting generated stage files, use `architecture-guard` before reporting, and use `stage-completion-auditor` before claiming this stage complete.

Do not execute stages 5I.1, 5I.2, or 5I.3.

## 1. PURPOSE

Create or refine executable active stage files for the next non-channel synthetic fixture and contract work:

- `5I.1` user/group `export` and `db-export` synthetic fixtures.
- `5I.2` non-channel contract test plan.
- `5I.3` non-channel export contract V1 draft.

This is a meta-stage only.

## 2. FILES TO INSPECT

Required:

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/stages/reports/STAGE_5H_1_NON_CHANNEL_EXPORT_CONTRACT_DESIGN_PRECHECK_REPORT.md`
- `docs/stages/reports/STAGE_5H_2_USER_DB_EXPORT_SYNTHETIC_FIXTURES_PLAN_REPORT.md`
- `docs/stages/reports/STAGE_5H_3_PRIVATE_ARCHIVE_CONTRACT_DEFERRED_DECISION_REPORT.md`
- `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_DESIGN.md`
- `docs/development/NON_CHANNEL_SYNTHETIC_FIXTURES_PLAN.md`
- `docs/architecture/PRIVATE_ARCHIVE_CONTRACT_DEFERRED_DECISION.md`
- `docs/architecture/CURRENT_PROJECT_CONTEXT.md`
- `docs/architecture/TXT_RENDERING.md`
- `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`
- `docs/stages/README.md`
- `README.md`
- `COMMANDS.md`

Allowed to create or edit:

- `docs/stages/active/stage_5i_1_user_db_export_synthetic_fixture_implementation.md`
- `docs/stages/active/stage_5i_2_non_channel_contract_test_plan.md`
- `docs/stages/active/stage_5i_3_non_channel_export_contract_v1_draft.md`
- `docs/stages/reports/STAGE_5I_0_NON_CHANNEL_SYNTHETIC_FIXTURES_STAGE_FILES_REPORT.md`
- `docs/stages/README.md`
- `docs/stages/completed/stage_5i_0_non_channel_synthetic_fixtures_stage_files.md`

## 3. HARD PROHIBITIONS

- Do not create fixtures, tests, final contract docs, runtime code, or examples.
- Do not change CLI behavior, output formats, TXT rendering, JSONL schema, SQLite schema, storage, services, or protected files.
- Do not add runtime dependencies.
- Do not read private artifacts, real exports, sessions, credentials, ignored DB files, logs, screenshots, or media.
- Do not include real Telegram data or realistic private conversations.
- Do not include `export-pm` or private archive in the user/group + `db-export` contract scope.
- Do not execute 5I.1, 5I.2, or 5I.3.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Confirm all 5H reports and design/planning docs listed above exist; block with `BLOCKED_MISSING_5H_CONTEXT` if required context is absent.
2. Create or refine stage files for 5I.1, 5I.2, and 5I.3 using the stage-writer shape.
3. Ensure each generated stage file has exact scope, allowed files, hard prohibitions, required Russian report path, verification, lifecycle cleanup, and compact output limits.
4. Ensure each generated stage file forbids private artifacts, real Telegram data, `export-pm`, runtime behavior changes, CLI changes, SQLite changes, and unsupported output-format changes.
5. Run stage-reviewer and architecture-guard against the generated stage files and patch only stage-file defects.

## 5. REQUIRED DOCS

Update only `docs/stages/README.md` if active/completed stage listings change. Do not edit user docs, architecture docs, README, COMMANDS, or changelog in this meta-stage.

## 6. TESTS / VERIFICATION

Run:

```bash
git diff --check
```

No runtime tests are required because this stage changes only stage files and the stage index.

## 7. REPORT

Create `docs/stages/reports/STAGE_5I_0_NON_CHANNEL_SYNTHETIC_FIXTURES_STAGE_FILES_REPORT.md` in Russian. Include status/outcome token, files inspected, stage files created or refined, whether all three future stages were created, checks run, confirmation that no runtime/tests/fixtures/contracts changed, private artifact boundary confirmation, `export-pm` exclusion, and lifecycle notes.

Allowed outcome tokens:

- `STAGE_FILES_CREATED_FOR_5I_SEQUENCE`
- `STAGE_FILE_CREATED_FOR_5I1_ONLY`
- `BLOCKED_MISSING_5H_CONTEXT`

## 8. COMPLETION CRITERIA

- Required context is present or the stage is blocked with exact missing files.
- Stage files for the selected 5I sequence are executable and pass stage-reviewer.
- Architecture-guard reports no boundary violations.
- Required report exists.
- `git diff --check` was run or failure is recorded.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md`, be in Russian, avoid full diffs, and mention only changed files, checks, preservation, notes, and stage status.
