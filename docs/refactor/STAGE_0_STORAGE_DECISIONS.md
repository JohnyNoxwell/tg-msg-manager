# Stage 0 Storage Decisions

Date: 2026-05-04

## `message_context_links`

### Current usage audit

References found:

- schema definition:
  - `tg_msg_manager/infrastructure/storage/_sqlite_schema.py`
- write path:
  - `tg_msg_manager/infrastructure/storage/_sqlite_write_path.py::_upsert_context_link_in_conn()`
- read path:
  - none
- tests:
  - no direct test reads

### Classification

- schema: active
- write: active
- read: inactive
- migration: implicit via schema creation only
- source of truth: no

### Current effective source of truth for context assembly

Current context behavior is driven by:

- `messages.reply_to_id`
- `messages.context_group_id`
- `message_target_links`
- storage range / reply read helpers
- live Telegram fallback through context fetchers

`message_context_links` is therefore not required by the current read-side or context engine behavior.

### Stage 0 decision

Decision: keep as a legacy compatibility table for now.

Why:

- it is still written during persistence;
- removing it would require explicit migration coverage;
- no Stage 0 requirement depends on reclaiming the table immediately.

### Recommendation for later stage

- do not drop in Stage 0;
- if a later cleanup stage wants removal, first add:
  - explicit migration plan;
  - read/write compatibility tests;
  - confirmation that no external scripts depend on it.
