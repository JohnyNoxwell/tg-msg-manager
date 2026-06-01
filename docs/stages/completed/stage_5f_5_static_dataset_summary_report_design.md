# STAGE 5F.5 — STATIC DATASET SUMMARY REPORT DESIGN

Status: active task
Stage: 5F.5
Type: docs
Depends on: `docs/architecture/POST_PROCESSING_BOUNDARY.md`, `docs/architecture/DATASET_CONTRACT_V1.md`, `docs/architecture/DATASET_VALIDATION.md`, and optional `docs/stages/reports/STAGE_5F_4_POST_PROCESSING_EXAMPLE_CATALOGUE_REFINEMENT_REPORT.md` if it exists before this stage starts.

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
- Do not start any next stage.
- Create the factual report before lifecycle cleanup.
- After the report exists, read and apply `.skills/stage-completion-auditor/SKILL.md`.
- Complete lifecycle cleanup according to `AGENTS.md`.

If any required skill is unavailable as a tool, manually read and apply the matching `.skills/<skill-name>/SKILL.md` before reporting it missing.

## 1. PURPOSE

Create a docs-only design for a future static dataset summary report as an external derived artifact.

The design must stay downstream of export, validation, inspection, and doctor output. It must not become part of the direct channel export dataset contract unless a later explicit stage scopes that separately.

This stage must not implement a report generator, CLI command, service, exporter hook, validator hook, doctor hook, SQLite persistence, or runtime package.

## 2. FILES TO INSPECT

Required:

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/architecture/CURRENT_PROJECT_CONTEXT.md`
- `docs/architecture/README.md`
- `docs/architecture/POST_PROCESSING_BOUNDARY.md`
- `docs/architecture/DATASET_CONTRACT_V1.md`
- `docs/architecture/DATASET_VALIDATION.md`
- `README.md`
- `COMMANDS.md`
- `docs/stages/README.md`

Conditional:

- `docs/stages/reports/STAGE_5F_4_POST_PROCESSING_EXAMPLE_CATALOGUE_REFINEMENT_REPORT.md` if present.
- `tg_msg_manager/cli_parser.py` only if command examples are added or changed.

Do not inspect archive files, private artifacts, or existing `docs/stages/reports/` files unrelated to this stage.

## 3. HARD PROHIBITIONS

Do not:

- implement runtime code;
- create a CLI command;
- add exporter hooks;
- add validator or doctor changes;
- add SQLite persistence;
- change dataset formats;
- change Dataset Contract V1;
- change services;
- add tests unless a docs-only check requires none;
- generate real reports from real datasets;
- make identity, profiling, or OSINT claims;
- add sentiment or narrative classification;
- add OCR, STT, or media recognition;
- add automatic claims about real persons;
- add LLM-dependent core behavior.

Do not read, inspect, copy, summarize, or use real Telegram exports, ignored export directories, sessions, credentials, `.env`, SQLite databases, logs with private identifiers, screenshots, message text, real Telegram IDs/usernames/channels, or private media.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Create a docs-only design file. Preferred path: `docs/architecture/STATIC_DATASET_SUMMARY_REPORT_DESIGN.md`.
2. Define the report as an external derived artifact after export, validation, inspection, and doctor output.
3. Include fields for source dataset path, source manifest schema version, generated time, deterministic flag, external service usage flag, LLM usage flag, message count, date range, media count, media status summary, discussion coverage summary, validation status, doctor findings summary, artifact list, and privacy checklist.
4. State explicit non-goals and forbidden boundaries.
5. Update architecture/docs links only where needed.

## 5. REQUIRED DOCS

Allowed documentation changes:

- `docs/architecture/STATIC_DATASET_SUMMARY_REPORT_DESIGN.md` or the chosen design path.
- `docs/architecture/README.md` only for a precise link to the design.
- `docs/architecture/POST_PROCESSING_BOUNDARY.md` only for a precise cross-link if needed.
- `README.md` or `COMMANDS.md` only for precise links if command examples or docs entrypoints require it.
- `docs/stages/reports/STAGE_5F_5_STATIC_DATASET_SUMMARY_REPORT_DESIGN_REPORT.md`.
- `docs/stages/README.md` and this stage file only during lifecycle cleanup after the report exists.

Do not update unrelated docs.

## 6. TESTS / VERIFICATION

Run:

```bash
git diff --check
```

If command examples are added or changed, verify them against:

- `tg_msg_manager/cli_parser.py`
- `README.md`
- `COMMANDS.md`

Do not claim unrun checks passed.

## 7. REPORT

Create:

```text
docs/stages/reports/STAGE_5F_5_STATIC_DATASET_SUMMARY_REPORT_DESIGN_REPORT.md
```

The report must be written in Russian and include:

- status;
- design document path;
- design scope;
- fields included;
- explicit non-goals;
- files changed;
- checks run;
- skills applied;
- preserved post-processing boundary;
- confirmation that no runtime implementation was added;
- confirmations for preserved behavior, CLI, SQLite, dataset formats, storage contracts, export behavior, validation/doctor behavior, and private-artifact boundary;
- lifecycle actions.

## 8. COMPLETION CRITERIA

This stage is complete only if:

- a docs-only design exists;
- the report remains an external derived artifact;
- forbidden analytics, OSINT, profiling, and media-recognition behavior is excluded;
- no runtime, CLI, SQLite, dataset, exporter, validator, doctor, or service behavior changed;
- the factual report exists;
- `stage-completion-auditor` has been applied;
- lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md`, stay under 1200 characters, and include only meaningful sections.

Do not include full diffs, large copied file content, markdown tables, generic summaries, speculation, or future recommendations.
