# STAGE 4C.0B — CHANNEL EXPORT WORKFLOW SPLIT

Status: active task
Stage: 4C.0B
Type: refactor / architecture hardening
Depends on: `tg_msg_manager/services/channel_export/service.py` current orchestration and Stage 4C.0A CLI split

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Execute only Stage 4C.0B.

Goal: move workflow-specific channel export run paths from `ChannelExportService`
into focused workflow modules without changing runtime behavior.

Do not start Stage 4C.0C.

## 1. PURPOSE

Keep `ChannelExportService` orchestration-only by extracting full export,
incremental export, and no-new-posts workflow paths.

## 2. FILES TO INSPECT

Required:

```text
tg_msg_manager/services/channel_export/service.py
tg_msg_manager/services/channel_export/models.py
tg_msg_manager/services/channel_export/plan_builder.py
tg_msg_manager/services/channel_export/result_builder.py
tg_msg_manager/services/channel_export/event_emitter.py
tg_msg_manager/services/channel_export/payload_writer.py
tg_msg_manager/services/channel_export/manifest_coordinator.py
tg_msg_manager/services/channel_export/media_processor.py
tg_msg_manager/services/channel_export/discussions/
tests/test_channel_export*.py
tests/test_channel_export_discussion*.py
```

May create:

```text
tg_msg_manager/services/channel_export/workflows/
docs/stages/reports/STAGE_4C_0B_CHANNEL_EXPORT_WORKFLOW_SPLIT_REPORT.md
```

May update `docs/architecture/` only if ownership boundaries change.

## 3. HARD PROHIBITIONS

Do not change channel export behavior, media behavior, discussion behavior,
dataset formats, manifest/state/changelog formats, filenames, output layout,
force/incremental/no-new-work semantics, SQLite schema, CLI flags, or public imports.

Do not add analytics, OCR, STT, media recognition, GUI, web UI, persistence, new
runtime dependencies, or feature logic to protected facades.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Map `ChannelExportService` responsibilities before editing.
2. Create `tg_msg_manager/services/channel_export/workflows/`.
3. Extract full export workflow.
4. Extract incremental workflow, including no-new-posts path.
5. Keep `ChannelExportService` limited to dependency wiring, option validation,
   source/plan setup, workflow selection, delegation, and failure emission.

## 5. REQUIRED DOCS

Create the stage report. Update architecture docs only for changed ownership
boundaries. Do not update user docs unless behavior docs become inaccurate.

## 6. TESTS / VERIFICATION

Run:

```bash
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
pytest tests -q -k "channel_export"
```

Record any skipped command and exact reason.

## 7. REPORT

Report in Russian:

```text
files moved/created
files changed
behavior preserved
checks run
checks not run and why
remaining follow-up
```

## 8. COMPLETION CRITERIA

Stage 4C.0B is complete when workflow modules own run paths, service facade is
thin, public imports still work, focused checks are recorded, docs are current,
the report exists, and lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

Use `AGENTS.md` compact final response format. No full diffs.
