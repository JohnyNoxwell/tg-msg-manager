# STAGE 5F.0 - CURRENT ARCHITECTURE / CONTEXT REFRESH

Status: active task
Stage: 5F.0
Type: docs/context refresh
Depends on: Stage 5C.0-5C.5, 5D.1-5D.5, and 5E.0-5E.2 reports listed below; current architecture/development docs listed below.

---

## 0. CODEX ENTRY CONTRACT

1. Read `AGENTS.md`.
2. Read this active stage file.
3. Apply `stage-reviewer` before implementation. If no tool is available, read and apply `.skills/stage-reviewer/SKILL.md`.
4. Apply `architecture-guard` before implementation. If no tool is available, read and apply `.skills/architecture-guard/SKILL.md`.
5. Do not read unrelated docs, source files, completed stages, archive files, or private local artifacts.

## 1. PURPOSE

Refresh the current portable project context after completed Stage 5C, 5D, and 5E work.

This is a docs/context refresh stage only. It must not change Python runtime code, tests, CLI behavior, SQLite schema, dataset formats, storage contracts, or export behavior.

## 2. FILES TO INSPECT

Required:

- `AGENTS.md`
- `docs/stages/active/stage_5f_0_current_architecture_context_refresh.md`
- `.skills/stage-reviewer/SKILL.md` if no `stage-reviewer` tool is available
- `.skills/architecture-guard/SKILL.md` if no `architecture-guard` tool is available
- `docs/stages/reports/STAGE_5C_0_DATASET_CONTRACT_COVERAGE_MATRIX_REPORT.md`
- `docs/stages/reports/STAGE_5C_1_PYTEST_COLLECTION_HYGIENE_REPORT.md`
- `docs/stages/reports/STAGE_5C_2_SKILL_ROUTING_FALLBACK_VERIFICATION_REPORT.md`
- `docs/stages/reports/STAGE_5C_3_CLI_README_COMMANDS_PARITY_AUDIT_REPORT.md`
- `docs/stages/reports/STAGE_5C_4_PRIVACY_SENSITIVE_ARTIFACTS_GUIDE_REPORT.md`
- `docs/stages/reports/STAGE_5C_5_PACKAGE_IDENTITY_VERSION_POLICY_CLEANUP_REPORT.md`
- `docs/stages/reports/STAGE_5D_1_DATASET_CONTRACT_GAP_CLOSURE_PLAN_REPORT.md`
- `docs/stages/reports/STAGE_5D_2_RUN_CHANGELOG_KEY_SET_CONTRACT_TESTS_REPORT.md`
- `docs/stages/reports/STAGE_5D_3_TXT_PROJECTION_CONTRACT_CLARIFICATION_REPORT.md`
- `docs/stages/reports/STAGE_5D_4_CHANNEL_EXPORT_MODE_MATRIX_TESTS_REPORT.md`
- `docs/stages/reports/STAGE_5D_5_USER_QUICKSTART_SAFE_FIRST_EXPORT_GUIDE_REPORT.md`
- `docs/stages/reports/STAGE_5E_0_SQLITE_SCHEMA_SPLIT_STAGE_2_MIGRATION_HELPERS_PRECHECK_REPORT.md`
- `docs/stages/reports/STAGE_5E_1_SQLITE_SCHEMA_SPLIT_STAGE_2_MIGRATION_HELPER_EXTRACTION_REPORT.md`
- `docs/stages/reports/STAGE_5E_2_SQLITE_SCHEMA_SPLIT_REGRESSION_EXPANSION_REPORT.md`
- `docs/README.md`
- `docs/architecture/README.md`
- `docs/architecture/DATASET_CONTRACT_V1.md`
- `docs/architecture/DATASET_CONTRACT_COVERAGE_MATRIX.md`
- `docs/architecture/DATASET_FORMAT.md`
- `docs/architecture/DATASET_VALIDATION.md`
- `docs/architecture/TXT_RENDERING.md`
- `docs/architecture/SQLITE_SCHEMA_SPLIT_MAP.md`
- `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`
- `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`
- `docs/development/SAFE_FIRST_CHANNEL_EXPORT.md`
- `docs/development/CLI_CONTRACT.md`
- `README.md`
- `COMMANDS.md`

Allowed change targets:

- `docs/architecture/CURRENT_PROJECT_CONTEXT.md`, or an existing canonical portable context file if one already exists
- `docs/architecture/README.md`, only to add or correct the context file link
- `docs/stages/reports/STAGE_5F_0_CURRENT_ARCHITECTURE_CONTEXT_REFRESH_REPORT.md`
- `docs/stages/README.md`
- `docs/stages/active/stage_5f_0_current_architecture_context_refresh.md`, only for lifecycle cleanup
- `docs/stages/completed/stage_5f_0_current_architecture_context_refresh.md`, only as the lifecycle cleanup destination for this stage file

## 3. HARD PROHIBITIONS

- Do not edit Python runtime code.
- Do not edit tests.
- Do not change CLI names, flags, defaults, output, or behavior.
- Do not change SQLite schema, migrations, storage contracts, or SQL behavior.
- Do not change dataset formats, manifests, state files, output layouts, or export behavior.
- Do not add new functionality, post-processing implementation, analytics, OSINT, profiling, classification, OCR, STT, media analysis, LLM-dependent behavior, GUI, Web UI, or SaaS features.
- Do not start SQLite schema split stage 3.
- Do not rewrite historical reports or completed stage files.
- Do not read private local artifacts, exported datasets, sessions, databases, credentials, or archive prompts.
- Do not add feature logic to protected service facades or compatibility wrappers.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Confirm whether a canonical portable context file already exists. Update it if present; otherwise create `docs/architecture/CURRENT_PROJECT_CONTEXT.md`.
2. Extract only factual current-state items from the required reports and docs.
3. Write a compact context document suitable for a new Codex chat.
4. Add or correct the context link in `docs/architecture/README.md` only if needed.
5. Create the Stage 5F.0 report in Russian.
6. Apply `stage-completion-auditor` after the report exists. If no tool is available, read and apply `.skills/stage-completion-auditor/SKILL.md`.
7. Complete lifecycle cleanup according to `AGENTS.md`: update `docs/stages/README.md` and move this stage file to `docs/stages/completed/` only after the report exists and completion criteria are met.

## 5. REQUIRED DOCS

The context document must cover, briefly and factually:

- Current project identity: project name, module name, console script, version policy, positioning, what the project does, and what it is not.
- Current architecture: CLI layer, runtime/config, services, channel export, dataset validation/inspection/doctor, storage/SQLite, schema split status, and post-processing boundary.
- Stage 5C closure: pytest collection hygiene, skill fallback verification, CLI/docs parity, privacy guide, package identity/version policy.
- Stage 5D closure: dataset contract gaps, run changelog key set tests, TXT projection clarification, channel export mode matrix tests, safe first channel export guide, and the `include_jsonl=False` / `include_txt=False` behavior mismatch only if confirmed by the report.
- Stage 5E closure: schema split stage 2 precheck, migration helper extraction, regression expansion, extracted helper groups, what remains in `_sqlite_schema.py`, and preserved invariants.
- Current risks: closed risks, remaining risks, deferred risks, and what must not be done prematurely.
- Next rational plan: full user quickstart index, synthetic channel dataset example, dataset doctor output examples, later post-processing examples design, later static dataset summary report design, and SQLite schema split stage 3 only if a concrete risk remains.
- Future-stage prohibitions: no analytics/OSINT/profiling in exporter core, no SQLite schema changes without explicit stage, no dataset format changes without docs/tests, no protected facade bloat, no private artifact reading, and no premature GUI/Web UI/SaaS work.

Keep the document concise. Do not duplicate full reports or large docs content.

## 6. TESTS / VERIFICATION

Required:

```bash
git diff --check
```

Optional scope check:

```bash
git diff --name-only
```

Do not run pytest or compile checks unless a prohibited runtime/test edit accidentally occurred; if that happens, stop and report the scope violation instead of expanding the stage.

Do not claim checks passed unless they were actually run.

## 7. REPORT

Create:

- `docs/stages/reports/STAGE_5F_0_CURRENT_ARCHITECTURE_CONTEXT_REFRESH_REPORT.md`

The report must be in Russian and include:

- scope completed;
- changed files;
- checks run and results;
- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md` if applied manually;
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md` if applied manually;
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md` if applied manually;
- confirmation that runtime behavior, CLI behavior, SQLite schema, dataset formats, and export behavior were preserved.

## 8. COMPLETION CRITERIA

- Canonical portable context exists and is linked from architecture docs if needed.
- Context content is factual, current, compact, and covers all required topics.
- No runtime code, tests, schema, dataset format, storage contract, CLI, or export behavior changed.
- Stage report exists.
- `git diff --check` was run and passed, or failure is documented with exact cause.
- `stage-completion-auditor` was applied after the report exists.
- Lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

- Final response must follow the `AGENTS.md` final structure.
- Final response max 1200 characters.
- Reports and factual completion records must be in Russian.
- No full diffs.
- No markdown tables unless explicitly needed.
- No broad summaries, speculation, or future recommendations beyond the required next-plan section.
