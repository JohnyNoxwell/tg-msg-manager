# Dataset Write Safety

## 1. Purpose

Direct channel export writes filesystem datasets. This document defines the write and commit model used to reduce partial dataset corruption when an `export-channel` run fails.

The model applies to channel payload files, channel manifests, channel state, discussion payload files, and discussion state. It does not introduce SQLite persistence or a database transaction layer.

## 2. Write Phases

The intended write phases are:

```text
prepare output paths
write payload temp files
commit payload files
write and commit manifest
save channel state last
save discussion state after manifest success
cleanup temp files
```

Temporary files are created in the same directory as the target file with a `.tmp` suffix. Successful commits replace the final file using Python's filesystem replace operation.

## 3. Full/Force Run Behavior

Full and force channel payload writes use overwrite mode:

```text
messages.jsonl.tmp -> messages.jsonl
messages.txt.tmp -> messages.txt
media_manifest.jsonl.tmp -> media_manifest.jsonl
```

If writing fails before commit, existing final files are not replaced and temporary files are removed.

Force discussion payload writes follow the same overwrite pattern:

```text
discussion_comments.jsonl.tmp -> discussion_comments.jsonl
discussion_comments.txt.tmp -> discussion_comments.txt
discussion_threads.jsonl.tmp -> discussion_threads.jsonl
```

## 4. Incremental Append Behavior

Incremental append uses copy-append-replace:

```text
copy existing final file to temp
append new rows to temp
replace final file after the write session exits successfully
```

If the append run fails before commit, the original final file remains unchanged and temporary files are removed.

This applies to:

- `messages.jsonl`
- `messages.txt`
- `media_manifest.jsonl`
- `discussion_comments.jsonl`
- `discussion_comments.txt`
- `discussion_threads.jsonl`

## 5. Manifest/State Ordering

`manifest.json` is serialized before replacement and is written through the same temp-and-replace helper.

Channel state ordering:

```text
payload commit succeeds
manifest commit succeeds
channel_export_state.json commit succeeds
```

Discussion state ordering when discussion export runs through `ChannelExportService`:

```text
discussion payload commit succeeds
manifest commit succeeds
channel_export_state.json commit succeeds
discussion_export_state.json commit succeeds
```

If manifest writing fails, channel state and discussion state are not advanced.

State consistency invariants and incremental/no-new-posts behavior are documented in [`STATE_AND_INCREMENTAL_MODEL.md`](STATE_AND_INCREMENTAL_MODEL.md).

## 6. Discussion Dataset Behavior

Discussion payload files use the same overwrite and copy-append-replace behavior as channel payload files.

No-new-posts incremental runs still do not resolve discussion sources, fetch discussion comments, rewrite discussion files, or mutate `discussion_export_state.json`.

## 7. Guarantees

The write model guarantees at the application level:

- payload temp files are cleaned up after normal success;
- payload temp files are cleaned up after write-session exceptions;
- overwrite failures do not replace existing final payload files;
- incremental append failures do not partially append final payload files;
- manifest serialization failures do not replace an existing manifest;
- channel state is saved only after payload and manifest commits succeed;
- discussion state is saved only after discussion payload, manifest, and channel state commits succeed in the service path;
- dataset schemas, manifest schema, state schema, and filenames are unchanged.

## 8. Non-Guarantees

This is not a full ACID transaction system.

Non-guarantees:

- no multi-file atomic transaction across all dataset files;
- no rollback of downloaded media files already written under `media/`;
- no protection against process termination or machine crash at every possible point between multiple file replacements;
- no concurrent-writer locking for multiple simultaneous exports to the same output directory;
- no SQLite transaction semantics because channel export remains filesystem-first.

## 9. Failure Behavior

Expected failure behavior:

- failure before payload commit leaves prior final payload files unchanged;
- failure during manifest serialization leaves prior `manifest.json` unchanged;
- failure during manifest write prevents channel and discussion state advancement;
- failure during discussion payload writing prevents discussion state advancement;
- temporary files use a predictable `.tmp` suffix and are removed by rollback where the process remains alive.
