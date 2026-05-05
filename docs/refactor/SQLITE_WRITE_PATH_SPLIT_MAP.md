# SQLite Write Path Split Map

Old hot-path file: `tg_msg_manager/infrastructure/storage/_sqlite_write_path.py`

Current compatibility surface:

- `_sqlite_write_path.py` -> compatibility aggregator over split writer modules
- `_sqlite_sync_state.py` -> compatibility wrapper for state/export/retry writers

## Writer Modules

| Module | Responsibility |
| --- | --- |
| `write/connection.py` | connection factory |
| `write/transaction.py` | write transaction coordinator |
| `write/message_writer.py` | message upsert/delete orchestration |
| `write/user_writer.py` | users, chats, sync target registration |
| `write/target_link_writer.py` | `message_target_links` writes |
| `write/context_writer.py` | `message_context_links` + missing reply refs |
| `write/checkpoint_writer.py` | sync state checkpoints and tail/head updates |
| `write/retry_writer.py` | retry queue lifecycle |
| `write/report_writer.py` | export target metadata + export run journal |

## Function Map

| Old function | New writer | Batch / transaction note |
| --- | --- | --- |
| `_save_batches_by_target` | `message_writer.py` | one DB transaction per background batch |
| `_save_msg_internal` | `message_writer.py` | inside caller transaction |
| `_normalize_raw_payload` | `message_writer.py` | pure helper |
| `_json_serial` | `message_writer.py` | pure helper |
| `_ensure_target_link_in_conn` | `target_link_writer.py` | in existing transaction |
| `_upsert_user_from_payload_in_conn` | `user_writer.py` | in existing transaction |
| `_upsert_chat_from_payload_in_conn` | `user_writer.py` | in existing transaction |
| `_upsert_context_link_in_conn` | `context_writer.py` | in existing transaction |
| `_refresh_missing_reply_state_in_conn` | `context_writer.py` | in existing transaction |
| `_resolve_missing_reply_refs_for_parent_in_conn` | `context_writer.py` | in existing transaction |
| `_update_sync_state_for_message_in_conn` | `checkpoint_writer.py` | in existing transaction |
| `update_sync_tail` / `update_last_msg_id` / `update_last_sync_at` | `checkpoint_writer.py` | own transaction |
| `register_target` / `upsert_user` / `upsert_chat` | `user_writer.py` | own transaction |
| `upsert_export_target` / `start_export_run` / `finish_export_run` | `report_writer.py` | own transaction |
| retry queue methods | `retry_writer.py` | own transaction |
