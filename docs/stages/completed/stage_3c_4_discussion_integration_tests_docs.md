# STAGE 3C.4 — DISCUSSION INTEGRATION, TESTS, DOCS

Status: completed
Stage: 3C.4
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

This stage integrates the isolated discussion export layer into `export-channel`.

This stage closes Stage 3C.

Expected result:

```text
export-channel --discussion full --max-comments-per-post N
```

writes discussion dataset files for channel posts exported in the current run.

---

## 4. PRECONDITIONS

Stage 3C.1 should provide architecture design.

Stage 3C.2 should provide:

```text
discussion options
discussion models
discussion resolver
CLI flags
```

Stage 3C.3 should provide:

```text
discussion fetcher
discussion mapper
discussion renderers
discussion payload writer
discussion state manager
discussion exporter
```

If these are missing, stop and report.

---

## 5. INTEGRATION RULE

`ChannelExportService` must not directly implement discussion internals.

Allowed service-level shape:

```python
if options.discussion_mode == "full":
    discussion_result = await self.discussion_exporter.export_for_posts(...)
```

Forbidden inside `ChannelExportService`:

```text
- direct comment fetching
- direct discussion group API calls
- direct comment mapping
- direct discussion JSON rendering
- direct discussion file writing
- discussion analytics
```

---

## 6. EXPECTED USER-FACING BEHAVIOR

Default behavior:

```bash
python3 -m tg_msg_manager.cli export-channel --channel @example --limit 10
```

Expected:

```text
discussion mode = none
no discussion resolver call
no discussion files
existing channel export behavior preserved
```

Explicit discussion export:

```bash
python3 -m tg_msg_manager.cli export-channel \
  --channel @example \
  --limit 10 \
  --discussion full \
  --max-comments-per-post 100
```

Expected files:

```text
discussion_comments.jsonl
discussion_comments.txt
discussion_threads.jsonl
discussion_export_state.json
```

Expected manifest:

```json
{
  "discussion": {
    "mode": "full",
    "discussion_chat_id": 123,
    "thread_count": 10,
    "comment_count": 237,
    "failed_thread_count": 1,
    "max_comments_per_post": 100,
    "included_files": [
      "discussion_comments.jsonl",
      "discussion_comments.txt",
      "discussion_threads.jsonl",
      "discussion_export_state.json"
    ]
  }
}
```

If discussion disabled:

```json
{
  "discussion": {
    "mode": "none"
  }
}
```

Or omit the block if that is more consistent with current manifest style. Choose one and test it. Prefer explicit block.

---

## 7. CURRENT-RUN RULE

Discussion export must operate only on posts exported in the current run.

Required behavior:

```text
full run:
  export discussions for all posts fetched in this run

force run:
  overwrite channel payload and discussion payload;
  export discussions for all posts fetched in this run

incremental run:
  export discussions only for newly fetched posts

no-new-posts incremental:
  do not refetch old discussions
  do not rewrite discussion files
  do not mutate discussion state
```

Do not implement:

```text
refresh discussions for old posts
backfill discussions for old metadata-only datasets
separate discussion refresh command
```

---

## 8. STATE SAFETY

Expected ordering:

```text
1. fetch/map/prepare channel posts
2. write channel payload
3. export/write discussion payload for current-run posts if enabled
4. build manifest
5. write manifest
6. save channel state
7. save discussion state
8. return result
```

Alternative ordering is acceptable only if tests prove state is not advanced after critical failures.

Critical rule:

```text
Do not advance state if manifest write fails.
```

Discussion per-thread failure is non-critical:

```text
one failed discussion thread does not fail whole export
```

Critical writer corruption may fail the export:

```text
discussion payload writer failure may fail export
but state must not advance incorrectly
```

---

## 9. MANIFEST INTEGRATION

Update main manifest builder to include discussion summary.

Fields:

```text
mode
discussion_chat_id
thread_count
comment_count
failed_thread_count
max_comments_per_post
included_files
```

Optional fields:

```text
partial_thread_count
not_linked_thread_count
not_available_thread_count
no_comments_thread_count
```

Do not remove existing manifest fields.

Do not change existing media fields.

---

## 10. RESULT MODEL / CLI SUMMARY

Update result model if needed to include discussion result.

CLI summary should print, when discussion enabled:

```text
Discussion mode: full
Discussion threads this run: N
Discussion comments this run: N
Failed discussion threads this run: N
Discussion comments: <path>
Discussion threads: <path>
Discussion state: <path>
```

When discussion disabled:

- [ ] avoid noisy output, or print only `Discussion mode: none`.
- [ ] do not imply comments were exported.

---

## 11. PLAN BUILDER

If not already done, add discussion paths to export plan:

```text
discussion_comments_jsonl_path
discussion_comments_txt_path
discussion_threads_jsonl_path
discussion_state_path
```

Paths must be inside the same channel export output directory.

Do not create separate global discussion export directory.

---

## 12. EVENTS / PROGRESS

Add discussion events only if the existing event system makes this clean.

Possible events:

```text
channel_export.discussion_started
channel_export.discussion_progress
channel_export.discussion_thread_failed
channel_export.discussion_completed
```

Do not overbuild progress if tests/docs become too heavy.

At minimum, CLI final summary must show discussion counts.

---

## 13. INTEGRATION TESTS

Add or extend:

```text
tests/test_channel_export_service.py
tests/test_channel_export_manifest.py
tests/test_channel_export_cli.py
tests/test_channel_export_discussion_*.py
```

Required tests:

### A. Defaults

- [ ] default discussion mode is `none`.
- [ ] default export does not call discussion resolver/exporter.
- [ ] default export does not create discussion files.
- [ ] old channel export tests still pass.

### B. Full discussion mode

- [ ] `--discussion full` triggers discussion exporter.
- [ ] discussion comments file is written.
- [ ] discussion threads file is written.
- [ ] discussion state file is written.
- [ ] manifest has discussion summary.
- [ ] CLI result includes discussion summary.

### C. Incremental behavior

- [ ] first full run exports discussions for fetched posts.
- [ ] second incremental run exports discussions only for new posts.
- [ ] no-new-posts run does not refetch old discussions.
- [ ] no-new-posts run does not mutate discussion state.

### D. Force behavior

- [ ] `--force --discussion full` overwrites discussion files.
- [ ] force does not append duplicate discussion comments.
- [ ] force rebuilds discussion state totals.

### E. Failure behavior

- [ ] failed thread is recorded.
- [ ] failed thread does not fail whole export.
- [ ] discussion payload writer failure does not advance state incorrectly.
- [ ] manifest write failure does not advance channel or discussion state.

### F. Scope guards

- [ ] no SQLite schema files changed.
- [ ] no legacy commands changed.
- [ ] no analytics output exists.
- [ ] no discussion media download occurs.

---

## 14. DOCUMENTATION TASKS

Update:

```text
README.md
COMMANDS.md
docs/testing/LIVE_SMOKE_CHECKLIST.md
CHANGELOG.md
```

Documentation must include:

- [ ] `--discussion none|full`.
- [ ] default `none`.
- [ ] `--max-comments-per-post`.
- [ ] generated files.
- [ ] current-run-only behavior.
- [ ] incremental limitation.
- [ ] no SQLite persistence.
- [ ] no analytics.
- [ ] no comment media full download.
- [ ] smoke command with small limit.

Smoke example:

```bash
python3 -m tg_msg_manager.cli export-channel \
  --channel "$TEST_CHANNEL" \
  --limit 3 \
  --media metadata \
  --discussion full \
  --max-comments-per-post 20
```

Expected:

```text
exit code 0
discussion files exist
manifest has discussion block
failed thread count is recorded if some threads fail
no SQLite migration required
```

---

## 15. FINAL REPORT

Create:

```text
docs/refactor/STAGE_3C_CHANNEL_DISCUSSION_CONTEXT_EXPORT_REPORT.md
```

Report must include:

```text
1. Summary
2. Scope
3. Architecture
4. CLI contract
5. Dataset files
6. State behavior
7. Incremental behavior
8. Failure behavior
9. Tests
10. Verification results
11. Known limitations
12. Explicit statement: no SQLite changes
13. Explicit statement: no analytics
14. Explicit statement: Stage 3D not started
```

Known limitations should include:

```text
- no DB persistence
- no old-thread refresh/backfill without --force
- no full media download for discussion comments
- no reply-tree reconstruction
- Telegram linked discussion edge cases may depend on channel configuration
```

---

## 16. VERIFICATION COMMANDS

Run:

```bash
pytest tests/test_channel_export_discussion_*.py
pytest tests/test_channel_export_*.py
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
ruff format --check tg_msg_manager tests
make test
make verify
python3 -m tg_msg_manager.cli export-channel --help
```

Do not claim verification passed unless actually run.

---

## 17. COMPLETION CRITERIA

Complete only if:

- [ ] `--discussion none|full` works.
- [ ] default remains `none`.
- [ ] `--max-comments-per-post` works.
- [ ] discussion export writes expected files.
- [ ] manifest includes discussion summary.
- [ ] discussion state is written.
- [ ] incremental behavior uses current-run posts only.
- [ ] no-new-posts does not refetch old discussions.
- [ ] force rewrites discussion files.
- [ ] one failed thread does not fail whole export.
- [ ] state does not advance on critical manifest failure.
- [ ] no SQLite schema changes.
- [ ] no analytics.
- [ ] no discussion media full download.
- [ ] docs updated.
- [ ] final report created.
- [ ] verification commands run and reported.

---

## 18. FINAL RESPONSE FORMAT

```text
## Summary
- Stage 3C integrated into export-channel
- discussion export is explicit
- dataset files added
- no SQLite changes

## Files changed
- path
- path

## Behavior preserved
- default discussion none
- existing channel export unchanged unless --discussion full
- no legacy command changes
- no analytics
- no discussion media download

## Tests
- command: result
- command: result

## Known limitations
- no DB persistence
- no old-thread refresh without --force
- no full media download for discussion comments
- no reply-tree reconstruction

## Stage status
Stage 3C: complete / partial / blocked
Stage 3D: not started
```
