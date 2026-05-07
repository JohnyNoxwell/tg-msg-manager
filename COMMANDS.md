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
- `--force` optional. Reserved re-export flag for future overwrite/policy handling.

Dataset layout:

```text
exports/
  channels/
    @channel_name__123456789/
      manifest.json
      messages.jsonl
      messages.txt
      media_manifest.jsonl
      media/
```

Notes:

- Stage 3A is dataset projection only. No analytics are performed.
- Stage 3A accepts broadcast channels only. Groups and supergroups are not supported by `export-channel`.
- Default media mode is `metadata`.
- `--media full` is not implemented yet and currently returns a clear CLI error.
- The command currently performs a full re-export into the dataset directory; it does not implement incremental channel updates yet.

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
