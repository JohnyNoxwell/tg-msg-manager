# DB Export Service Split Map

| Current method | Responsibility | Target module | Public/private | Covered by tests | Notes |
|---|---|---|---|---|---|
| `__init__` | dependency wiring | `services/db_export/service.py` | public | indirect | Keep service construction stable |
| `_load_export_manifest` | legacy manifest lookup | `services/db_export/skip_policy.py` | private | indirect | Legacy compatibility path only |
| `_artifact_paths_exist` | artifact existence check | `services/db_export/skip_policy.py` | private | indirect | Shared by DB state and legacy manifest checks |
| `_db_skip_match` | fingerprint-to-DB-state skip match | `services/db_export/skip_policy.py` | private | yes | Used by unchanged export tests |
| `_legacy_manifest_skip_match` | fingerprint-to-legacy-manifest skip match | `services/db_export/skip_policy.py` | private | indirect | Preserve old `.export_state` compatibility |
| `_resolve_export_author_name` | author resolution from `MessageData` | `services/db_export/plan_builder.py` | private | yes | Keep fallback to message author when user card is empty |
| `_resolve_export_author_name_from_rows` | author resolution from export rows | `services/db_export/plan_builder.py` | private | indirect | Used by JSONL fast path planning |
| `format_message` | compatibility rendering entrypoint | `services/db_export/jsonl_renderer.py` / `services/db_export/txt_renderer.py` | public | yes | Keep for tests and legacy callers |
| `_serialize_ai_row` | AI JSONL row serialization | `services/db_export/jsonl_renderer.py` | private | indirect | Deterministic JSONL schema |
| `_write_batch_size` | writer batching policy | `services/db_export/payload_writer.py` | private | yes | Existing tests assert values |
| `_load_export_source` | full export source loading | `services/db_export/source_loader.py` | private | yes | Existing streaming-row tests cover fast path |
| `_load_incremental_export_source` | incremental export source loading | `services/db_export/source_loader.py` | private | yes | Used by incremental update tests |
| `_prepare_export_plan` | output path, author and fingerprint planning | `services/db_export/plan_builder.py` | private | yes | Must preserve filename contract |
| `_maybe_skip_unchanged_export` | final skip decision + telemetry/logging | `services/db_export/skip_policy.py` / `services/db_export/event_emitter.py` | private | yes | Split decision from event emission |
| `_cleanup_existing_export_files` | duplicate artifact cleanup | `services/db_export/payload_writer.py` | private | indirect | Must preserve output directory semantics |
| `_format_txt_export_block` | TXT block formatting | `services/db_export/txt_renderer.py` | private | indirect | Legacy duplicate of package helper |
| `_extract_export_cursor` | derive export cursor from source/fingerprint | `services/db_export/state_manager.py` | private | indirect | Required for export target state |
| `_upsert_export_target_state` | persist export target artifact metadata | `services/db_export/state_manager.py` | private | yes | Part of unchanged/incremental state behavior |
| `_start_export_run` | create export run row | `services/db_export/state_manager.py` | private | indirect | Thin storage orchestration |
| `_resolve_existing_export_path` | resolve current export artifact path | `services/db_export/state_manager.py` | private | indirect | Shared by skip/update paths |
| `_supports_incremental_update` | incremental update eligibility | `services/db_export/state_manager.py` | private | yes | Behavioural gate for append mode |
| `_refresh_export_target_artifact_from_db_state` | refresh artifact metadata from DB summary | `services/db_export/state_manager.py` | private | yes | Used after incremental append |
| `_finish_export_run` | close export run row | `services/db_export/state_manager.py` | private | indirect | Must preserve success/failure bookkeeping |
| `_write_export_payloads` | streaming render + write orchestration | `services/db_export/payload_writer.py` | private | yes | Core hot path to shrink |
| `export_user_messages` | full export orchestration | `services/db_export/service.py` | public | yes | Final facade method |
| `update_user_messages` | incremental export orchestration | `services/db_export/service.py` | public | yes | Final facade method |
