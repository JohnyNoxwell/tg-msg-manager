# STAGE 7C.2 — LEGACY NULL DISCUSSION BATCH COMPATIBILITY

Status: completed
Stage: 7C.2
Type: bugfix
Depends on: Stage 7C.0 batch option reconstruction and legacy VPS manifests with `discussion: null`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Execute Stage 7C.2 with the smallest safe patch. Apply `discussion-export-diagnoser`, `bugfix-stage-writer`, `stage-reviewer`, and `architecture-guard`. Do not start later stages or add features.

## 1. SYMPTOM

`update-channels` updates valid modern datasets but rejects two completed legacy datasets with:

```text
Manifest discussion must be a JSON object
```

## 2. REPRODUCTION / OBSERVED OUTPUT

VPS artifacts:

```text
@alekseevka_kharkiv__1257747107/manifest.json: discussion=null
@radnyknews__1650479418/manifest.json: discussion=null
dataset_type=direct_channel_export, schema_version=1.0, status=completed
```

Expected: legacy `discussion: null` is treated as discussion mode `none` without rewriting the manifest.

## 3. LIKELY CAUSE

`ChannelBatchOptionsBuilder.build()` requires `manifest.discussion` to be a JSON object before applying discussion defaults, while older valid manifests used JSON null.

## 4. FILES TO INSPECT

Required:

- `tg_msg_manager/services/channel_export/batch_options.py`
- `tests/services/channel_export/test_channel_batch_update.py`
- `docs/architecture/DATASET_FORMAT.md`
- `COMMANDS.md`
- `.github/workflows/ci.yml`
- `Makefile`

May create `docs/stages/reports/STAGE_7C_2_LEGACY_NULL_DISCUSSION_BATCH_COMPATIBILITY_REPORT.md`. Do not inspect or change unrelated source/docs, archive, completed stages, or unrelated existing reports.

## 5. HARD PROHIBITIONS

- Do not add features, broad refactors, dependencies, or formatting churn.
- Do not change CLI commands/flags/defaults, output files/layout, dataset schema, SQLite schema, or export/state/incremental behavior.
- Do not rewrite legacy manifests or relax validation for non-null non-object discussion values.
- Do not change protected files, service orchestration, media/discussion crawling, or discussion defaults.

## 6. MINIMAL PATCH TASKS

1. Confirm the builder rejects JSON null before option reconstruction; do not edit unrelated validation.
2. Normalize only missing/null `discussion` to `{"mode": "none"}` in batch read compatibility.
3. Preserve strict rejection of scalar/list discussion values and all existing modern-manifest validation.
4. Add regression coverage for null/missing discussion and invalid non-object discussion.

## 7. REGRESSION TESTS

- Assert legacy null and missing discussion build `discussion_mode="none"`, default comment limit, `force=False`, and do not mutate manifest bytes.
- Assert a scalar/list discussion value still fails.

## 8. NON-REGRESSION CHECKS

```bash
python3 -m pytest tests/services/channel_export/test_channel_batch_update.py -q
python3 -m compileall tg_msg_manager
make verify
make pre-commit
```

Do not claim checks passed unless run. Environment/tooling failure leaves the stage incomplete.

## 9. REQUIRED DOCS

- Update `COMMANDS.md` and `docs/architecture/DATASET_FORMAT.md` only with the batch-read legacy compatibility fact; do not change the current write contract.
- Create the required Russian factual report.

## 10. REPORT

Create `docs/stages/reports/STAGE_7C_2_LEGACY_NULL_DISCUSSION_BATCH_COMPATIBILITY_REPORT.md` with exact files/checks, bug fixed, preserved behavior, VPS evidence, and skill application facts.

## 11. COMPLETION CRITERIA

- Legacy null/missing discussion manifests update through the existing batch path without artifact mutation.
- Invalid non-null non-object discussion still fails.
- Regression/full checks pass; report exists; `stage-completion-auditor` passes.
- lifecycle cleanup is completed according to `AGENTS.md`.

## 12. OUTPUT LIMITS

Use `AGENTS.md` compact final response. Do not paste diffs or include broad summaries/recommendations.
