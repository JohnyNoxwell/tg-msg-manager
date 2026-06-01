# STAGE 5G.0 — Post-5F Documentation / Examples Consistency Audit

Status: active task
Stage: 5G.0
Type: docs audit
Depends on: completed Stage 5F.1-5F.5 reports, current user docs, current synthetic examples

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.
Use `stage-reviewer` before implementation, `architecture-guard` for boundary-sensitive findings, and `stage-completion-auditor` before claiming complete. If a skill is unavailable as a tool, read and apply the matching `.skills/<skill-name>/SKILL.md` file manually.

Do not execute any other 5G stage.

## 1. PURPOSE

Audit documentation and synthetic examples added or updated by the 5F block for consistency. Fix only small documentation/navigation inconsistencies that are directly found and safe.

Acceptable outcomes:

- `CONSISTENT_NO_DOC_FIXES_REQUIRED`
- `CONSISTENT_AFTER_DOC_FIXES`
- `BLOCKED_WITH_FINDINGS`

## 2. FILES TO INSPECT

Required reading:

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/architecture/CURRENT_PROJECT_CONTEXT.md`
- `docs/architecture/README.md`
- `docs/architecture/DATASET_VALIDATION.md`
- `docs/architecture/POST_PROCESSING_BOUNDARY.md`
- `docs/architecture/STATIC_DATASET_SUMMARY_REPORT_DESIGN.md`
- `README.md`
- `COMMANDS.md`
- `docs/README.md`
- `docs/development/README.md`
- `docs/development/SAFE_FIRST_CHANNEL_EXPORT.md`
- `docs/user/QUICKSTART.md`
- `docs/user/DATASET_DOCTOR_EXAMPLES.md`
- `docs/stages/README.md`

Read these reports if present and record missing ones:

- `docs/stages/reports/STAGE_5F_1_USER_DOCUMENTATION_NAVIGATION_AUDIT_QUICKSTART_CONSOLIDATION_REPORT.md`
- `docs/stages/reports/STAGE_5F_2_SYNTHETIC_CHANNEL_DATASET_EXAMPLE_REPORT.md`
- `docs/stages/reports/STAGE_5F_3_DATASET_DOCTOR_OUTPUT_EXAMPLES_REPORT.md`
- `docs/stages/reports/STAGE_5F_4_POST_PROCESSING_EXAMPLE_CATALOGUE_REFINEMENT_REPORT.md`
- `docs/stages/reports/STAGE_5F_5_STATIC_DATASET_SUMMARY_REPORT_DESIGN_REPORT.md`

Inspect these example directories without reading private artifacts:

- `docs/examples/channel_dataset_minimal/`
- `docs/examples/channel_dataset_warning_gap/`
- `docs/examples/channel_dataset_missing_required_file/`

Inspect only if command examples are evaluated:

- `tg_msg_manager/cli_parser.py`
- `tg_msg_manager/cli/__init__.py`

Allowed change targets:

- files listed above under root docs, `docs/`, and `docs/stages/README.md`
- `docs/stages/reports/STAGE_5G_0_POST_5F_DOCUMENTATION_EXAMPLES_CONSISTENCY_AUDIT_REPORT.md`
- lifecycle copy under `docs/stages/completed/`

## 3. HARD PROHIBITIONS

- Do not change runtime code, tests, CLI parser behavior, command names, flags, defaults, or output behavior.
- Do not change exporter, validator, inspector, doctor, storage, SQLite, services, dataset generation, or Dataset Contract V1.
- Do not add post-processing implementation, static report generator implementation, or a new CLI command.
- Do not create, alter, or inspect real export artifacts, sessions, credentials, real logs, screenshots, local SQLite DB files, or ignored private content.
- Do not add GUI/Web/SaaS/OSINT/profiling/LLM analytics.
- Do not rewrite historical reports.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Inspect the required docs, reports, and synthetic example paths; do not edit yet.
2. Answer the consistency questions for quickstart entrypoint, command reference, validation/inspection/doctor read-only boundary, post-processing external boundary, synthetic example paths/statuses, privacy warnings, stale 5F references, and static report design links.
3. If inconsistencies are small and documentation-only, make minimal edits in allowed files.
4. If a major inconsistency requires runtime changes or a separate stage, do not fix it; record `BLOCKED_WITH_FINDINGS`.
5. Create the required Russian factual report and then complete lifecycle cleanup according to `AGENTS.md`.

## 5. REQUIRED DOCS

Update docs only when the audit finds stale or contradictory documentation. Keep `COMMANDS.md` as the command reference and `docs/user/QUICKSTART.md` as the user entrypoint if the audit confirms that structure.

## 6. TESTS / VERIFICATION

Run:

```bash
git diff --check
```

If command examples are changed, compare them manually or with a focused script against:

- `tg_msg_manager/cli_parser.py`
- `README.md`
- `COMMANDS.md`

If synthetic example paths or statuses are referenced, run where possible:

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
```

Expected missing-required-file validation: exit code `1`, status `errors`.

Do not claim checks passed unless actually run.

## 7. REPORT

Create `docs/stages/reports/STAGE_5G_0_POST_5F_DOCUMENTATION_EXAMPLES_CONSISTENCY_AUDIT_REPORT.md` in Russian.

Include:

- status and outcome token;
- whether the stage was audit-only or docs-fix;
- files inspected;
- inconsistencies found;
- changes made;
- checks run and exact outcomes;
- confirmation that runtime/CLI/SQLite/dataset/export/validation/doctor behavior was preserved;
- confirmation that private artifacts were not read;
- lifecycle notes.

## 8. COMPLETION CRITERIA

- Consistency questions are answered.
- Only allowed files changed.
- Required report exists.
- Required checks are run or exact skip reasons are recorded.
- `stage-completion-auditor` is applied.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md`, be under 1200 characters, and include only meaningful sections. Do not paste full diffs or broad summaries.
