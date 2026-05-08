# Commands

## `export-channel`

Export posts directly from a Telegram channel into a filesystem dataset.

Example:

```bash
python3 -m tg_msg_manager.cli export-channel --channel @example --limit 100 --media metadata
```

Arguments:

- `--channel` required. Broadcast-channel username, numeric ID, or another value accepted by `get_entity`.
- `--limit` optional. Maximum number of posts to export.
- `--media` optional. `none`, `metadata`, or `full`.
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
```

Notes:

- Stage 3A / 3A.1 is dataset projection only. No analytics are performed.
- `export-channel` accepts broadcast channels only. Groups and supergroups are not supported.
- Default media mode is `metadata`.
- `--media full` is not implemented yet and currently returns a clear CLI error.
- Successful runs create/update `channel_export_state.json` with the last exported message id and aggregate counters.
- A second run without `--force` exports only posts newer than `last_exported_message_id` and appends to `messages.jsonl`, `messages.txt`, and `media_manifest.jsonl`.
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
