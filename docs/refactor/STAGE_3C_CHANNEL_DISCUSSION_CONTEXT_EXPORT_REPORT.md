# Stage 3C — Channel Discussion Context Export Report

## 1. Summary

Stage 3C adds explicit linked discussion export to `export-channel`.

The default remains `--discussion none`. In default mode, no discussion resolver runs and no discussion files are written.

When `--discussion full` is requested, discussion comments are exported as dataset files for channel posts fetched in the current run.

## 2. Scope

Implemented scope:

- Discussion architecture contract.
- Discussion options, models, and resolver.
- Isolated fetch/map/render/write/state/export components.
- `export-channel` integration.
- CLI flags:
  - `--discussion none|full`
  - `--max-comments-per-post N`
- Manifest and CLI summary discussion counts.
- Tests and documentation.

Out of scope:

- SQLite persistence for discussion comments.
- SQLite schema changes or migrations.
- Analytics or OSINT interpretation.
- Discussion media full download.
- Old-thread refresh/backfill without `--force`.
- Reply-tree reconstruction beyond preserving `reply_to_id`.
- Stage 3D.

## 3. Architecture

Discussion-specific implementation lives under:

```text
tg_msg_manager/services/channel_export/discussions/
```

Components:

- `options.py`: discussion modes and validation.
- `models.py`: discussion records, result, state, and stats.
- `resolver.py`: linked discussion source resolution.
- `fetcher.py`: per-post discussion comment fetch boundary.
- `mapper.py`: Telegram/fake comment object to dataset record mapping.
- `jsonl_renderer.py`: JSONL rendering.
- `txt_renderer.py`: TXT rendering.
- `payload_writer.py`: discussion dataset file writing.
- `state_manager.py`: `discussion_export_state.json` read/write.
- `exporter.py`: isolated current-run discussion export orchestration.
- `manifest_summary.py`: discussion manifest block and included-file summary.

`ChannelExportService` only orchestrates by delegating to the isolated discussion resolver/exporter.

## 4. CLI Contract

Supported command shape:

```bash
python3 -m tg_msg_manager.cli export-channel \
  --channel @example \
  --limit 10 \
  --media metadata \
  --discussion full \
  --max-comments-per-post 100
```

Defaults:

- `--media metadata`
- `--discussion none`
- `--max-comments-per-post 100`

## 5. Dataset Files

When `--discussion full` is used and current-run posts are exported, the dataset may include:

```text
discussion_comments.jsonl
discussion_comments.txt
discussion_threads.jsonl
discussion_export_state.json
```

Default `--discussion none` writes none of these files.

## 6. State Behavior

Discussion state is stored only in:

```text
discussion_export_state.json
```

It is separate from `channel_export_state.json` and separate from SQLite.

Discussion state is saved only after discussion payload writing and manifest writing complete successfully.

## 7. Incremental Behavior

Incremental runs export discussions only for newly fetched channel posts.

No-new-posts runs:

- do not resolve discussion sources;
- do not fetch old discussion comments;
- do not rewrite discussion files;
- do not mutate `discussion_export_state.json`.

Force runs overwrite discussion files and rebuild discussion state for posts fetched in that force run.

## 8. Failure Behavior

Per-thread discussion failures are recorded in `discussion_threads.jsonl` and do not fail the whole channel export.

Critical writer failures fail the export before state is advanced.

Manifest write failure does not advance channel state or discussion state.

## 9. Tests

Added or updated coverage for:

- Discussion option validation.
- Discussion model construction.
- Discussion resolver behavior.
- Discussion fetcher behavior and comment limits.
- Mapper field preservation and metadata-only media.
- JSONL/TXT rendering.
- Payload writer overwrite/append behavior.
- Discussion state manager load/save/merge behavior.
- Isolated exporter success, failed-thread, not-linked, and partial behavior.
- `export-channel` default `none` behavior.
- Full discussion integration and manifest summary.
- Incremental current-run-only discussion export.
- No-new-posts no-refetch/no-state-mutation behavior.
- Force overwrite/rebuild behavior.
- Manifest failure state safety.
- CLI discussion summary output.

## 10. Verification Results

Final verification commands run:

- `pytest tests/test_channel_export_discussion_*.py` — passed, 38 tests.
- `pytest tests/test_channel_export_*.py` — passed, 130 tests.
- `python3 -m compileall tg_msg_manager` — passed.
- `ruff check tg_msg_manager tests` — passed.
- `ruff format --check tg_msg_manager tests` — passed.
- `make test` — passed, 336 tests.
- `make verify` — passed.
- `python3 -m tg_msg_manager.cli export-channel --help` — passed and shows `--discussion` / `--max-comments-per-post`.

## 11. Known Limitations

- No DB persistence.
- No old-thread refresh/backfill without `--force`.
- No full media download for discussion comments.
- No reply-tree reconstruction beyond preserving `reply_to_id`.
- Telegram linked discussion edge cases may depend on channel configuration and API availability.

## 12. No SQLite Changes

Stage 3C does not change SQLite schema, does not add migrations, and does not write discussion comments into SQLite.

## 13. No Analytics

Stage 3C does not add analytics, OSINT interpretation, sentiment analysis, bot detection, user profiling, influence scoring, or narrative classification.

## 14. Stage 3D

Stage 3D was not started.
