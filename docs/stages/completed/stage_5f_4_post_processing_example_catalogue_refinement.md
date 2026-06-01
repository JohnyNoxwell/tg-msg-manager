# STAGE 5F.4 — POST-PROCESSING EXAMPLE CATALOGUE REFINEMENT

Status: active task
Stage: 5F.4
Type: docs
Depends on: `docs/architecture/POST_PROCESSING_BOUNDARY.md`, `docs/architecture/DATASET_CONTRACT_V1.md`, `docs/architecture/DATASET_VALIDATION.md`, and `docs/stages/reports/STAGE_5F_0_CURRENT_ARCHITECTURE_CONTEXT_REFRESH_REPORT.md`.

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
- Do not start Stage 5F.5 or later work.
- Create the factual report before lifecycle cleanup.
- After the report exists, read and apply `.skills/stage-completion-auditor/SKILL.md`.
- Complete lifecycle cleanup according to `AGENTS.md`.

If any required skill is unavailable as a tool, manually read and apply the matching `.skills/<skill-name>/SKILL.md` before reporting it missing.

## 1. PURPOSE

Refine the catalogue of allowed future external post-processing examples on top of `docs/architecture/POST_PROCESSING_BOUNDARY.md`.

This is a docs-only architecture-boundary refinement stage. It must not create runtime implementation, a `post_processing/` package, exporter hooks, CLI commands, SQLite persistence, or derived analysis behavior.

Preserve this pipeline:

```text
export -> validate/inspect -> dataset doctor -> post-processing -> optional LLM report
```

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
- `docs/stages/reports/STAGE_5F_0_CURRENT_ARCHITECTURE_CONTEXT_REFRESH_REPORT.md`

Conditional:

- `tg_msg_manager/cli_parser.py` only if command examples are added or changed.

Do not inspect archive files, private artifacts, or existing `docs/stages/reports/` files unrelated to this stage.

## 3. HARD PROHIBITIONS

Do not:

- create a `post_processing/` Python package;
- add runtime code;
- add CLI commands;
- add exporter hooks;
- add validator or doctor hooks;
- change SQLite or write derived analysis into SQLite;
- mutate source dataset contract;
- change Dataset Contract V1;
- implement reports;
- implement LLM prompt generation;
- implement analytics.

Explicitly keep these out of exporter core:

- analytics;
- OSINT interpretation;
- profiling;
- identity claims;
- fingerprinting;
- sentiment or narrative classification;
- OCR;
- STT;
- media recognition;
- LLM-dependent behavior.

Do not read, inspect, copy, summarize, or use real Telegram exports, ignored export directories, sessions, credentials, `.env`, SQLite databases, logs with private identifiers, screenshots, message text, real Telegram IDs/usernames/channels, or private media.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Refine `docs/architecture/POST_PROCESSING_BOUNDARY.md` to clarify future external example categories.
2. Include only these future external example categories: Markdown summary, JSON summary, static HTML report, LLM prompt pack outside exporter core, timeline summary, media status summary, discussion coverage summary, and redaction checklist.
3. State that these categories are examples of future external post-processing only, not exporter-core permissions.
4. Create one small companion docs file only if necessary; justify it in the report.
5. Update architecture/docs links only where needed.

## 5. REQUIRED DOCS

Allowed documentation changes:

- `docs/architecture/POST_PROCESSING_BOUNDARY.md`.
- One small companion docs file only if necessary and justified in the report.
- `docs/architecture/README.md` only for a precise link update if a companion file is created.
- `README.md` or `COMMANDS.md` only for precise links if command examples or docs entrypoints require it.
- `docs/stages/reports/STAGE_5F_4_POST_PROCESSING_EXAMPLE_CATALOGUE_REFINEMENT_REPORT.md`.
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
docs/stages/reports/STAGE_5F_4_POST_PROCESSING_EXAMPLE_CATALOGUE_REFINEMENT_REPORT.md
```

The report must be written in Russian and include:

- status;
- files changed;
- whether a companion file was created and why;
- categories added or clarified;
- forbidden boundaries preserved;
- checks run;
- skills applied;
- confirmation that no runtime package or implementation was created;
- confirmations for preserved behavior, CLI, SQLite, dataset formats, storage contracts, export behavior, validation/doctor behavior, and private-artifact boundary;
- lifecycle actions.

## 8. COMPLETION CRITERIA

This stage is complete only if:

- post-processing examples are clearly external and future-scoped;
- exporter core boundaries are stronger, not weaker;
- no implementation exists;
- no CLI, runtime, SQLite, dataset, validation, doctor, exporter, or service behavior changed;
- the factual report exists;
- `stage-completion-auditor` has been applied;
- lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md`, stay under 1200 characters, and include only meaningful sections.

Do not include full diffs, large copied file content, markdown tables, generic summaries, speculation, or future recommendations.
