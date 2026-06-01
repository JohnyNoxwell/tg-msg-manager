# STAGE 5F.3 — DATASET DOCTOR OUTPUT EXAMPLES

Status: active task
Stage: 5F.3
Type: docs
Depends on: `docs/stages/reports/STAGE_5F_2_SYNTHETIC_CHANNEL_DATASET_EXAMPLE_REPORT.md`, the Stage 5F.2 synthetic example directory recorded in that report, `docs/architecture/DATASET_VALIDATION.md`, and `tg_msg_manager/services/dataset_validation/` only if output wording must be checked.

---

## 0. CODEX ENTRY CONTRACT

Before editing:

1. Read `AGENTS.md`.
2. Read and apply `.skills/stage-reviewer/SKILL.md`.
3. Read and apply `.skills/architecture-guard/SKILL.md`.
4. Inspect only files listed in this stage, plus directly linked docs needed to verify a claim.
5. Write a compact plan with no more than 5 bullets.

During execution:

- Stop as blocked if the Stage 5F.2 synthetic example does not exist.
- Implement only this stage.
- Do not start Stage 5F.4 or later work.
- Create the factual report before lifecycle cleanup.
- After the report exists, read and apply `.skills/stage-completion-auditor/SKILL.md`.
- Complete lifecycle cleanup according to `AGENTS.md`.

If any required skill is unavailable as a tool, manually read and apply the matching `.skills/<skill-name>/SKILL.md` before reporting it missing.

## 1. PURPOSE

Create user-facing documentation with synthetic examples and interpretation for:

```text
validate-dataset
inspect-dataset
inspect-dataset --doctor
```

The documentation must explain healthy output, warning/error output, doctor suggested actions, and the read-only boundary.

## 2. FILES TO INSPECT

Required:

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/architecture/CURRENT_PROJECT_CONTEXT.md`
- `docs/architecture/README.md`
- `docs/architecture/DATASET_VALIDATION.md`
- `docs/architecture/DATASET_CONTRACT_V1.md`
- `README.md`
- `COMMANDS.md`
- `docs/development/SAFE_FIRST_CHANNEL_EXPORT.md`
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_5F_2_SYNTHETIC_CHANNEL_DATASET_EXAMPLE_REPORT.md`
- the Stage 5F.2 synthetic example directory

Conditional:

- `tg_msg_manager/services/dataset_validation/doctor.py` only if needed to verify exact doctor wording.
- `tg_msg_manager/services/dataset_validation/report_renderer.py` only if needed to verify rendered output.
- Other files under `tg_msg_manager/services/dataset_validation/` only if needed to verify validation or doctor output.

Do not inspect archive files, private artifacts, or existing `docs/stages/reports/` files unrelated to this stage.

## 3. HARD PROHIBITIONS

Do not change:

- runtime code;
- doctor code;
- validation code;
- severity mapping;
- CLI parser behavior, command names, flags, defaults, output, or exit behavior;
- dataset format or Dataset Contract V1;
- exporter code;
- SQLite schema or storage behavior;
- services.

Do not create examples from real export data.

Do not imply that doctor repairs, migrates, fetches from Telegram, rewrites files, mutates source datasets, writes SQLite, analyzes message meaning, classifies users/content, performs OCR/STT/media recognition, or calls LLMs.

Do not read, inspect, copy, summarize, or use real Telegram exports, ignored export directories, sessions, credentials, `.env`, SQLite databases, logs with private identifiers, screenshots, message text, real Telegram IDs/usernames/channels, or private media.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify that the Stage 5F.2 synthetic example and report exist; stop as blocked if they do not.
2. Create a user-facing doctor examples document. Prefer `docs/user/DATASET_DOCTOR_EXAMPLES.md`; if another existing docs convention fits better, use it and explain why in the report.
3. Document interpretation for healthy dataset output, warnings, errors, `message_id_gap_detected`, missing required files, missing conditional files, media path issues, reply parent warnings, suggested actions, and read-only behavior.
4. Create additional synthetic example variants only if required to demonstrate warning/error output.
5. Add docs links only where needed.

## 5. REQUIRED DOCS

Allowed documentation changes:

- `docs/user/DATASET_DOCTOR_EXAMPLES.md` or the chosen documentation path.
- Stage 5F.2 synthetic example variants only if needed for warning/error demonstrations.
- `README.md` only for a precise link if useful.
- `COMMANDS.md` only for a precise link if useful.
- `docs/development/SAFE_FIRST_CHANNEL_EXPORT.md` only for a precise link if useful.
- `docs/stages/reports/STAGE_5F_3_DATASET_DOCTOR_OUTPUT_EXAMPLES_REPORT.md`.
- `docs/stages/README.md` and this stage file only during lifecycle cleanup after the report exists.

Do not update unrelated docs.

## 6. TESTS / VERIFICATION

Run:

```bash
git diff --check
```

If synthetic examples exist and commands can run without credentials, run:

```bash
python3 -m tg_msg_manager.cli validate-dataset --path <synthetic_path>
python3 -m tg_msg_manager.cli inspect-dataset --path <synthetic_path>
python3 -m tg_msg_manager.cli inspect-dataset --path <synthetic_path> --doctor
```

If examples include JSON mode, run the corresponding `--json` commands or record why not.

Do not claim unrun checks passed.

## 7. REPORT

Create:

```text
docs/stages/reports/STAGE_5F_3_DATASET_DOCTOR_OUTPUT_EXAMPLES_REPORT.md
```

The report must be written in Russian and include:

- status;
- docs file path created or updated;
- synthetic dataset path used;
- whether Stage 5F.2 was present;
- commands run to generate or verify examples;
- warnings or errors demonstrated;
- files changed;
- checks run;
- skills applied;
- confirmation that doctor remains read-only;
- confirmation that no real export artifacts were used;
- confirmations for preserved behavior, CLI, SQLite, dataset formats, storage contracts, export behavior, validation/doctor behavior, and private-artifact boundary;
- lifecycle actions.

## 8. COMPLETION CRITERIA

This stage is complete only if:

- examples are based only on synthetic data;
- healthy, warning, and error interpretation is documented;
- doctor read-only boundary is explicit;
- no validation, doctor, runtime, CLI, SQLite, dataset, exporter, or service behavior changed;
- the factual report exists;
- `stage-completion-auditor` has been applied;
- lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md`, stay under 1200 characters, and include only meaningful sections.

Do not include full diffs, large copied file content, markdown tables, generic summaries, speculation, or future recommendations.
