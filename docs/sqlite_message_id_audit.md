# SQLite Message ID Audit

Date: 2026-05-04

Architectural rule:

- Telegram messages must be identified by `(chat_id, message_id)`.
- Bare `message_id` is only safe when the chat scope is already fixed and cannot leak across tables or chats.

## Safe or locally-scoped uses

These places use bare `message_id`, but only after `chat_id` is already fixed in the surrounding query or in-memory structure:

- `read/messages.py`
- `read/context.py`
- `read/targets.py`
- `services/context/*` in per-chat candidate pools
- `services/sync/range_scanner.py` when filtering IDs inside a single chat sync pass
- `db_export` formatting logic when resolving reply references inside one already loaded export set

## Current cross-table risk

### `message_context_links`

Current schema:

```sql
CREATE TABLE IF NOT EXISTS message_context_links (
    message_id INTEGER,
    context_message_id INTEGER,
    link_type TEXT,
    PRIMARY KEY (message_id, context_message_id)
)
```

Current write path:

- [`_sqlite_write_path.py`](/Users/maczone/dev/TG_CLEANER/tg_msg_manager/infrastructure/storage/_sqlite_write_path.py) inserts only `message_id` and `reply_to_id`

Why this is risky:

- `message_id` is not globally unique across chats;
- two different chats can generate the same `(message_id, context_message_id)` pair;
- diagnostics already report a large dangling-link count, which is consistent with this design weakness.

Immediate conclusion:

- `message_context_links` is the first schema object that must be migrated to chat-safe metadata.

## Already hardened

### `messages`

- primary key is `(chat_id, message_id)`

### `message_target_links`

- primary key is `(chat_id, message_id, target_user_id)`
- read/write paths already join on both `chat_id` and `message_id`

## Recommended next migration order

1. Migrate `message_context_links` to include chat-safe source/target message coordinates.
2. Rebuild or backfill legacy context-link rows with explicit metadata.
3. Re-run `scripts/db_diagnostics.py` and compare dangling-context-link counts.
4. Only after that extend thread/context analytics on top of the stabilized schema.
