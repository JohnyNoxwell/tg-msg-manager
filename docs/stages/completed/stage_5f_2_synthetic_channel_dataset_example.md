# STAGE 5F.2 — SYNTHETIC CHANNEL DATASET EXAMPLE

Status: active task
Stage: 5F.2
Type: docs
Depends on: `docs/architecture/DATASET_CONTRACT_V1.md`, `docs/architecture/DATASET_FORMAT.md`, `docs/architecture/DATASET_VALIDATION.md`, `docs/stages/reports/STAGE_5F_0_CURRENT_ARCHITECTURE_CONTEXT_REFRESH_REPORT.md`, and `tg_msg_manager/services/dataset_validation/` only if validation behavior must be checked.

---

## 0. CODEX ENTRY CONTRACT

Before editing:

1. Read `AGENTS.md`.
2. Read and apply `.skills/stage-reviewer/SKILL.md`.
3. Read and apply `.skills/architecture-guard/SKILL.md`.
4. Inspect only files listed in this stage, plus directly linked docs needed to verify a claim.
5. Write a compact plan with no more than 5 bullets.

During execution:

- Implement only this stage.
- Do not start Stage 5F.3 or later work.
- Create the factual report before lifecycle cleanup.
- After the report exists, read and apply `.skills/stage-completion-auditor/SKILL.md`.
- Complete lifecycle cleanup according to `AGENTS.md`.

If any required skill is unavailable as a tool, manually read and apply the matching `.skills/<skill-name>/SKILL.md` before reporting it missing.

## 1. PURPOSE

Create a safe, minimal, synthetic direct channel export dataset example that demonstrates Dataset Contract V1 structure.

The example must not use real Telegram data, private exports, logs, sessions, local database content, screenshots, real identifiers, or real media.

## 2. FILES TO INSPECT

Required:

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/architecture/CURRENT_PROJECT_CONTEXT.md`
- `docs/architecture/README.md`
- `docs/architecture/DATASET_CONTRACT_V1.md`
- `docs/architecture/DATASET_FORMAT.md`
- `docs/architecture/DATASET_VALIDATION.md`
- `README.md`
- `COMMANDS.md`
- `docs/development/SAFE_FIRST_CHANNEL_EXPORT.md`
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_5F_0_CURRENT_ARCHITECTURE_CONTEXT_REFRESH_REPORT.md`

Conditional:

- `tg_msg_manager/services/dataset_validation/` only if needed to make the synthetic example validate against current behavior.
- Existing repository example directories only to choose the least surprising path.

Do not inspect archive files, private artifacts, or existing `docs/stages/reports/` files unrelated to this stage.

## 3. HARD PROHIBITIONS

Do not change:

- runtime code;
- exporter code;
- validator code;
- doctor code;
- CLI parser behavior, command names, flags, defaults, output, or exit behavior;
- Dataset Contract V1;
- SQLite schema or storage behavior;
- services;
- tests, unless a documentation-only smoke reference is explicitly necessary and remains non-runtime.

Do not alter contract or validator behavior to make the example pass. The example must conform to the current contract, not the reverse.

Do not include real media. If media is represented, use metadata-only records and synthetic relative paths.

Do not read, inspect, copy, summarize, or use real Telegram exports, ignored export directories, sessions, credentials, `.env`, SQLite databases, logs with private identifiers, screenshots, message text, real Telegram IDs/usernames/channels, or private media.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Choose the example path. Prefer `docs/examples/channel_dataset_minimal/`; if another existing examples path clearly fits better, use it and explain why in the report.
2. Create only files required for a safe minimal Dataset Contract V1 direct channel export example.
3. Use synthetic channel id, username, title, message ids, timestamps, neutral text, and relative paths only.
4. Add or update documentation links pointing to the example only where needed.
5. Do not create warning/error variants; those belong to Stage 5F.3.

## 5. REQUIRED DOCS

Allowed documentation changes:

- `docs/examples/channel_dataset_minimal/` or the chosen example directory.
- `README.md` only for a precise link to the example if useful.
- `COMMANDS.md` only for a precise link to the example if useful.
- `docs/development/SAFE_FIRST_CHANNEL_EXPORT.md` only for a precise link to the example if useful.
- `docs/stages/reports/STAGE_5F_2_SYNTHETIC_CHANNEL_DATASET_EXAMPLE_REPORT.md`.
- `docs/stages/README.md` and this stage file only during lifecycle cleanup after the report exists.

Do not update unrelated docs.

## 6. TESTS / VERIFICATION

Run:

```bash
git diff --check
```

If possible without credentials, also run:

```bash
python3 -m tg_msg_manager.cli validate-dataset --path <example_path>
python3 -m tg_msg_manager.cli inspect-dataset --path <example_path>
```

Do not claim unrun checks passed. If validation or inspection cannot run, record the exact reason in the report.

## 7. REPORT

Create:

```text
docs/stages/reports/STAGE_5F_2_SYNTHETIC_CHANNEL_DATASET_EXAMPLE_REPORT.md
```

The report must be written in Russian and include:

- status;
- chosen example path;
- files created or changed;
- synthetic data policy;
- checks run;
- whether validation and inspection were run;
- exact reason if validation or inspection was not run;
- skills applied;
- confirmation that no private data was used;
- confirmations for preserved behavior, CLI, SQLite, dataset contract, storage contracts, export behavior, validation/doctor behavior, and private-artifact boundary;
- lifecycle actions.

## 8. COMPLETION CRITERIA

This stage is complete only if:

- a safe synthetic dataset example exists;
- the example uses no private data;
- it conforms to current Dataset Contract V1 or intentional warnings are documented;
- validation and inspection were run or exact blockers were recorded;
- no runtime, CLI, SQLite, dataset-contract, exporter, validator, doctor, or service behavior changed;
- the factual report exists;
- `stage-completion-auditor` has been applied;
- lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md`, stay under 1200 characters, and include only meaningful sections.

Do not include full diffs, large copied file content, markdown tables, generic summaries, speculation, or future recommendations.
