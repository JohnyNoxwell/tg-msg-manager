# State and Incremental Model

## 1. Purpose

This document defines the state model for direct channel export.

State files are not analytics.
State files are not source-of-truth message databases.
State files are export checkpoint metadata.

The state model exists so `export-channel` can resume incremental filesystem exports without changing SQLite schema or persisting channel posts/comments to the application database.

## 2. Channel State

Channel state lives in:

```text
channel_export_state.json
```

It records:

- channel identity;
- last exported message id;
- aggregate message/media counters;
- date bounds;
- last manifest filename;
- completed run status and update timestamps.

The state is a committed checkpoint. It must describe only dataset payload and manifest files that were successfully written and committed.

## 3. Discussion State

Discussion state lives in:

```text
discussion_export_state.json
```

It is separate from channel state and separate from SQLite.

It records:

- channel id;
- discussion chat id when available;
- aggregate thread/comment/failure counters;
- completed run status and update timestamps.

Discussion state is valid only for the channel dataset it belongs to.

## 4. Full/Force Run

A full run creates a new channel dataset checkpoint from the posts fetched in that run.

A force run ignores existing channel state, overwrites dataset payload files, and rebuilds channel state from the forced run contents.

For `--discussion full`, force mode also overwrites discussion files and rebuilds discussion state from posts fetched in that force run.

## 5. Incremental Run

An incremental run uses `channel_export_state.json` as the checkpoint.

Rules:

- fetch only posts newer than `last_exported_message_id`;
- append committed new payload rows through copy-append-replace;
- advance channel state only after payload and manifest success;
- keep channel id stable;
- do not let message/media counters move backwards;
- do not let `last_exported_message_id` move backwards after successful incremental runs.

For discussion export, incremental runs export discussion comments only for newly exported channel posts. Discussion state counters must not move backwards.

## 6. No-New-Posts Run

If an incremental run finds no new channel posts:

- channel manifest may be refreshed;
- channel state is not advanced;
- no discussion resolver runs;
- no discussion comments are fetched;
- discussion files are not rewritten;
- `discussion_export_state.json` is not mutated.

## 7. Manifest/State Ordering

The service-level ordering is:

```text
payload write session commits
discussion payload write session commits when applicable
manifest writes successfully
channel_export_state.json saves successfully
discussion_export_state.json saves successfully when applicable
```

Discussion state is saved after channel state in the service path so discussion state does not advance if the channel manifest or channel state commit fails.

## 8. Failure Behavior

Failure rules:

- payload write failure does not save channel state;
- discussion payload failure does not save discussion state;
- manifest write failure does not save channel or discussion state;
- failed per-thread discussion records may be committed as dataset facts;
- when failed per-thread records are committed, discussion state reflects the committed files and failure counters.

## 9. Consistency Invariants

Channel state invariants:

- `channel_id` must match the resolved channel before incremental reuse;
- counters must not be negative;
- incremental message/media counters must not decrease;
- `last_exported_message_id` must not move backwards after successful incremental runs;
- `last_run_status` is `completed` for committed state.

Discussion state invariants:

- counters must not be negative;
- `channel_id` must match the channel dataset;
- `discussion_chat_id` must match the resolved discussion source when both are known;
- incremental thread/comment/failure counters must not decrease;
- no-new-posts runs must not mutate discussion state;
- `last_run_status` is `completed` for committed state.

## 10. Non-Goals

Non-goals:

- SQLite persistence for channel posts or discussion comments;
- SQLite schema changes or migrations;
- analytics, OSINT interpretation, profiling, scoring, or classification;
- using state files as a queryable message database;
- full multi-file ACID transactions across all dataset files;
- refresh/backfill of old discussion threads outside explicit force behavior.
