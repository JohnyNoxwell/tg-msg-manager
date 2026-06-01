# STAGE 5D.5 — USER QUICKSTART SAFE FIRST EXPORT GUIDE

Status: active task
Stage: 5D.5
Type: docs
Depends on: `docs/stages/reports/STAGE_5D_1_DATASET_CONTRACT_GAP_CLOSURE_PLAN_REPORT.md`, `docs/stages/reports/STAGE_5D_2_RUN_CHANGELOG_KEY_SET_CONTRACT_TESTS_REPORT.md`, `docs/stages/reports/STAGE_5D_3_TXT_PROJECTION_CONTRACT_CLARIFICATION_REPORT.md`, `docs/stages/reports/STAGE_5D_4_CHANNEL_EXPORT_MODE_MATRIX_TESTS_REPORT.md`

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` first.
- Read Stage 5D.1 through Stage 5D.4 reports before editing.
- Apply `stage-reviewer` before edits.
- Apply `architecture-guard` because this stage documents export/validation boundaries.
- Write a plan with max 5 bullets before editing.
- Do not implement any 5E stage.

## 1. PURPOSE

Create a concise user quickstart for a safe first channel export.

The guide must help a user run a small metadata-only export, validate it, inspect it, and understand privacy boundaries without adding product behavior.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/stages/reports/STAGE_5D_1_DATASET_CONTRACT_GAP_CLOSURE_PLAN_REPORT.md`
- `docs/stages/reports/STAGE_5D_4_CHANNEL_EXPORT_MODE_MATRIX_TESTS_REPORT.md`
- `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`
- `docs/development/CLI_CONTRACT.md`
- `docs/development/README.md`
- `docs/architecture/DATASET_VALIDATION.md`
- `docs/architecture/DATASET_CONTRACT_V1.md`
- `COMMANDS.md`
- `README.md`

## 3. HARD PROHIBITIONS

- Do not change Python code or tests.
- Do not change CLI flags, defaults, command names, output files, dataset schemas, or SQLite behavior.
- Do not present `--media full` or `--discussion full` as the first safe default.
- Do not add analytics, interpretation, reporting, GUI, dashboard, or SaaS framing.
- Do not include real channel names, real user ids, real message text, screenshots, secrets, sessions, local DB content, or private export excerpts.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Add a safe first export guide under `docs/development/`.
2. Use only synthetic placeholders such as `@example`.
3. Include commands in this order:
   - small metadata export with `--limit`;
   - `validate-dataset`;
   - `inspect-dataset`;
   - optional `inspect-dataset --doctor`.
4. Explain when to consider `--media full`, `--discussion metadata`, `--discussion full`, and `--force` without recommending them as first run defaults.
5. Link the guide from `docs/development/README.md`, `docs/README.md`, `README.md`, or `COMMANDS.md` only where existing navigation requires it.

## 5. REQUIRED DOCS

- New guide path: `docs/development/SAFE_FIRST_CHANNEL_EXPORT.md`
- Update at least `docs/development/README.md`.
- Update root navigation only if the new guide would otherwise be undiscoverable.

## 6. TESTS / VERIFICATION

- `git diff --check`
- `rg -n "SAFE_FIRST_CHANNEL_EXPORT|Safe First|safe first|validate-dataset|inspect-dataset" docs README.md COMMANDS.md`
- Code tests are not required for docs-only changes.

## 7. REPORT

Create `docs/stages/reports/STAGE_5D_5_USER_QUICKSTART_SAFE_FIRST_EXPORT_GUIDE_REPORT.md` in Russian.

The report must include:

- docs added or changed;
- privacy/sensitive artifact confirmation;
- verification results;
- confirmation that code, CLI, dataset format, and SQLite were not changed;
- skill lines:
  - `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
  - `architecture-guard: applied from .skills/architecture-guard/SKILL.md`

## 8. COMPLETION CRITERIA

- Safe first export guide exists and is linked.
- Guide uses only safe synthetic placeholders.
- `stage-completion-auditor` is applied after the report.
- Lifecycle cleanup is completed according to `AGENTS.md`; do not move unrelated later active files.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Do not continue to Stage 5E.0.
