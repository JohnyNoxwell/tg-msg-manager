# Live Smoke Checklist

## Variables

Use real local values:

- `TEST_USER_ID`: target Telegram user ID for export/archive checks
- `TEST_CHAT_ID`: chat/dialog ID that contains known messages from `TEST_USER_ID`
- `TEST_DELETE_USER_ID`: disposable local target ID used only for destructive delete validation in a copied test DB
- `TEST_CHANNEL`: Telegram channel username or ID for direct channel export checks

## Preconditions

- Valid Telegram session exists.
- Test chat/dialog is available.
- Test user ID is known.
- DB backup created.
- Network available.

## Commands

### 1. Basic CLI help

Command:

```bash
python3 -m tg_msg_manager.cli --help
```

Expected:

- exit code `0`
- command exits `0`
- help output contains main commands

Failure:

- non-zero exit code
- traceback
- missing `export`, `db-export`, `export-pm`, `export-channel`, `retry`, or `report` commands

### 2. Minimal sync

Command:

```bash
python3 -m tg_msg_manager.cli export --user-id "$TEST_USER_ID" --chat-id "$TEST_CHAT_ID" --flat --limit 1
```

Expected:

- exit code `0`
- no crash
- DB receives a new or known message
- sync checkpoint updates correctly

Failure:

- non-zero exit code
- no message persistence for a known live message
- checkpoint not updated after a successful run

### 3. Flat export

Command:

```bash
python3 -m tg_msg_manager.cli export --user-id "$TEST_USER_ID" --chat-id "$TEST_CHAT_ID" --flat --limit 1
```

Expected:

- exit code `0`
- output file created
- target user's message appears
- no unrelated messages included

Failure:

- non-zero exit code
- output file missing
- target message absent
- unexpected unrelated context appears in flat mode

### 4. Deep context export

Command:

```bash
python3 -m tg_msg_manager.cli export --user-id "$TEST_USER_ID" --chat-id "$TEST_CHAT_ID" --depth 2 --limit 1
```

Expected:

- exit code `0`
- output file created
- target message included
- context messages included
- separators preserved

Failure:

- non-zero exit code
- output file missing
- context not rendered in deep mode
- formatting separators differ unexpectedly

### 5. DB export

Command:

```bash
python3 -m tg_msg_manager.cli db-export --user-id "$TEST_USER_ID" --json
```

Expected:

- exit code `0`
- output created
- export target state updates
- unchanged second run is skipped or handled as designed

Failure:

- non-zero exit code
- JSON/JSONL artifact missing
- target export state not updated
- repeated unchanged run rewrites output unexpectedly

### 6. Private archive

Command:

```bash
python3 -m tg_msg_manager.cli export-pm --user-id "$TEST_USER_ID"
```

Expected:

- exit code `0`
- no crash
- archive output created
- checkpoint/state updated

Failure:

- non-zero exit code
- chat log or media directories missing
- target checkpoint not updated after a successful archive

### 7. Retry/report

Command:

```bash
python3 -m tg_msg_manager.cli retry --list
python3 -m tg_msg_manager.cli retry --limit 1
python3 -m tg_msg_manager.cli report
```

Expected:

- commands exit `0`
- report contains expected sections
- retry listing renders without traceback
- retry run either processes due tasks or reports a zero-work summary without traceback

Failure:

- non-zero exit code
- missing retry/report sections
- traceback in either command

### 8. Update summary

Command:

```bash
python3 -m tg_msg_manager.cli update
```

Expected:

- exit code `0`
- command prints per-user summary lines for changed targets
- each changed line uses the current format: `<target name> - <own count> without context, <linked count> with context`
- counts reflect messages newly synced in the current `update` run, not historical per-target totals from the local DB
- unchanged targets are not printed in the final update summary block

Failure:

- non-zero exit code
- summary falls back to the old aggregate `processed/targets` block
- traceback during tracked update finalization

### 9. Clean dry-run

Command:

```bash
python3 -m tg_msg_manager.cli clean --dry-run
```

Expected:

- exit code `0`
- command does not delete Telegram messages
- summary is printed
- dry-run warning/info is shown

Failure:

- non-zero exit code
- destructive behavior during dry-run
- traceback or missing summary

### 10. Delete safety note

Command:

```bash
python3 -m tg_msg_manager.cli delete --user-id "$TEST_DELETE_USER_ID"
```

Expected:

- run only against a disposable copied database and disposable export/archive directories
- local DB rows and local export/archive artifacts for the disposable user are removed
- no Telegram-side deletion happens
- rollback path is restoring the copied DB/files from backup

Failure:

- command is run against the primary working database
- unrelated targets are removed
- local filesystem cleanup diverges from the target user scope

Notes:

- `delete` has no dry-run/safe-mode flag in the current CLI.
- Because of that, it is not part of routine live smoke on the primary workspace.
- Use it only in an isolated copy of the workspace after making a backup.

### 11. Report-only confirmation

Command:

```bash
python3 -m tg_msg_manager.cli report
```

Expected:

- exit code `0`
- report renders database/target/retry/export sections
- no Telegram access is required

Failure:

- non-zero exit code
- traceback

### 12. Direct channel export

Command:

```bash
python3 -m tg_msg_manager.cli export-channel --channel "$TEST_CHANNEL" --limit 3 --media metadata
```

Expected:

- exit code `0`
- output directory created under `exports/channels/`
- `manifest.json` exists
- `messages.jsonl` exists
- `messages.txt` exists
- `media_manifest.jsonl` exists
- `media/` directory exists
- `channel_export_state.json` exists
- full media files are not downloaded in metadata mode
- source is a broadcast channel, not a group/supergroup
- rerunning the same command prints a clear `no new posts` / zero-new-work outcome or appends only genuinely new posts
- `--force` recreates the dataset from scratch instead of appending duplicates

Failure:

- non-zero exit code
- traceback
- required dataset files missing
- state file missing
- metadata mode downloads full media unexpectedly
- rerun appends duplicate posts without new channel content
- `--force` leaves the old dataset appended instead of overwritten
- command is pointed at a group/supergroup and is treated as a valid broadcast-channel export

### 13. Direct channel export with full media

Non-routine test. Stage 3B enables controlled full media download; keep this smoke scoped and small.

Command:

```bash
python3 -m tg_msg_manager.cli export-channel --channel "$TEST_CHANNEL" --limit 1 --media full --max-media-size 50MB
```

Expected:

- exit code `0`
- media file downloaded or explicitly marked `already_exists`
- `media_manifest.jsonl` row contains final status and `sha256` for downloaded/existing files
- no silent fallback to metadata-only behavior

Failure:

- non-zero exit code
- silent success without media file / final media status
- missing `sha256` for `downloaded` or `already_exists`

### 14. Direct channel export full media with type/size guardrails

Command:

```bash
python3 -m tg_msg_manager.cli export-channel --channel "$TEST_CHANNEL" --limit 3 --media full --media-types photo --max-media-size 1MB
```

Expected:

- exit code `0`
- disallowed or oversized media are recorded as `skipped_by_type` / `skipped_by_size`
- rerunning the same command or `--force` on the same dataset does not create duplicate payload rows
- existing media files are reused as `already_exists` instead of being downloaded again

Failure:

- unexpected media download outside allowlist/size policy
- duplicate payload rows after rerun
- existing files re-downloaded instead of marked `already_exists`

### 15. Direct channel export with linked discussion comments

Use a broadcast channel that has a linked discussion group. Keep the limit small.

Command:

```bash
python3 -m tg_msg_manager.cli export-channel \
  --channel "$TEST_CHANNEL" \
  --limit 3 \
  --media metadata \
  --discussion full \
  --max-comments-per-post 20
```

Expected:

- exit code `0`
- `discussion_comments.jsonl` exists when discussion export is available for current-run posts
- `discussion_comments.txt` exists when discussion export is available for current-run posts
- `discussion_threads.jsonl` exists
- `discussion_export_state.json` exists
- `manifest.json` contains a `discussion` block with mode `full`
- failed thread count is recorded if some threads fail or are unavailable
- no SQLite migration is required
- no full media files are downloaded for discussion comments

Incremental/no-new-posts check:

- rerun without `--force`
- if there are no new channel posts, old discussion threads are not refetched
- `discussion_export_state.json` is not mutated on a no-new-posts run

Failure:

- non-zero exit code
- missing discussion files when the channel has linked discussion data for current-run posts
- `manifest.json` lacks the `discussion` block
- discussion comments are written into SQLite
- discussion media is fully downloaded
- old discussion threads are refreshed without `--force`

## Result table

| Date | Commit | Tester | Scenario | Result | Notes |
|---|---|---|---|---|---|
