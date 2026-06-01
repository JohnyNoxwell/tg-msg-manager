# STAGE 5G.1 — Synthetic Examples Regression Check

Status: active task
Stage: 5G.1
Type: docs audit
Depends on: Stage 5F.2 and 5F.3 reports, current synthetic examples, current validation/inspection/doctor CLI

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.
Use `stage-reviewer` before implementation, `architecture-guard` for validation/doctor boundary review, and `stage-completion-auditor` before claiming complete. If a skill is unavailable as a tool, read and apply the matching `.skills/<skill-name>/SKILL.md` file manually.

Do not execute any other 5G stage.

## 1. PURPOSE

Verify that synthetic channel dataset examples still produce the documented validation, inspection, and doctor outcomes. This stage may be audit-only or may make narrow documentation corrections. It must not change runtime behavior.

Acceptable outcomes:

- `REGRESSION_EXPECTATIONS_CONFIRMED`
- `REGRESSION_EXPECTATIONS_CONFIRMED_AFTER_DOC_FIXES`
- `BLOCKED_ENVIRONMENT_COMMANDS_NOT_RUN`
- `REGRESSION_MISMATCH_FOUND`

## 2. FILES TO INSPECT

Required reading:

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/user/DATASET_DOCTOR_EXAMPLES.md`
- `docs/development/SAFE_FIRST_CHANNEL_EXPORT.md`
- `docs/architecture/DATASET_VALIDATION.md`
- `docs/architecture/DATASET_CONTRACT_V1.md`
- `docs/stages/reports/STAGE_5F_2_SYNTHETIC_CHANNEL_DATASET_EXAMPLE_REPORT.md`
- `docs/stages/reports/STAGE_5F_3_DATASET_DOCTOR_OUTPUT_EXAMPLES_REPORT.md`

Inspect:

- `docs/examples/channel_dataset_minimal/`
- `docs/examples/channel_dataset_warning_gap/`
- `docs/examples/channel_dataset_missing_required_file/`

Allowed change targets:

- docs corrections in listed docs if expected statuses or paths are stale
- optional `docs/development/SYNTHETIC_EXAMPLES_REGRESSION_CHECKLIST.md` only if it avoids duplication
- `docs/stages/reports/STAGE_5G_1_SYNTHETIC_EXAMPLES_REGRESSION_CHECK_REPORT.md`
- lifecycle copy under `docs/stages/completed/`
- `docs/stages/README.md`

## 3. HARD PROHIBITIONS

- Do not change runtime code, validator/inspector/doctor logic, CLI behavior, dataset format, Dataset Contract V1, exporter behavior, SQLite, services, or tests.
- Do not use real Telegram exports, real Telegram IDs/usernames/message text, sessions, credentials, logs, screenshots, local DB files, ignored private artifacts, or real export directories.
- Do not convert synthetic examples into generated outputs from real data.
- Do not repair runtime mismatches in this stage; record them and recommend a separate bugfix stage.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Inspect required docs, reports, and synthetic example directories; do not edit yet.
2. Run the required validation, inspection, and doctor commands or record exact environment blockers.
3. Compare observed statuses and expected warning/error codes with documented expectations.
4. If docs paths or status text are stale, make minimal docs-only corrections in allowed files.
5. Create the required Russian factual report and then complete lifecycle cleanup according to `AGENTS.md`.

## 5. REQUIRED DOCS

Only update docs if expected statuses, paths, or warning/error code descriptions are stale. Do not create `docs/development/SYNTHETIC_EXAMPLES_REGRESSION_CHECKLIST.md` if existing docs can hold the correction without duplication.

## 6. TESTS / VERIFICATION

Run or record exact reason not run:

```bash
python3 -m tg_msg_manager.cli validate-dataset --path docs/examples/channel_dataset_minimal
python3 -m tg_msg_manager.cli inspect-dataset --path docs/examples/channel_dataset_minimal
python3 -m tg_msg_manager.cli inspect-dataset --path docs/examples/channel_dataset_minimal --doctor
python3 -m tg_msg_manager.cli validate-dataset --path docs/examples/channel_dataset_warning_gap
python3 -m tg_msg_manager.cli inspect-dataset --path docs/examples/channel_dataset_warning_gap
python3 -m tg_msg_manager.cli inspect-dataset --path docs/examples/channel_dataset_warning_gap --doctor
python3 -m tg_msg_manager.cli validate-dataset --path docs/examples/channel_dataset_missing_required_file
python3 -m tg_msg_manager.cli inspect-dataset --path docs/examples/channel_dataset_missing_required_file
python3 -m tg_msg_manager.cli inspect-dataset --path docs/examples/channel_dataset_missing_required_file --doctor
git diff --check
```

Expected results:

- `channel_dataset_minimal`: validate exit `0` status `ok`; inspect exit `0` validation status `ok`; doctor exit `0` status `ok`.
- `channel_dataset_warning_gap`: validate exit `0` status `warnings`; inspect exit `0` validation status `warnings`; doctor exit `0` status `warnings`; warning includes `message_id_gap_detected`.
- `channel_dataset_missing_required_file`: validate exit `1` status `errors`; inspect exit `0` validation status `errors`; doctor exit `0` status `errors`; error includes `missing_required_file`.

Optional JSON checks are allowed only if docs claim JSON examples or JSON stability.

Do not claim checks passed unless actually run.

## 7. REPORT

Create `docs/stages/reports/STAGE_5G_1_SYNTHETIC_EXAMPLES_REGRESSION_CHECK_REPORT.md` in Russian.

Include:

- status and outcome token;
- example directories checked;
- exact command outcomes;
- whether expected statuses matched;
- whether warning/error codes matched expectations;
- docs changes, if any;
- confirmation that no real artifacts were used;
- confirmation that runtime/CLI/SQLite/dataset/export/validation/doctor behavior was preserved;
- lifecycle notes.

## 8. COMPLETION CRITERIA

- Required commands are run or exact blockers are recorded.
- Observed outcomes are compared to expectations.
- Only allowed files changed.
- Required report exists.
- `stage-completion-auditor` is applied.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md`, be under 1200 characters, and include only meaningful sections. Do not paste full diffs or broad summaries.
