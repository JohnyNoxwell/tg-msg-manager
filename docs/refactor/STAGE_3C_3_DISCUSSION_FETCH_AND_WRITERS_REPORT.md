# Stage 3C.3 — Discussion Fetch And Writers Report

## Summary

Stage 3C.3 added the isolated discussion fetch/map/write layer under:

```text
tg_msg_manager/services/channel_export/discussions/
```

Implemented:

- `ChannelDiscussionFetcher`
- `ChannelDiscussionMapper`
- `ChannelDiscussionJsonlRenderer`
- `ChannelDiscussionTxtRenderer`
- `ChannelDiscussionPayloadWriter`
- `ChannelDiscussionStateManager`
- `ChannelDiscussionExporter`
- Discussion output paths in `ChannelExportPlan`

## Files Added

- `tg_msg_manager/services/channel_export/discussions/fetcher.py`
- `tg_msg_manager/services/channel_export/discussions/mapper.py`
- `tg_msg_manager/services/channel_export/discussions/jsonl_renderer.py`
- `tg_msg_manager/services/channel_export/discussions/txt_renderer.py`
- `tg_msg_manager/services/channel_export/discussions/payload_writer.py`
- `tg_msg_manager/services/channel_export/discussions/state_manager.py`
- `tg_msg_manager/services/channel_export/discussions/exporter.py`
- `tests/test_channel_export_discussion_fetcher.py`
- `tests/test_channel_export_discussion_mapper.py`
- `tests/test_channel_export_discussion_renderers.py`
- `tests/test_channel_export_discussion_payload_writer.py`
- `tests/test_channel_export_discussion_state_manager.py`
- `tests/test_channel_export_discussion_exporter.py`

## Behavior Implemented

- Comments can be fetched for one current-run channel post through an isolated fetcher boundary.
- `max_comments_per_post` is enforced.
- Fetch results preserve per-thread errors without failing the entire discussion export.
- Comments are mapped to dataset records with `reply_to_id` preserved.
- Discussion media remains metadata-only; no full media download is performed.
- JSONL/TXT renderers produce deterministic dataset output.
- Payload writer writes:
  - `discussion_comments.jsonl`
  - `discussion_comments.txt`
  - `discussion_threads.jsonl`
- State manager writes and reads `discussion_export_state.json`.
- Isolated exporter can write discussion files for supplied current-run posts.

## Integration Status

This stage is not fully integrated into the main `export-channel` pipeline.

`ChannelExportService`, CLI output summaries, manifest discussion summary, and no-new-posts discussion behavior remain Stage 3C.4 work.

## Tests Added

Added focused tests for:

- Fetching current-post comments.
- Fetch limit behavior.
- Mapper field preservation.
- JSONL/TXT rendering.
- Payload writer overwrite/append behavior.
- State read/write and incremental merge behavior.
- Isolated exporter success, partial, failed-thread, and not-linked behavior.

## Verification

Commands run:

- `pytest tests/test_channel_export_discussion_*.py` — passed, 38 tests.
- `pytest tests/test_channel_export_*.py` — passed, 121 tests.
- `python3 -m compileall tg_msg_manager` — passed.
- `ruff check tg_msg_manager tests` — passed.
- `ruff format --check tg_msg_manager tests` — passed.

## Limitations

- Not fully integrated into `export-channel` until Stage 3C.4.
- Old discussion threads are not refreshed or backfilled.
- Discussion comments are not persisted to SQLite.
- Discussion comment media is metadata-only.
- Reply-tree reconstruction is not implemented beyond preserving `reply_to_id`.

## Boundary Confirmation

- No SQLite changes.
- No migrations.
- No analytics.
- No OSINT interpretation.
- No discussion media full download.
- No Stage 3D work started.
