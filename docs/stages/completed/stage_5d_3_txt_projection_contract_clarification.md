# STAGE 5D.3 — TXT PROJECTION CONTRACT CLARIFICATION

Status: active task
Stage: 5D.3
Type: docs/tests
Depends on: `docs/stages/reports/STAGE_5D_1_DATASET_CONTRACT_GAP_CLOSURE_PLAN_REPORT.md`

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` first.
- Read the Stage 5D.1 report before editing.
- Apply `stage-reviewer` before edits.
- Apply `architecture-guard` because TXT projection docs affect dataset/export boundaries.
- Write a plan with max 5 bullets before editing.
- Do not implement Stage 5D.4 or later.

## 1. PURPOSE

Clarify TXT projection contracts before expanding mode matrix tests.

This stage must remove ambiguity between:

- direct channel export TXT projections: `messages.txt`, `discussion_comments.txt`;
- user/group `export` TXT profiles;
- `db-export` TXT profiles.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/stages/reports/STAGE_5D_1_DATASET_CONTRACT_GAP_CLOSURE_PLAN_REPORT.md`
- `docs/architecture/TXT_RENDERING.md`
- `docs/architecture/DATASET_FORMAT.md`
- `docs/architecture/DATASET_CONTRACT_V1.md`
- `docs/architecture/DATASET_CONTRACT_COVERAGE_MATRIX.md`
- `docs/development/CLI_CONTRACT.md`
- `COMMANDS.md`
- `README.md`
- `tg_msg_manager/services/channel_export/txt_renderer.py`
- `tg_msg_manager/services/channel_export/discussions/txt_renderer.py`
- `tg_msg_manager/services/rendering/txt_profiles.py`
- `tests/services/channel_export/test_channel_export_renderers.py`
- `tests/services/channel_export/test_channel_export_dataset_contracts.py`
- `tests/cli/test_txt_profile_cli.py`

## 3. HARD PROHIBITIONS

- Do not change renderer output unless a stale test proves docs are wrong and the active task explicitly scopes the behavior correction.
- Do not add golden snapshot tests for full TXT output.
- Do not change JSONL, manifest, state, SQLite, CLI flags, or TXT profile names.
- Do not add analytics, classification, OCR, STT, LLM behavior, or media analysis.
- Do not inspect private exports.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Confirm current direct channel TXT renderer smoke-test contract.
2. Confirm current `export` and `db-export` TXT profile defaults from code/tests.
3. Fix stale or ambiguous docs only:
   - channel TXT is human-readable projection, not canonical schema;
   - channel TXT tests remain smoke/marker tests, not full golden snapshots;
   - user/group and DB TXT profile defaults must match `DEFAULT_TXT_PROFILE`.
4. Update the coverage matrix to reflect that TXT projection clarification is complete.
5. Do not broaden direct channel TXT behavior.

## 5. REQUIRED DOCS

- `docs/architecture/TXT_RENDERING.md`
- `docs/architecture/DATASET_FORMAT.md`
- `docs/architecture/DATASET_CONTRACT_V1.md` only if its TXT wording is ambiguous.
- `docs/architecture/DATASET_CONTRACT_COVERAGE_MATRIX.md`
- `COMMANDS.md` or `README.md` only if they contradict current defaults.

## 6. TESTS / VERIFICATION

- `python3 -m pytest tests/services/channel_export/test_channel_export_renderers.py tests/services/channel_export/test_channel_export_dataset_contracts.py tests/cli/test_txt_profile_cli.py -q`
- `git diff --check`

## 7. REPORT

Create `docs/stages/reports/STAGE_5D_3_TXT_PROJECTION_CONTRACT_CLARIFICATION_REPORT.md` in Russian.

The report must include:

- docs changed;
- confirmed channel TXT contract;
- confirmed `export` and `db-export` TXT profile defaults;
- verification results;
- confirmation that runtime behavior, CLI, dataset JSON files, and SQLite were preserved;
- skill lines:
  - `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
  - `architecture-guard: applied from .skills/architecture-guard/SKILL.md`

## 8. COMPLETION CRITERIA

- TXT projection docs no longer contradict code/tests.
- Coverage matrix no longer lists TXT projection clarification as open.
- `stage-completion-auditor` is applied after the report.
- Lifecycle cleanup is completed according to `AGENTS.md`; do not move unrelated later active files.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Do not continue to Stage 5D.4.
