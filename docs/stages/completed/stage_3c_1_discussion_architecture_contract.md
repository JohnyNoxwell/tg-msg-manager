# STAGE 3C.1 — DISCUSSION ARCHITECTURE CONTRACT

Status: completed
Stage: 3C.1
Scope: historical task instructions

## 0. CODEX ENTRY PROMPT

```text
Read AGENTS.md first.

Then read this file completely before editing anything.

You are working on tg-msg-manager.

This task is part of Stage 3C — Channel Discussion Context Export.

Follow the scope exactly. Do not implement later Stage 3C parts unless this file explicitly allows it.

When in doubt, preserve existing behavior and stop at the boundary defined in this file.
```

---

## 1. GLOBAL ARCHITECTURAL DECISION

Stage 3C is an export/dataset-layer extension only.

```text
Stage 3C does not write discussion data into SQLite.
Stage 3C does not change SQLite schema.
Stage 3C does not change existing export/db-export/export-pm behavior.
Stage 3C does not add analytics.
Stage 3C does not add OSINT interpretation.
Stage 3C does not add OCR, speech-to-text, image/video/audio analysis.
```

Discussion data must be represented as files inside the channel export dataset, not as database records.

Target dataset direction:

```text
exports/channels/<channel_slug>/
  manifest.json
  messages.jsonl
  messages.txt
  media_manifest.jsonl
  channel_export_state.json
  media/

  discussion_comments.jsonl
  discussion_comments.txt
  discussion_threads.jsonl
  discussion_export_state.json
```

The exact files are introduced gradually across Stage 3C sub-stages. Do not create files outside the current task scope.

---

## 2. HARD PROHIBITIONS

Do not implement:

```text
- SQLite schema changes
- DB persistence for discussion comments
- migrations
- discussion/comment analytics
- sentiment analysis
- bot detection
- user profiling
- influence scoring
- narrative classification
- OCR
- image/video analysis
- speech-to-text
- media full download for discussion comments
- reply-tree reconstruction beyond preserving reply_to_id
- refresh/backfill of old discussion threads outside current-run posts
- Stage 3D
- Stage 4
- GUI/dashboard/SaaS features
```

Do not add feature logic to protected hot-path files:

```text
tg_msg_manager/services/export/service.py
tg_msg_manager/services/db_export/service.py
tg_msg_manager/services/private_archive/service.py
tg_msg_manager/services/context/engine.py
```

Do not bloat:

```text
tg_msg_manager/services/channel_export/service.py
```

`ChannelExportService` may orchestrate only. Any discussion-specific logic must live under:

```text
tg_msg_manager/services/channel_export/discussions/
```

---


## 3. PURPOSE

This file defines Stage 3C architecture before runtime implementation starts.

This task is mostly documentation and boundary-locking.

Expected result:

```text
docs/refactor/STAGE_3C_CHANNEL_DISCUSSION_CONTEXT_EXPORT_DESIGN.md
```

No runtime discussion export should be implemented in this stage.

---

## 4. STAGE 3C TARGET BEHAVIOR

Stage 3C will eventually allow:

```bash
python3 -m tg_msg_manager.cli export-channel \
  --channel @example \
  --limit 100 \
  --media metadata \
  --discussion full \
  --max-comments-per-post 100
```

Default must remain:

```text
--discussion none
```

Expected meaning:

```text
discussion none:
  do not resolve discussion source
  do not fetch comments
  do not write discussion files
  preserve current export-channel behavior

discussion full:
  for channel posts exported in the current run,
  attempt to export linked discussion comments into dataset files
```

Important current-run rule:

```text
Full/force export:
  discussions are exported for posts fetched in that full/force run.

Incremental export:
  discussions are exported only for newly fetched channel posts.

No-new-posts incremental run:
  do not refetch old discussions.
```

Accepted limitation:

```text
Stage 3C does not refresh comments under previously exported posts unless --force causes those posts to be exported again.
```

---

## 5. TARGET COMPONENT BOUNDARIES

Stage 3C discussion logic must be isolated under:

```text
tg_msg_manager/services/channel_export/discussions/
```

Target future components:

```text
discussions/
  __init__.py
  errors.py
  models.py
  options.py
  resolver.py
  fetcher.py
  mapper.py
  jsonl_renderer.py
  txt_renderer.py
  payload_writer.py
  state_manager.py
  exporter.py
```

Not every file must be created in 3C.1. This is target architecture.

Responsibilities:

```text
models.py:
  discussion dataclasses only

options.py:
  discussion mode constants and validation

resolver.py:
  resolve linked discussion group/source

fetcher.py:
  fetch comments for a specific channel post/thread

mapper.py:
  map Telegram/message objects into discussion records

jsonl_renderer.py:
  render discussion comments/threads to JSONL

txt_renderer.py:
  render discussion comments to human-readable TXT

payload_writer.py:
  write discussion_comments.jsonl, discussion_comments.txt, discussion_threads.jsonl

state_manager.py:
  read/write discussion_export_state.json

exporter.py:
  orchestrate discussion export for current-run channel posts
```

`ChannelExportService` must only call something like:

```python
discussion_result = await self.discussion_exporter.export_for_posts(...)
```

It must not fetch/map/write discussion comments directly.

---

## 6. DATA CONTRACT DIRECTION

### 6.1. discussion_threads.jsonl

Target record:

```json
{
  "channel_id": 111,
  "channel_username": "example",
  "channel_message_id": 5001,
  "discussion_chat_id": 222,
  "discussion_root_message_id": 98765,
  "comments_count": 42,
  "exported_comments_count": 40,
  "status": "exported",
  "error": null
}
```

Allowed thread statuses:

```text
not_available
not_linked
no_comments
exported
partial
failed
```

### 6.2. discussion_comments.jsonl

Target record:

```json
{
  "message_id": 98770,
  "discussion_chat_id": 222,
  "channel_id": 111,
  "channel_message_id": 5001,
  "discussion_root_message_id": 98765,
  "author_id": 123,
  "author_name": "User",
  "username": "user",
  "timestamp": "2026-05-08T12:00:00+00:00",
  "text": "comment text",
  "reply_to_id": 98765,
  "media": [],
  "reactions": {},
  "raw_payload": {}
}
```

### 6.3. discussion_export_state.json

Target direction:

```json
{
  "schema_version": "1.0",
  "channel_id": 111,
  "discussion_chat_id": 222,
  "last_run_at": "2026-05-08T12:00:00+00:00",
  "thread_count_total": 10,
  "comment_count_total": 237,
  "failed_thread_count_total": 1,
  "last_run_status": "completed"
}
```

State should be separate from `channel_export_state.json`.

---

## 7. TASKS

### A. Inspect baseline

- [ ] Read `AGENTS.md`.
- [ ] Read `docs/refactor/STAGE_3B_MEDIA_DOWNLOAD_HARDENING_REPORT.md`.
- [ ] Read `docs/refactor/STAGE_3B_1_CHANNEL_EXPORT_STABILIZATION_REPORT.md`.
- [ ] Inspect `tg_msg_manager/services/channel_export/`.
- [ ] Inspect `tg_msg_manager/services/channel_export/service.py`.
- [ ] Inspect `tg_msg_manager/services/channel_export/media_processor.py`.
- [ ] Inspect `tg_msg_manager/services/channel_export/models.py`.
- [ ] Inspect `tg_msg_manager/cli_parser.py`.
- [ ] Inspect `tg_msg_manager/cli_commands.py`.
- [ ] Inspect `tests/test_channel_export_*.py`.

### B. Create architecture design note

Create:

```text
docs/refactor/STAGE_3C_CHANNEL_DISCUSSION_CONTEXT_EXPORT_DESIGN.md
```

The design note must include:

- [ ] Purpose.
- [ ] Out-of-scope list.
- [ ] Explicit no-SQLite decision.
- [ ] Explicit no-analytics decision.
- [ ] Target CLI contract.
- [ ] Target dataset files.
- [ ] Target models.
- [ ] Target component boundaries.
- [ ] Current-run-only discussion export rule.
- [ ] Incremental behavior.
- [ ] Force behavior.
- [ ] No-new-posts behavior.
- [ ] Accepted limitations.
- [ ] Stage split:
  - [ ] 3C.1 architecture contract
  - [ ] 3C.2 resolver/models
  - [ ] 3C.3 fetch/writers
  - [ ] 3C.4 integration/tests/docs

### C. Guard against premature implementation

- [ ] Do not add CLI args yet unless this repo already has an established docs-first pattern that requires command docs.
- [ ] Do not add discussion runtime modules yet.
- [ ] Do not fetch Telegram discussion data.
- [ ] Do not write discussion JSONL/TXT files.
- [ ] Do not modify `ChannelExportService`.
- [ ] Do not modify SQLite.
- [ ] Do not modify old export commands.

### D. Optional documentation touch

Only if useful:

- [ ] Add a short roadmap note to `CHANGELOG.md`.
- [ ] Add a short future-stage note to `README.md`.

Do not claim Stage 3C is implemented.

---

## 8. TESTING

Usually no runtime tests are required for 3C.1 if only docs are changed.

If any code changes are made, run:

```bash
pytest tests/test_channel_export_*.py
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
ruff format --check tg_msg_manager tests
```

---

## 9. COMPLETION CRITERIA

Complete only if:

- [ ] Design note exists.
- [ ] Design note explicitly prohibits SQLite changes.
- [ ] Design note explicitly says discussion export is dataset-layer only.
- [ ] Design note explicitly says default discussion mode will be `none`.
- [ ] Design note explicitly says old thread refresh/backfill is out of scope.
- [ ] No Stage 3C runtime implementation was added.
- [ ] No existing export behavior was changed.
- [ ] No SQLite files/schema/migrations were changed.

---

## 10. FINAL RESPONSE FORMAT

```text
## Summary
- design note created
- no runtime implementation added
- Stage 3C boundaries locked

## Files changed
- path

## Tests
- command/result or "not run; docs-only"

## Status
Stage 3C.1: complete / partial / blocked
Stage 3C runtime: not started
```
