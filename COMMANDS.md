# Commands

Documentation map: [`docs/README.md`](docs/README.md)
Coding-agent contract: [`AGENTS.md`](AGENTS.md)

## `export-channel`

Export posts directly from a Telegram channel into a filesystem dataset.

Example:

```bash
python3 -m tg_msg_manager.cli export-channel --channel @example --limit 100 --media metadata
python3 -m tg_msg_manager.cli export-channel --channel @example --limit 100 --media full
python3 -m tg_msg_manager.cli export-channel --channel @example --limit 100 --media full --max-media-size 50MB --media-types photo,video
python3 -m tg_msg_manager.cli export-channel --channel @example --limit 10 --media metadata --discussion full --max-comments-per-post 100
```

Arguments:

- `--channel` required. Broadcast-channel username, numeric ID, or another value accepted by `get_entity`.
- `--limit` optional. Maximum number of posts to export.
- `--media` optional. `none`, `metadata`, or `full`.
- `--max-media-size` optional. Maximum file size for `--media full`. Accepts bytes or units such as `50MB`. Default in full mode: `50MB`.
- `--media-types` optional. Comma-separated allowlist for `--media full`: `photo`, `video`, `document`, `audio`, `voice`, `animation`.
- `--discussion` optional. `none` or `full`. Default: `none`.
- `--max-comments-per-post` optional. Positive integer limit for linked discussion comments per exported channel post. Default: `100`.
- `--output-dir` optional. Base directory for channel export datasets.
- `--force` optional. Ignore `channel_export_state.json`, rebuild the dataset from scratch, and recreate state.

Dataset layout:

```text
exports/
  channels/
    @channel_name__123456789/
      manifest.json
      messages.jsonl
      messages.txt
      media_manifest.jsonl
      channel_export_state.json
      media/
      discussion_comments.jsonl       # only with --discussion full
      discussion_comments.txt         # only with --discussion full
      discussion_threads.jsonl        # only with --discussion full
      discussion_export_state.json    # only with --discussion full
```

Notes:

- Stage 3A / 3A.1 / 3B / 3C is dataset projection only. No analytics are performed.
- `export-channel` accepts broadcast channels only. Groups and supergroups are not supported.
- Default media mode is `metadata`.
- Default discussion mode is `none`; in this mode no discussion resolver runs and no discussion files are written.
- `--discussion full` exports linked discussion comments only for channel posts fetched in the current run.
- Incremental runs export discussions only for newly fetched posts. No-new-posts runs do not refetch old discussion threads and do not mutate `discussion_export_state.json`.
- `--force --discussion full` overwrites discussion files and rebuilds discussion state for posts fetched in that force run.
- `--media full` downloads files only when explicitly requested and records final statuses in `media_manifest.jsonl`.
- Media filenames and final media subdirectories are resolved from a safe Telegram original filename, then Telegram MIME type, then lightweight magic bytes. `.bin` is used only when the type remains unknown.
- `media_manifest.jsonl` records the final media path; no OCR, speech-to-text, media analysis, transcoding, or ffmpeg processing is performed.
- Full media statuses are `downloaded`, `already_exists`, `skipped_by_size`, `skipped_by_type`, and `failed`.
- Discussion comment media remains metadata-only; full media download for discussion comments is not implemented.
- Discussion comments are not persisted to SQLite, and no SQLite migration is required.
- Successful runs create/update `channel_export_state.json` with the last exported message id and aggregate counters.
- A second run without `--force` exports only posts newer than `last_exported_message_id` and appends to `messages.jsonl`, `messages.txt`, and `media_manifest.jsonl`.
- Channel and discussion payload appends use temp-file copy/append/replace, so a write-session failure does not partially append final payload files.
- `channel_export_state.json` and `discussion_export_state.json` advance only after required payload and manifest writes succeed.
- If there are no new posts, the command reports that state clearly and does not advance the export cursor.

## Interactive Menu

The interactive `tg` menu now uses two-digit item codes:

- `01`..`10` for primary actions
- `11` for `Retry Queue`
- `12` for `Audit Report`
- `98` for language toggle
- `00` for exit

Legacy short inputs remain accepted for compatibility:

- `1`..`9`
- `R`
- `P`
- `L`
- `0`

Interactive menu item `10` / `export-channel` asks for the same channel export
controls as the direct command path: discussion mode (`none` / `full`), max
comments per post, force re-export, output directory, max media size, and media
types. Empty answers preserve the direct CLI defaults.
