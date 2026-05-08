# DB Baseline Report

Date: 2026-05-04

Note:

- this document is a historical pre-hardening baseline snapshot;
- it records the state before the runtime migrations were applied to the writable database;
- the current live runtime has since moved the working database forward beyond this baseline.

Command used:

```bash
python3 scripts/db_diagnostics.py messages.db
```

Database:

- path: `/Users/maczone/dev/TG_CLEANER/messages.db`
- integrity_check: `ok`
- journal_mode: `wal`
- user_version: `6` at baseline capture time

Key counts:

- messages: `77586`
- users: `3433`
- chats: `1`
- sync_targets: `23`
- sync_state: `1`
- message_context_links: `71760`
- message_target_links: `136142`
- retry_queue: `0`
- user_identity_history: `3189`

Message range:

- min timestamp: `2020-03-24T00:25:11+00:00`
- max timestamp: `2026-05-04T11:59:57+00:00`
- reply links in `messages`: `71339`

Data-quality snapshot:

- messages without `user_id`: `6`
- messages without `text` and without `media_type`: `0`
- duplicate `(chat_id, message_id)`: `0`
- duplicate `payload_hash`: `0`
- missing reply references: `22547`
- dangling context links: `22968`
- dangling target links with missing message: `0`
- dangling target links with missing user: `0`

Short conclusion:

- Core message uniqueness by `(chat_id, message_id)` is currently healthy.
- `message_target_links` is already chat-scoped and has no dangling links in the sampled baseline.
- The largest remaining schema/data risk is `message_context_links`, which is still keyed only by bare `message_id` pairs and shows a large dangling-link count in diagnostics.
- Reply incompleteness is expected in the current dataset and must be treated as a first-class migration concern before deeper thread/context features are added.

Current note:

- this baseline should be read together with the later hardening work: current runtime/schema expectations now live in `docs/sqlite_message_id_audit.md` and the active architecture overview.
