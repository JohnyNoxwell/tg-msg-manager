# Context Engine Split Map

Old hot-path file: `tg_msg_manager/services/context_engine.py`

Current compatibility surface:

- `tg_msg_manager/services/context_engine.py` -> thin wrapper
- implementation lives in `tg_msg_manager/services/context/engine.py`

## Strategy Modules

- `reply_chain_resolver.py` -> parent reply lookup boundary
- `neighbor_window_resolver.py` -> candidate/window lookup boundary
- `cluster_builder.py` -> cluster assembly boundary
- `deduplicator.py` -> processed-id state holder
- `scope_policy.py` -> explicit context limits/depth policy
- `rounds.py` -> batch-round orchestration facade

## Method Map

| Method group | Responsibility | Target module |
| --- | --- | --- |
| `reset`, `_message_key` | run-local processed state | `deduplicator.py` / `engine.py` |
| `extract_batch_context` | batch-round orchestration | `rounds.py` |
| `extract_context` | single-target facade | `engine.py` |
| cluster assembly methods | `_initialize_clusters`, `_associate_candidates`, `_with_cluster` | `cluster_builder.py` / existing `clustering.py` |
| reply-chain methods | `_fetch_parent_messages` | `reply_chain_resolver.py` / existing `resolvers.py` |
| neighbor-window methods | `_fetch_candidate_pool`, `_scan_before_ids`, `_scan_after_ids` | `neighbor_window_resolver.py` / existing `resolvers.py` |
| fallback methods | `_apply_time_fallback`, `_select_time_fallback` | existing `fallback.py` |
| fetch/storage boundary methods | `_fetch_range`, `_fetch_ranges`, `_fetch_missing_ids`, `_load_stored_range`, `_load_stored_messages_by_ids`, `_load_stored_replies` | existing `fetchers.py` |

## Result

- `tg_msg_manager/services/context_engine.py` is now a 6-line compatibility wrapper.
- `tg_msg_manager/services/context/engine.py` is a 209-line facade that wires dedicated resolvers and delegates batch extraction to `rounds.py`.
- Reply-chain, neighbor-window, cluster assembly, deduplication, and fallback rules now live behind explicit boundaries instead of one monolithic hot-path file.
