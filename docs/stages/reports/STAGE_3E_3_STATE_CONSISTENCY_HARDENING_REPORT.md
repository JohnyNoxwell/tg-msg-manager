# Stage 3E.3 - State Consistency Hardening Report

## 1. Summary

Stage 3E.3 made direct channel export state consistency rules explicit, documented, and tested.

Completed:

- added pure state consistency helper functions;
- validated loaded/saved channel state for non-negative counters and committed status;
- validated loaded/saved discussion state for non-negative counters and committed status;
- validated previous discussion state before incremental merge;
- added tests for channel and discussion incremental monotonicity;
- added tests for invalid state counters and mismatched discussion state;
- documented the state and incremental model.

## 2. State invariants

Channel state invariants now covered:

- counters must not be negative;
- `last_exported_message_id` must not be negative;
- committed state uses `last_run_status == "completed"`;
- incremental channel state must belong to the same channel;
- incremental counters must not move backwards;
- incremental `last_exported_message_id` must not move backwards.

Discussion state invariants now covered:

- counters must not be negative;
- committed state uses `last_run_status == "completed"`;
- incremental discussion state must belong to the same channel;
- incremental discussion state must belong to the same discussion chat when both sides know the chat id;
- thread/comment/failure counters must not move backwards.

## 3. Channel state behavior

`ChannelExportStateManager` now validates state integrity after load and before save.

Existing channel behavior remains:

- channel identity mismatch is rejected before incremental reuse;
- channel state is saved after payload and manifest success;
- manifest failure does not advance channel state;
- payload failure does not advance channel state.

## 4. Discussion state behavior

`ChannelDiscussionStateManager` now validates state integrity after load and before save.

`ChannelDiscussionExporter` now rejects incompatible previous discussion state before incremental merge when:

- previous discussion state belongs to a different channel;
- previous discussion state belongs to a different discussion chat and both chat ids are known.

Existing discussion behavior remains:

- no-new-posts runs do not resolve/fetch/mutate discussion state;
- discussion state is saved only after channel manifest/state success in the service path;
- force runs rebuild discussion state for posts fetched in the force run.

## 5. Failure-path coverage

Coverage now includes:

- channel payload failure does not advance channel state;
- manifest failure does not advance channel state;
- manifest failure does not advance discussion state;
- discussion payload failure does not advance discussion state;
- no-new-posts does not resolve/fetch/mutate discussion state;
- incremental success advances channel and discussion totals;
- force success rebuilds discussion state;
- invalid channel state for the wrong channel is rejected;
- invalid discussion state mismatch is rejected.

## 6. Docs updated

Added:

```text
docs/architecture/STATE_AND_INCREMENTAL_MODEL.md
```

Updated:

```text
docs/architecture/README.md
docs/architecture/DATASET_WRITE_SAFETY.md
docs/stages/README.md
```

## 7. Verification results

| Command | Result |
| --- | --- |
| `pytest tests/test_channel_export_state_consistency.py tests/test_channel_export_state_manager.py tests/test_channel_export_discussion_state_manager.py tests/test_channel_export_discussion_exporter.py tests/test_channel_export_service.py` | passed, 45 tests |
| `pytest tests/test_channel_export_*.py` | passed, 176 tests |
| `python3 -m compileall tg_msg_manager` | passed |
| `ruff check tg_msg_manager tests` | passed |
| `ruff format --check tg_msg_manager tests` | passed, 250 files already formatted |
| `python3 -m tg_msg_manager.cli export-channel --help` | passed |

`make test` and `make verify` were left for the sequence-level final verification.

## 8. Runtime behavior statement

No CLI behavior changed.
No dataset schema changed.
No state schema changed.
No SQLite schema changed.
No product feature was added.

The only runtime hardening is rejection of invalid or incompatible state that would violate the documented consistency invariants.

## 9. Remaining limitations

- State files are checkpoint metadata, not source-of-truth message databases.
- The filesystem dataset still does not provide full multi-file ACID transactions.
- Downloaded media files already written under `media/` are not rolled back.
- Concurrent exports to the same output directory are not locked.

## 10. Status

Stage 3E.3: complete.
