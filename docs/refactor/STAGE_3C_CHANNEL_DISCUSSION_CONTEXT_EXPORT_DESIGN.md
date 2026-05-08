# Stage 3C — Channel Discussion Context Export Design

## Purpose

Stage 3C adds optional linked discussion/comment export to the direct channel export dataset.

This is an export/dataset-layer extension only. Discussion comments are represented as files inside the channel export directory. They are not normalized into application storage and they do not participate in analytics, reporting, sync, DB export, or private archive behavior.

The goal is to preserve current `export-channel` behavior by default while allowing an explicit opt-in dataset export for comments linked to channel posts fetched in the current run.

## Out Of Scope

Stage 3C must not implement:

- SQLite schema changes.
- SQLite migrations.
- DB persistence for discussion comments.
- Changes to existing `export`, `db-export`, or `export-pm` behavior.
- Analytics or OSINT interpretation.
- Sentiment analysis.
- Bot detection.
- User profiling.
- Influence scoring.
- Narrative classification.
- OCR.
- Image, video, or audio analysis.
- Speech-to-text.
- Full media download for discussion comments.
- Reply-tree reconstruction beyond preserving `reply_to_id`.
- Refresh or backfill of old discussion threads outside the explicit current-run/force behavior.
- Stage 3D or Stage 4 functionality.
- GUI, dashboard, SaaS, or external service features.

## Storage Decision

Discussion export is dataset-layer only.

Stage 3C does not write discussion comments, discussion threads, or discussion state into SQLite. It does not change the SQLite schema, add migrations, or add storage contracts for persisted discussion data.

The discussion state file is separate from SQLite and separate from `channel_export_state.json`.

## Analytics Decision

Stage 3C does not add analytics.

Discussion files may contain exported records and counts needed to describe export completion, but they must not perform interpretation, classification, scoring, profile building, bot detection, influence detection, sentiment analysis, or narrative analysis.

## Target CLI Contract

Target command:

```bash
python3 -m tg_msg_manager.cli export-channel \
  --channel @example \
  --limit 100 \
  --media metadata \
  --discussion full \
  --max-comments-per-post 100
```

Target discussion options:

- `--discussion none`
- `--discussion full`
- `--max-comments-per-post N`

Default behavior must remain:

```text
--discussion none
```

`discussion none` means:

- Do not resolve a linked discussion source.
- Do not fetch discussion comments.
- Do not write discussion files.
- Preserve current `export-channel` behavior.

`discussion full` means:

- For channel posts exported in the current run, attempt to resolve linked discussion threads.
- Export linked discussion comments into dataset files.
- Preserve comment `reply_to_id` without reconstructing a reply tree.
- Export discussion media metadata only, without downloading full media files.

## Target Dataset Files

Target channel export directory:

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

Discussion files are written only when `--discussion full` is explicitly selected and applicable posts are exported in the current run.

No discussion files are written for the default `--discussion none` mode.

## Target Models

Target discussion models live under:

```text
tg_msg_manager/services/channel_export/discussions/models.py
```

Expected model groups:

- Discussion export options.
- Linked discussion source/thread resolution result.
- Discussion comment record.
- Discussion thread record.
- Discussion export run statistics.
- Discussion export state.
- Discussion export result.

Target `discussion_threads.jsonl` fields:

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

Target `discussion_comments.jsonl` fields:

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

Target `discussion_export_state.json` fields:

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

## Component Boundaries

Discussion logic must be isolated under:

```text
tg_msg_manager/services/channel_export/discussions/
```

Target components:

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

Responsibilities:

- `models.py`: discussion dataclasses only.
- `options.py`: discussion mode constants and validation.
- `resolver.py`: resolve linked discussion group/source and post thread roots.
- `fetcher.py`: fetch comments for one channel post/thread.
- `mapper.py`: map Telegram/message objects into discussion records.
- `jsonl_renderer.py`: render discussion comments and threads to JSONL.
- `txt_renderer.py`: render discussion comments to human-readable TXT.
- `payload_writer.py`: write `discussion_comments.jsonl`, `discussion_comments.txt`, and `discussion_threads.jsonl`.
- `state_manager.py`: read/write `discussion_export_state.json`.
- `exporter.py`: orchestrate discussion export for current-run channel posts.

`ChannelExportService` may only orchestrate discussion export by delegating to an isolated discussion exporter, for example:

```python
discussion_result = await self.discussion_exporter.export_for_posts(...)
```

`ChannelExportService` must not fetch, map, render, or write discussion comments directly.

No discussion feature logic may be added to protected hot-path services:

- `tg_msg_manager/services/export/service.py`
- `tg_msg_manager/services/db_export/service.py`
- `tg_msg_manager/services/private_archive/service.py`
- `tg_msg_manager/services/context/engine.py`

## Current-Run Rule

Discussion export operates only on channel posts fetched/exported in the current run.

It must not refresh, refetch, or backfill discussion threads for posts that were exported in earlier runs unless those posts are exported again through the explicit force behavior.

## Incremental Behavior

Incremental `export-channel` runs export discussion data only for newly fetched channel posts.

If an incremental run finds no new posts, discussion resolution and comment fetch must not run, discussion files must not be written, and `discussion_export_state.json` must not be mutated.

## Force Behavior

Force export is treated as a fresh full channel export for the selected run scope.

When `--discussion full` and `--force` are used together, discussion files are overwritten and discussion export runs for posts fetched in that force run.

## Full Export Behavior

Full export writes discussion files only when `--discussion full` is explicitly selected.

Full export with `--discussion none` must behave like current channel export and must not resolve discussion sources.

## No-New-Posts Behavior

A no-new-posts incremental run must not:

- Resolve linked discussion sources.
- Fetch old discussion comments.
- Rewrite discussion dataset files.
- Mutate `discussion_export_state.json`.

The existing channel manifest may still be refreshed according to current channel export behavior, but discussion state must not be refreshed in that path.

## Accepted Limitations

- Discussion comments are not persisted to SQLite.
- Old discussion threads are not refreshed without `--force`.
- Discussion media is metadata-only; full media download for comments is out of scope.
- Reply-tree reconstruction is out of scope beyond preserving `reply_to_id`.
- Telegram linked discussion behavior may depend on channel configuration.
- Comments unavailable through Telegram API permissions/configuration are represented as thread statuses or failures, not as storage records.

## Stage Split

Stage 3C.1: architecture contract.

- Create this design note.
- Lock boundaries.
- Do not implement runtime discussion export.
- Do not add CLI flags unless a docs-first pattern requires it.

Stage 3C.2: resolver and models.

- Add discussion options.
- Add discussion models.
- Add resolver skeleton.
- Add CLI flags with default `--discussion none`.
- Do not fetch comments.
- Do not write discussion files.

Stage 3C.3: fetch and writers.

- Add isolated discussion fetcher.
- Add mapper.
- Add JSONL/TXT renderers.
- Add payload writer.
- Add discussion state manager.
- Add isolated discussion exporter.
- Add focused tests proving discussion records can be fetched, mapped, and written.
- Do not fully integrate with `export-channel` unless the stage file explicitly requires it.

Stage 3C.4: integration, tests, and docs.

- Integrate discussion export into `export-channel`.
- Write discussion dataset files for `--discussion full`.
- Include discussion summary in `manifest.json`.
- Write `discussion_export_state.json`.
- Include discussion counts in CLI summary.
- Test incremental, force, and no-new-posts behavior.
- Update README, COMMANDS, live smoke checklist, changelog, and final report.
