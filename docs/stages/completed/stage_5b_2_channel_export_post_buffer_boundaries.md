# STAGE 5B.2 — Channel Export Post Buffer Boundaries

Status: active task
Stage: 5B.2
Type: implementation
Depends on: `tg_msg_manager/services/channel_export/workflows/`; `tg_msg_manager/services/channel_export/run_changelog.py`

---

## 0. CODEX ENTRY CONTRACT

1. Read `AGENTS.md`.
2. Read this stage file only.
3. Apply `stage-reviewer` before implementation. If no tool exists, read `.skills/stage-reviewer/SKILL.md`.
4. Apply `architecture-guard` because this touches channel export workflows and dataset metadata. If no tool exists, read `.skills/architecture-guard/SKILL.md`.
5. Do not start any other active 5B stage.

## 1. PURPOSE

Reduce avoidable full channel post object retention in direct channel export without changing dataset files, manifest fields, state semantics, run changelog schema, CLI behavior, or discussion behavior.

Current risk to address:

- `run_full_export()` keeps `current_run_records` for all posts.
- In no-discussion mode, full post records are only needed later for run changelog facts.

## 2. FILES TO INSPECT

Inspect only:

- `AGENTS.md`
- `docs/architecture/README.md`
- `docs/architecture/ARCHITECTURE_RULES.md`
- `docs/architecture/DATASET_WRITE_SAFETY.md`
- `docs/architecture/STATE_AND_INCREMENTAL_MODEL.md`
- `tg_msg_manager/services/channel_export/workflows/full_export.py`
- `tg_msg_manager/services/channel_export/workflows/incremental_export.py`
- `tg_msg_manager/services/channel_export/workflows/context.py`
- `tg_msg_manager/services/channel_export/run_changelog.py`
- `tg_msg_manager/services/channel_export/models.py`
- `tg_msg_manager/services/channel_export/discussions/options.py`
- `tests/services/channel_export/test_channel_export_service.py`
- `tests/services/channel_export/test_channel_export_payload_writer.py`
- `tests/services/channel_export/test_channel_export_dataset_contracts.py`

May create:

- `tg_msg_manager/services/channel_export/run_summary.py`
- `tests/services/channel_export/test_channel_export_run_summary.py`
- `docs/stages/reports/STAGE_5B_2_CHANNEL_EXPORT_POST_BUFFER_BOUNDARIES_REPORT.md`

## 3. HARD PROHIBITIONS

- Do not change `messages.jsonl`, `messages.txt`, `media_manifest.jsonl`, `manifest.json`, `channel_export_state.json`, `discussion_*` formats, or `run_changelog.jsonl` schema.
- Do not change incremental ordering semantics.
- Do not change discussion export behavior.
- Do not add SQLite persistence for channel posts or comments.
- Do not add raw Telegram calls outside existing fetch/resolver layers.
- Do not add feature logic to `ChannelExportService`.
- Do not add analytics, classification, profiling, OSINT, OCR, STT, media recognition, or LLM logic.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Add a focused run-summary helper that records only:
   - new message ids;
   - first/last message id;
   - first/last message timestamp;
   - message count.
2. Keep `ChannelRunChangelogWriter.append_entry()` backward-compatible with current `posts` input.
3. Add a summary-based path for no-discussion full exports so full `ChannelPostRecord` objects are not retained only for changelog.
4. Leave discussion modes that require post records unchanged unless a focused test proves behavior and ordering are preserved.
5. Add tests proving run changelog output is byte/field equivalent for the no-discussion full-export path.
6. If preserving behavior requires retaining full records in a path, stop and report that path as out of scope instead of forcing a change.

## 5. REQUIRED DOCS

No user docs are required if dataset/run-changelog schemas and CLI behavior are unchanged.

Create:

- `docs/stages/reports/STAGE_5B_2_CHANNEL_EXPORT_POST_BUFFER_BOUNDARIES_REPORT.md`

Update architecture docs only if a new helper becomes part of the documented channel export organization.

## 6. TESTS / VERIFICATION

Run:

- `pytest tests/services/channel_export/test_channel_export_run_summary.py tests/services/channel_export/test_channel_export_service.py`
- `pytest tests/services/channel_export/test_channel_export_dataset_contracts.py`
- `python3 -m compileall tg_msg_manager`
- `ruff check tg_msg_manager tests`

If no new run-summary test file is created, explain why in the report.

## 7. REPORT

Report in Russian:

- exact buffering path reduced;
- paths intentionally left unchanged;
- schema/format preservation evidence;
- tests/checks run;
- `stage-reviewer` and `architecture-guard` application.

## 8. COMPLETION CRITERIA

- No-discussion full channel export no longer retains full post records solely for run changelog.
- Run changelog schema remains unchanged.
- Dataset/state/manifest behavior is preserved.
- Required tests pass or unrelated blockers are documented.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md` final structure, be in Russian, and stay under 1200 characters.
