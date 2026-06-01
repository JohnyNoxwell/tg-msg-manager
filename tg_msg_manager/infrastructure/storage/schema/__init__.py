from .backfills import (
    backfill_export_targets,
    backfill_missing_reply_refs,
    normalize_context_link_types,
    reclassify_target_link_types,
)
from .compat import (
    ensure_export_target_columns,
    ensure_retry_queue_columns,
    ensure_sync_target_columns,
    migrate_existing_links,
    migrate_message_context_links_to_chat_safe,
    migrate_message_target_links_metadata,
    migrate_sync_targets_to_composite_pk,
    resolve_legacy_context_link_chat_id,
    resolve_legacy_target_link_chat_id,
)
from .indexes import (
    create_context_link_indexes,
    create_export_runs_indexes,
    create_indexes,
    create_missing_reply_ref_indexes,
    create_target_link_indexes,
)
from .inspection import (
    context_links_has_chat_scope,
    sync_targets_has_composite_primary_key,
    table_exists,
    target_links_has_chat_scope,
    target_links_has_metadata,
)
from .migrations import run_migrations
from .tables import (
    create_export_runs_table,
    create_missing_reply_refs_table,
    create_tables,
)

__all__ = [
    "backfill_export_targets",
    "backfill_missing_reply_refs",
    "context_links_has_chat_scope",
    "create_context_link_indexes",
    "create_export_runs_indexes",
    "create_export_runs_table",
    "create_indexes",
    "create_missing_reply_ref_indexes",
    "create_missing_reply_refs_table",
    "create_tables",
    "create_target_link_indexes",
    "ensure_export_target_columns",
    "ensure_retry_queue_columns",
    "ensure_sync_target_columns",
    "migrate_existing_links",
    "migrate_message_context_links_to_chat_safe",
    "migrate_message_target_links_metadata",
    "migrate_sync_targets_to_composite_pk",
    "normalize_context_link_types",
    "reclassify_target_link_types",
    "resolve_legacy_context_link_chat_id",
    "resolve_legacy_target_link_chat_id",
    "run_migrations",
    "sync_targets_has_composite_primary_key",
    "table_exists",
    "target_links_has_chat_scope",
    "target_links_has_metadata",
]
