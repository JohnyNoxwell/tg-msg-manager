# Context Relation Tables Decision

## 1. Existing tables

- `message_context_links`
- `message_context_links_legacy_backup`
- `message_target_links`
- `message_target_links_legacy_backup`
- `messages.context_group_id`
- `messages.reply_to_id`

## 2. Current writers

- `tg_msg_manager/infrastructure/storage/write/context_writer.py` writes `message_context_links`
- `tg_msg_manager/infrastructure/storage/write/target_link_writer.py` writes `message_target_links`
- `tg_msg_manager/infrastructure/storage/write/message_writer.py` persists `messages.reply_to_id` and `messages.context_group_id`

## 3. Current readers

- Active export read paths use `message_target_links`
- Active context clustering uses `messages.reply_to_id` and `messages.context_group_id`
- Reporting reads counts from `message_target_links` and `messages.context_group_id`
- Current hot-path context/export code does not use `message_context_links` as a primary read source

## 4. Current hot-path usage

- `message_target_links` is active hot-path state for export/db-export selection
- `messages.reply_to_id` is active reply-parent source of truth
- `messages.context_group_id` is active context-cluster grouping signal
- `message_context_links` is retained and tested, but not used as the current hot-path source of truth

## 5. Problems

- `message_context_links` still exists in schema and migrations, so its status must be explicit
- future features could accidentally depend on it despite Stage 0 docs already indicating it is not required by the current read-side
- `message_target_links` and `context_group_id` already cover active export/context selection more directly

## 6. Decision

Chosen status:

- `message_context_links`: Legacy compatibility layer
- `message_target_links`: First-class relation layer
- `messages.context_group_id`: First-class context-cluster field
- `messages.reply_to_id`: First-class reply relation field

## 7. Consequences

- New context logic must not depend on `message_context_links` unless a future migration explicitly promotes it again
- `message_target_links` remains the first-class relation layer for target attribution and DB-export source selection
- context reconstruction should continue to rely on `reply_to_id`, `context_group_id`, `message_target_links`, and live/storage fetchers
- schema, writers, and tests for `message_context_links` remain for compatibility and migration safety only

## 8. Follow-up tasks

- Keep compatibility comments near `context_writer.py` and related schema definitions
- Do not build analytics/export/context features directly on `message_context_links`
- If a future migration wants a first-class relation graph, document new semantics before promoting `message_context_links`
