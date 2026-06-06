# STAGE 5O.8 — Discussion Builder Split

Status: active task
Stage: 5O.8
Type: implementation
Depends on: completed Stage 5O.0 report and current discussion export tests

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` and this file before editing.
- Do not start unless `docs/stages/reports/STAGE_5O_0_REFACTORING_GUARDRAILS_REPORT.md` exists or the user explicitly overrides the dependency.
- Use `stage-reviewer` before implementation; if unavailable, read `.skills/stage-reviewer/SKILL.md` manually and state that in the report.
- Use `architecture-guard` because this stage touches channel export services; if unavailable, read `.skills/architecture-guard/SKILL.md` manually and state that in the report.
- Write a compact plan with no more than 5 bullets before edits.

## 1. PURPOSE

Separate pure discussion artifact/status building from `ChannelDiscussionExporter` orchestration while preserving dataset artifacts and discussion export semantics.

## 2. FILES TO INSPECT

- `tg_msg_manager/services/channel_export/discussions/exporter.py`
- `tg_msg_manager/services/channel_export/discussions/`
- `tg_msg_manager/services/channel_export/models.py`
- `tests/services/channel_export/discussions/`
- `tests/services/channel_export/test_channel_export_service.py`
- `docs/architecture/DATASET_FORMAT.md`
- `docs/architecture/DATASET_VALIDATION.md`

May change:

- modules under `tg_msg_manager/services/channel_export/discussions/`
- focused discussion tests
- `docs/stages/reports/STAGE_5O_8_DISCUSSION_BUILDER_SPLIT_REPORT.md`
- lifecycle updates required by `AGENTS.md`

## 3. HARD PROHIBITIONS

- Do not change discussion artifact filenames, status values, JSON fields, ordering, or dataset layout.
- Do not change discussion fetch behavior, Telegram API behavior, retry behavior, or media behavior.
- Do not add DB persistence for channel posts or discussion comments.
- Do not change `ChannelExportService` except mechanical wiring if unavoidable.
- Do not read existing `docs/stages/reports/` files unrelated to this stage.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Add pure tests for discussion status/root-id/comments-count decisions using synthetic records.
2. Extract status/thread/metadata building into one or more pure helper modules under `discussions/`.
3. Keep `ChannelDiscussionExporter` responsible for orchestration, fetch coordination, and writing only.
4. Reuse existing models; do not introduce broad generic abstractions.
5. Run focused discussion and channel export tests.

## 5. REQUIRED DOCS

- Update dataset docs only if a documented mismatch is discovered; no format change is allowed.
- Create the required report in Russian.

## 6. TESTS / VERIFICATION

Run:

- `pytest tests/services/channel_export/discussions`
- `pytest tests/services/channel_export/test_channel_export_service.py`
- `python3 -m compileall tg_msg_manager`
- `ruff check tg_msg_manager/services/channel_export tests/services/channel_export`

## 7. REPORT

Create `docs/stages/reports/STAGE_5O_8_DISCUSSION_BUILDER_SPLIT_REPORT.md` in Russian with:

- helpers extracted;
- artifact/status behavior preserved;
- tests run and results;
- any intentionally deferred discussion cleanup.

## 8. COMPLETION CRITERIA

- Builder logic is testable without exporter orchestration.
- Discussion dataset contract is unchanged.
- Required report exists.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Keep final response under 1200 characters unless the user asks otherwise.
