# STAGE 3C.3 — DISCUSSION FETCH AND WRITERS

Status: completed
Stage: 3C.3
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

This stage implements isolated discussion fetching, mapping, and dataset writers.

It must produce discussion dataset records, but integration into the main `export-channel` pipeline should remain minimal and controlled.

Do not bloat `ChannelExportService`.

---

## 4. PRECONDITIONS

Stage 3C.2 should already provide:

```text
discussions/options.py
discussions/models.py
discussions/resolver.py
discussion CLI options
discussion mode default none
```

Before editing:

- [ ] Confirm Stage 3C.2 files exist.
- [ ] Confirm CLI flags exist.
- [ ] Confirm discussion models exist.
- [ ] Confirm no SQLite changes exist.
- [ ] Confirm Stage 3C design note exists.

If Stage 3C.2 is incomplete, stop and report.

---

## 5. ALLOWED SCOPE

Allowed files:

```text
tg_msg_manager/services/channel_export/discussions/
tests/test_channel_export_discussion_*.py
docs/refactor/
```

Allowed minimal modifications:

```text
tg_msg_manager/services/channel_export/plan_builder.py
tg_msg_manager/services/channel_export/models.py
```

Only if needed to add discussion output paths to the export plan.

Avoid modifying:

```text
tg_msg_manager/services/channel_export/service.py
tg_msg_manager/cli_commands.py
tg_msg_manager/cli_io.py
```

Those are mainly for Stage 3C.4.

---

## 6. TARGET NEW FILES

Create if not present:

```text
tg_msg_manager/services/channel_export/discussions/fetcher.py
tg_msg_manager/services/channel_export/discussions/mapper.py
tg_msg_manager/services/channel_export/discussions/jsonl_renderer.py
tg_msg_manager/services/channel_export/discussions/txt_renderer.py
tg_msg_manager/services/channel_export/discussions/payload_writer.py
tg_msg_manager/services/channel_export/discussions/state_manager.py
tg_msg_manager/services/channel_export/discussions/exporter.py
```

The `exporter.py` may remain isolated and callable from tests. Full service integration is Stage 3C.4.

---

## 7. OUTPUT FILE CONTRACT

Target files:

```text
discussion_comments.jsonl
discussion_comments.txt
discussion_threads.jsonl
discussion_export_state.json
```

If adding paths to `ChannelExportPlan`, use names like:

```text
discussion_comments_jsonl_path
discussion_comments_txt_path
discussion_threads_jsonl_path
discussion_state_path
```

Do not alter existing output file names:

```text
messages.jsonl
messages.txt
media_manifest.jsonl
manifest.json
channel_export_state.json
```

---

## 8. FETCHER CONTRACT

Create:

```python
class ChannelDiscussionFetcher:
    async def iter_comments_for_post(...):
        ...
```

Input should be explicit:

```text
discussion_entity
channel_post_record
max_comments_per_post
```

Expected behavior:

- [ ] Fetch comments for one channel post/thread only.
- [ ] Respect `max_comments_per_post`.
- [ ] Yield comments in stable chronological order if possible.
- [ ] Do not fetch all discussion group history.
- [ ] Do not fetch comments for posts outside current run.
- [ ] Do not throw for normal no-comments case.
- [ ] Unexpected errors should be isolated per thread.

Important:

```text
Telegram discussion mapping can be tricky.
Keep API assumptions isolated inside fetcher/resolver.
Make fake-client testing easy.
```

If exact Telegram API behavior is uncertain, implement a conservative adapter boundary and cover it with fake objects.

---

## 9. THREAD RESOLUTION CONTRACT

For each current-run channel post, create one thread record.

Thread status rules:

```text
not_available:
  discussion mode full requested, but discussion source cannot be resolved due platform/API limitations

not_linked:
  channel has no linked discussion group

no_comments:
  linked discussion exists, but post has no comments/thread

exported:
  comments were exported and count is within limit

partial:
  comments were exported but limited by max_comments_per_post or fetcher indicates more comments exist

failed:
  this post/thread failed, but whole export continues
```

Atomic tasks:

- [ ] Implement status constants.
- [ ] Ensure one failed thread does not fail entire discussion export.
- [ ] Ensure thread errors are stored in thread record.
- [ ] Ensure failed thread can still be written to `discussion_threads.jsonl`.
- [ ] Ensure no comments are written for failed thread unless partial records are safely available.

---

## 10. MAPPER CONTRACT

Create:

```python
class ChannelDiscussionMapper:
    def map_comment(...):
        ...
```

Map fields:

```text
message_id
discussion_chat_id
channel_id
channel_message_id
discussion_root_message_id
author_id
author_name
username
timestamp
text
reply_to_id
media
reactions
raw_payload
```

Rules:

- [ ] Preserve `reply_to_id`.
- [ ] Do not build reply tree.
- [ ] Do not infer user identity.
- [ ] Do not profile users.
- [ ] Media should be metadata only or empty.
- [ ] raw_payload must be JSON-safe or rendered safely by renderer.
- [ ] Missing author data must not crash mapping.
- [ ] Service messages should be handled consistently with existing message behavior.

---

## 11. RENDERER CONTRACT

### 11.1. JSONL renderer

Create renderers for:

```text
ChannelDiscussionCommentRecord
ChannelDiscussionThreadRecord
```

Requirements:

- [ ] one JSON object per line
- [ ] UTF-8
- [ ] ensure_ascii=False
- [ ] datetime as ISO string
- [ ] raw_payload JSON-safe
- [ ] stable field names

### 11.2. TXT renderer

Create human-readable discussion comments TXT.

Suggested block:

```text
[2026-05-08 12:00] Author (ID: 123, username: user):
Comment text
```

Include relation header per thread if useful:

```text
--- Channel post 5001 / discussion root 98765 ---
```

Requirements:

- [ ] readable
- [ ] stable
- [ ] no analytics
- [ ] no sentiment
- [ ] no inferred profile

---

## 12. PAYLOAD WRITER CONTRACT

Create:

```python
class ChannelDiscussionPayloadWriter
```

Responsibilities:

- [ ] open files in write or append mode.
- [ ] write comment records to `discussion_comments.jsonl`.
- [ ] write comment blocks to `discussion_comments.txt`.
- [ ] write thread records to `discussion_threads.jsonl`.
- [ ] return run stats.

Run stats:

```text
thread_count
comment_count
failed_thread_count
partial_thread_count
not_linked_thread_count
not_available_thread_count
no_comments_thread_count
```

Modes:

```text
full/force:
  overwrite discussion files

incremental:
  append discussion files
```

Do not manage `manifest.json` here.

Do not manage `channel_export_state.json` here.

---

## 13. DISCUSSION STATE MANAGER CONTRACT

Create:

```python
class ChannelDiscussionStateManager
```

Responsibilities:

- [ ] write `discussion_export_state.json`.
- [ ] read existing state if needed.
- [ ] build completed state from discussion run stats.
- [ ] keep state separate from `channel_export_state.json`.

State fields:

```text
schema_version
channel_id
discussion_chat_id
last_run_at
thread_count_total
comment_count_total
failed_thread_count_total
last_run_status
updated_at
```

Incremental behavior:

- [ ] add current run totals to previous state.
- [ ] force/full behavior may rebuild totals from current run.
- [ ] no-new-posts behavior should not change discussion state in Stage 3C.4.

---

## 14. ISOLATED EXPORTER CONTRACT

Create:

```python
class ChannelDiscussionExporter:
    async def export_for_posts(...):
        ...
```

Input:

```text
channel_identity
discussion_source
posts exported in current run
output paths / plan
discussion options
run mode
previous state if needed
```

Responsibilities:

- [ ] iterate current-run channel posts only.
- [ ] for each post, resolve/fetch discussion comments.
- [ ] map comments.
- [ ] write comments/threads.
- [ ] write discussion state.
- [ ] return discussion result.
- [ ] catch per-thread failures and continue.
- [ ] do not catch critical writer/state corruption silently.

Do not write main manifest in Stage 3C.3 unless already isolated and tested.

---

## 15. TEST TASKS

Create/extend tests:

```text
tests/test_channel_export_discussion_fetcher.py
tests/test_channel_export_discussion_mapper.py
tests/test_channel_export_discussion_renderers.py
tests/test_channel_export_discussion_payload_writer.py
tests/test_channel_export_discussion_state_manager.py
tests/test_channel_export_discussion_exporter.py
```

### A. Fetcher tests

- [ ] fetches comments for one post.
- [ ] respects max comments per post.
- [ ] does not fetch unrelated group history.
- [ ] no comments returns empty result.
- [ ] per-thread error can be represented as failed.

### B. Mapper tests

- [ ] maps author id/name/username.
- [ ] maps text.
- [ ] maps timestamp.
- [ ] maps reply_to_id.
- [ ] handles missing author.
- [ ] handles missing text.
- [ ] maps media as metadata/empty, no download.

### C. Renderer tests

- [ ] JSONL comment line valid JSON.
- [ ] JSONL thread line valid JSON.
- [ ] datetime rendered as ISO.
- [ ] raw_payload safe.
- [ ] TXT output includes timestamp/author/text.

### D. Payload writer tests

- [ ] writes comments JSONL.
- [ ] writes comments TXT.
- [ ] writes threads JSONL.
- [ ] overwrite mode replaces files.
- [ ] append mode appends files.
- [ ] stats count comments.
- [ ] stats count failed threads.

### E. State manager tests

- [ ] writes state JSON.
- [ ] loads state JSON.
- [ ] incremental totals are merged.
- [ ] force/full totals are rebuilt.
- [ ] corrupted state raises domain error.

### F. Exporter tests

- [ ] exports comments for current-run posts.
- [ ] failed thread does not fail whole export.
- [ ] no linked discussion writes thread statuses.
- [ ] max comments limit produces partial if appropriate.
- [ ] no SQLite touched.

---

## 16. DOCUMENTATION TASKS

Create report:

```text
docs/refactor/STAGE_3C_3_DISCUSSION_FETCH_AND_WRITERS_REPORT.md
```

Report must include:

```text
- summary
- files added
- behavior implemented
- tests added
- limitations
- explicit statement: not integrated into export-channel pipeline yet, unless minimal tested integration was required
- explicit statement: no SQLite changes
- explicit statement: no analytics
```

---

## 17. VERIFICATION COMMANDS

Run:

```bash
pytest tests/test_channel_export_discussion_*.py
pytest tests/test_channel_export_*.py
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
ruff format --check tg_msg_manager tests
```

Do not claim passed unless actually run.

---

## 18. COMPLETION CRITERIA

Complete only if:

- [ ] fetcher exists.
- [ ] mapper exists.
- [ ] renderers exist.
- [ ] payload writer exists.
- [ ] discussion state manager exists.
- [ ] isolated exporter exists.
- [ ] discussion files can be written in tests.
- [ ] per-thread failure does not fail whole discussion export.
- [ ] max comments limit is enforced.
- [ ] no SQLite changes.
- [ ] no analytics.
- [ ] no comment media download.
- [ ] main `export-channel` behavior remains stable.
- [ ] Stage 3C.4 integration is not prematurely completed unless explicitly documented and tested.

---

## 19. FINAL RESPONSE FORMAT

```text
## Summary
- discussion fetch/map/write layer added
- isolated exporter added
- no SQLite changes

## Files changed
- path
- path

## Tests
- command: result

## Behavior preserved
- existing export-channel unchanged unless explicitly noted
- no legacy command changes
- no analytics
- no discussion media download

## Known limitations
- not fully integrated into CLI/service until Stage 3C.4
- old discussions not refreshed

## Stage status
Stage 3C.3: complete / partial / blocked
Stage 3C.4: not started
```
