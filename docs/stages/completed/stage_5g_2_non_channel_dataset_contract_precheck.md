# STAGE 5G.2 — Non-Channel Dataset Contract Precheck

Status: active task
Stage: 5G.2
Type: report
Depends on: current non-channel export/db-export/export-pm implementation, existing docs, existing tests

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.
Use `stage-reviewer` before implementation, `architecture-guard` for CLI/service/storage/dataset boundary review, and `stage-completion-auditor` before claiming complete. If a skill is unavailable as a tool, read and apply the matching `.skills/<skill-name>/SKILL.md` file manually.

Do not execute any other 5G stage.

## 1. PURPOSE

Perform a read-only precheck of existing behavior, docs, and tests for non-channel output families: user/group `export`, `db-export`, and `export-pm`. Do not create a formal contract or change runtime behavior.

Acceptable outcomes:

- `PRECHECK_COMPLETE_SEPARATE_CONTRACTS_RECOMMENDED`
- `PRECHECK_COMPLETE_CONTRACT_NOT_READY`
- `PRECHECK_COMPLETE_EXPORT_PM_DEFERRED`
- `BLOCKED_INSUFFICIENT_CURRENT_FILES`

## 2. FILES TO INSPECT

Required reading:

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/architecture/CURRENT_PROJECT_CONTEXT.md`
- `docs/architecture/DATASET_CONTRACT_V1.md`
- `docs/architecture/DATASET_FORMAT.md`
- `docs/architecture/TXT_RENDERING.md`
- `docs/architecture/README.md`
- `README.md`
- `COMMANDS.md`
- `docs/user/QUICKSTART.md`
- `docs/development/README.md`
- `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`

Read if present and record absence if missing:

- `docs/stages/reports/STAGE_5D_3_TXT_PROJECTION_CONTRACT_CLARIFICATION_REPORT.md`
- `docs/stages/reports/STAGE_4A_7_DB_EXPORT_TXT_PROFILE_PARITY_REPORT.md`

Inspect current code/tests only as needed:

- `tg_msg_manager/cli_parser.py`
- `tg_msg_manager/cli/commands/`
- `tg_msg_manager/services/export/`
- `tg_msg_manager/services/db_export/`
- `tg_msg_manager/services/private_archive/`
- `tg_msg_manager/services/rendering/`
- `tg_msg_manager/services/context/`
- `tg_msg_manager/infrastructure/storage/read/`
- `tg_msg_manager/infrastructure/storage/write/`
- `tests/`

Allowed change targets:

- `docs/stages/reports/STAGE_5G_2_NON_CHANNEL_DATASET_CONTRACT_PRECHECK_REPORT.md`
- optional `docs/architecture/NON_CHANNEL_DATASET_CONTRACT_PRECHECK.md`
- lifecycle copy under `docs/stages/completed/`
- `docs/stages/README.md`

## 3. HARD PROHIBITIONS

- Do not create a formal contract.
- Do not change runtime behavior, CLI behavior, output formats, TXT rendering, JSONL schema, SQLite, storage, exporter/db-export/private archive services, or tests.
- Do not create synthetic examples unless separately scoped.
- Do not read real private exports, sessions, credentials, logs, screenshots, DB files, ignored private artifacts, or archive docs as current instruction.
- Do not turn non-channel exports into Dataset Contract V1.
- Do not add analytics, profiling, OSINT, OCR, STT, media recognition, GUI/Web/SaaS, or LLM behavior.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Inspect required docs and current files; do not edit yet.
2. Summarize current output behavior for user/group `export`, including TXT projections, JSONL outputs, `--json`, `--txt-profile context-readable`, and `--txt-profile legacy`.
3. Summarize current output behavior for `db-export`, including `--json`, `--txt-profile`, TXT profile parity, JSONL stability, tests, and gaps.
4. Summarize current `export-pm` outputs and whether they are dataset, archive, text log, media structure, or another output family.
5. Recommend whether one contract or separate contracts are needed, whether `export-pm` should be deferred, which tests/docs are required later, and whether optional findings docs are useful.
6. Create the required Russian factual report and then complete lifecycle cleanup according to `AGENTS.md`.

## 5. REQUIRED DOCS

Preferred output is report-only. Create `docs/architecture/NON_CHANNEL_DATASET_CONTRACT_PRECHECK.md` only if the findings are stable and useful outside the stage report.

Do not update user docs unless command examples are changed; such changes should normally be deferred.

## 6. TESTS / VERIFICATION

Run:

```bash
git diff --check
```

Runtime tests are not required for this precheck/report-only stage unless command examples are changed.

If command examples are changed, verify against:

- `tg_msg_manager/cli_parser.py`
- `README.md`
- `COMMANDS.md`

Do not claim checks passed unless actually run.

## 7. REPORT

Create `docs/stages/reports/STAGE_5G_2_NON_CHANNEL_DATASET_CONTRACT_PRECHECK_REPORT.md` in Russian.

Include:

- status and outcome token;
- files inspected;
- existing behavior summary for user/group export;
- existing behavior summary for `db-export`;
- existing behavior summary for `export-pm`;
- tests/docs coverage found;
- gaps;
- recommendation token such as `CONTRACT_STAGE_NEEDED`, `CONTRACT_STAGE_NOT_READY`, `SEPARATE_CONTRACTS_RECOMMENDED`, or `EXPORT_PM_DEFERRED`;
- no-runtime-change confirmation;
- private-artifact boundary confirmation;
- lifecycle notes.

## 8. COMPLETION CRITERIA

- Precheck questions are answered from current files.
- No runtime, CLI, schema, storage, dataset, or test behavior changed.
- Required report exists.
- Optional findings doc is created only if justified.
- Required checks are run or exact skip reasons are recorded.
- `stage-completion-auditor` is applied.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md`, be under 1200 characters, and include only meaningful sections. Do not paste full diffs or broad summaries.
