# STAGE 5O.4 — Dataset Contract Constants

Status: active task
Stage: 5O.4
Type: implementation
Depends on: completed Stage 5O.0 report and current dataset validation/export contracts

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` and this file before editing.
- Do not start unless `docs/stages/reports/STAGE_5O_0_REFACTORING_GUARDRAILS_REPORT.md` exists or the user explicitly overrides the dependency.
- Use `stage-reviewer` before implementation; if unavailable, read `.skills/stage-reviewer/SKILL.md` manually and state that in the report.
- Use `architecture-guard` because this stage touches dataset validation/export boundaries; if unavailable, read `.skills/architecture-guard/SKILL.md` manually and state that in the report.
- Write a compact plan with no more than 5 bullets before edits.

## 1. PURPOSE

Reduce drift risk by centralizing repeated dataset contract filenames and artifact keys without changing dataset output, validation behavior, or docs semantics.

## 2. FILES TO INSPECT

- `tg_msg_manager/services/dataset_validation/`
- `tg_msg_manager/services/channel_export/`
- `tg_msg_manager/core/models/`
- `tests/services/dataset_validation/`
- `tests/services/channel_export/`
- `docs/architecture/DATASET_FORMAT.md`
- `docs/architecture/DATASET_VALIDATION.md`

May change:

- a new neutral constants module under `tg_msg_manager/core/models/` or another architecture-safe location
- dataset validation modules that currently repeat contract filenames
- channel export modules that currently repeat the same contract filenames
- focused tests under `tests/services/dataset_validation/` and `tests/services/channel_export/`
- `docs/stages/reports/STAGE_5O_4_DATASET_CONTRACT_CONSTANTS_REPORT.md`
- lifecycle updates required by `AGENTS.md`

## 3. HARD PROHIBITIONS

- Do not change dataset filenames, manifest keys, artifact names, run changelog keys, validation codes, or output layouts.
- Do not move feature logic into `core`.
- Do not make `core` import services or infrastructure.
- Do not change SQLite behavior or persist channel posts/comments to DB.
- Do not read existing `docs/stages/reports/` files unrelated to this stage.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Identify only duplicated constants that are already part of documented dataset contracts.
2. Create a neutral constants module with names only; do not add formatting, validation, IO, or business logic.
3. Replace duplicate literal usages where this does not increase coupling.
4. Add tests that prove validation/export still recognize the same filenames and keys.
5. If a constant cannot be centralized without violating imports, leave it in place and document the reason in the report.

## 5. REQUIRED DOCS

- Update docs only if a code/doc mismatch is discovered; no contract change is expected.
- Create the required report in Russian.

## 6. TESTS / VERIFICATION

Run:

- `pytest tests/services/dataset_validation tests/services/channel_export`
- `python3 -m compileall tg_msg_manager`
- `ruff check tg_msg_manager tests/services/dataset_validation tests/services/channel_export`

## 7. REPORT

Create `docs/stages/reports/STAGE_5O_4_DATASET_CONTRACT_CONSTANTS_REPORT.md` in Russian with:

- constants centralized;
- literals intentionally left duplicated and why;
- tests run and results;
- confirmation that dataset format was preserved.

## 8. COMPLETION CRITERIA

- No dataset output or validation contract changed.
- Centralized constants do not create invalid imports.
- Required report exists.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Keep final response under 1200 characters unless the user asks otherwise.
