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

## Hardened in code

### `message_context_links`

Runtime schema target:

```sql
CREATE TABLE IF NOT EXISTS message_context_links (
    chat_id INTEGER NOT NULL,
    message_id INTEGER NOT NULL,
    context_message_id INTEGER NOT NULL,
    link_type TEXT NOT NULL DEFAULT 'unknown',
    distance INTEGER,
    algorithm_version TEXT NOT NULL DEFAULT 'legacy',
    created_at INTEGER NOT NULL,
    PRIMARY KEY (chat_id, message_id, context_message_id, link_type, algorithm_version)
)
```

Implemented behavior:

- [`_sqlite_schema.py`](/Users/maczone/dev/TG_CLEANER/tg_msg_manager/infrastructure/storage/_sqlite_schema.py) creates the chat-safe table on fresh databases and migrates legacy rows from the old schema.
- [`_sqlite_write_path.py`](/Users/maczone/dev/TG_CLEANER/tg_msg_manager/infrastructure/storage/_sqlite_write_path.py) now writes `chat_id`, `distance`, `algorithm_version`, and `created_at` for new reply links.
- legacy rows are copied into the new table with `link_type='legacy'` and `algorithm_version='legacy'`.
- the first migration keeps a `message_context_links_legacy_backup` table instead of deleting the old rows immediately.

What still remains risky:

- existing writable databases still need to be opened once through the migrated runtime to move from the legacy table shape to the new chat-safe one;
- the baseline report taken before that writable migration still shows the old table shape and the pre-migration dangling-link count;
- deeper context reconstruction still relies primarily on `messages.reply_to_id` and `context_group_id`, so this schema hardening is necessary but not sufficient for full thread semantics.

Immediate conclusion:

- `message_context_links` is no longer the next planned migration item; it is now the first completed chat-safe link migration in the SQLite hardening track.

## Already hardened

### `messages`

- primary key is `(chat_id, message_id)`

### `message_target_links`

- primary key is `(chat_id, message_id, target_user_id)`
- runtime schema now also carries `link_type` and `created_at`
- legacy rows are migrated into metadata-aware rows and preserved in `message_target_links_legacy_backup`
- write-path now upgrades new links toward:
  - `target_author`
  - `reply_context`
  - `legacy`
- read/write paths already join on both `chat_id` and `message_id`

## Recommended next migration order

1. Open the real writable database through the migrated runtime and capture a post-migration diagnostics snapshot.
2. Re-run `scripts/db_diagnostics.py` and compare pre/post-migration snapshots for both context links and target links.
3. Continue with export-state tables and broader export bookkeeping normalization.
4. Only after that extend thread/context analytics on top of the stabilized schema.
