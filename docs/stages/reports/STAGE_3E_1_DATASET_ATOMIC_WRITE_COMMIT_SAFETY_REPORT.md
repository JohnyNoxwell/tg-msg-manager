# Stage 3E.1 - Dataset Atomic Write / Commit Safety Report

## 1. Summary

Stage 3E.1 hardened direct channel export filesystem writes with temp-file write/commit behavior.

Completed:

- added a focused atomic text write helper;
- changed channel payload writes to temp-file overwrite and copy-append-replace;
- changed discussion payload writes to temp-file overwrite and copy-append-replace;
- changed `manifest.json`, `channel_export_state.json`, and `discussion_export_state.json` saves to serialize then replace through temp files;
- documented write guarantees and non-guarantees;
- updated user-facing known limitations that previously described partial append rollback as missing;
- added failure and cleanup tests.

## 2. Atomic write model

The write model is:

```text
write temp payload files
commit payload files
write and commit manifest
save channel state last
save discussion state after manifest/channel state success
cleanup temp files
```

Temporary files are written in the target directory with a `.tmp` suffix and committed with filesystem replace.

## 3. Files/modules changed

Runtime modules changed:

```text
tg_msg_manager/services/channel_export/atomic_writer.py
tg_msg_manager/services/channel_export/payload_writer.py
tg_msg_manager/services/channel_export/discussions/payload_writer.py
tg_msg_manager/services/channel_export/manifest_writer.py
tg_msg_manager/services/channel_export/state_manager.py
tg_msg_manager/services/channel_export/discussions/state_manager.py
```

Tests changed:

```text
tests/test_channel_export_payload_writer.py
tests/test_channel_export_discussion_payload_writer.py
tests/test_channel_export_manifest.py
tests/test_channel_export_service.py
```

Docs changed:

```text
README.md
COMMANDS.md
docs/architecture/DATASET_WRITE_SAFETY.md
docs/architecture/README.md
docs/stages/README.md
```

## 4. Full/force write behavior

Full and force channel payload files now write to temp files and replace final files only when the session exits successfully.

Covered files:

```text
messages.jsonl
messages.txt
media_manifest.jsonl
```

Discussion full/force payload files use the same pattern:

```text
discussion_comments.jsonl
discussion_comments.txt
discussion_threads.jsonl
```

Overwrite failure tests verify existing final files are not replaced.

## 5. Incremental append behavior

Incremental append now uses copy-append-replace:

```text
copy final file to temp
append new records to temp
replace final file on successful session exit
```

Append failure tests verify final payload files remain unchanged and temporary files are removed.

## 6. Manifest/state ordering

`manifest.json` is serialized before writing and then committed through temp-file replace.

`ChannelExportService` already saved channel state after payload and manifest success. That ordering is preserved.

Discussion state save remains deferred in the service path until after discussion payload, manifest, and channel state success.

## 7. Discussion dataset behavior

Discussion payload writer behavior now matches channel payload writer safety:

- overwrite uses temp-and-replace;
- incremental append uses copy-append-replace;
- write-session failure rolls back temp files;
- `discussion_export_state.json` remains service-committed after manifest success.

No discussion CLI behavior, dataset fields, or state fields changed.

## 8. Failure behavior

Covered failure behavior:

- full overwrite write-session failure does not replace channel payload files;
- incremental append write-session failure does not partially append channel payload files;
- discussion overwrite failure does not replace discussion payload files;
- discussion append failure does not partially append discussion payload files;
- manifest serialization failure does not replace an existing manifest;
- channel payload failure does not advance channel state;
- manifest failure does not advance channel or discussion state;
- temp files are cleaned on tested success and failure paths.

## 9. Guarantees

Guaranteed by this stage:

- same-directory temp files for payload, manifest, and state writes;
- atomic replace for individual final files where supported by the filesystem;
- copy-append-replace for incremental payload appends;
- channel state advances only after payload and manifest success;
- discussion state advances only after discussion payload, manifest, and channel state success in the service path;
- no dataset, manifest, or state schema changes.

## 10. Remaining limitations

This is not a full multi-file ACID transaction.

Remaining limitations:

- no all-files-at-once transaction across payload, manifest, and state files;
- no rollback of media files already downloaded under `media/`;
- no crash-proof guarantee for every point between multiple file replacements;
- no concurrent-writer lock for two exports targeting the same directory.

## 11. Tests

Added or updated coverage for:

- overwrite rollback for channel payload files;
- incremental append rollback for channel payload files;
- temp cleanup after channel payload success/failure;
- overwrite rollback for discussion payload files;
- incremental append rollback for discussion payload files;
- manifest serialization failure preserving the old manifest;
- channel payload failure preserving channel state;
- existing manifest failure preserving channel and discussion state.

## 12. Verification results

| Command | Result |
| --- | --- |
| `pytest tests/test_channel_export_payload_writer.py tests/test_channel_export_discussion_payload_writer.py tests/test_channel_export_manifest.py tests/test_channel_export_service.py` | passed, 39 tests |
| `pytest tests/test_channel_export_*.py` | passed, 163 tests |
| `python3 -m compileall tg_msg_manager` | passed |
| `ruff check tg_msg_manager tests` | passed |
| `ruff format --check tg_msg_manager tests` | passed, 247 files already formatted |
| `python3 -m tg_msg_manager.cli export-channel --help` | passed |

`make test` and `make verify` were not run during this stage because the required stage verification passed and the current stage scope was channel export write safety.

No CLI behavior changed.
No dataset schema changed.
No state schema changed.
No SQLite schema changed.
No product feature was added.

## 13. Status

Stage 3E.1: complete.
