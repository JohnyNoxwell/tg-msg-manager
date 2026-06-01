import logging
import sqlite3

from .schema import (
    backfill_export_targets,
    backfill_missing_reply_refs,
    context_links_has_chat_scope,
    create_context_link_indexes,
    create_export_runs_indexes,
    create_export_runs_table,
    create_indexes,
    create_missing_reply_ref_indexes,
    create_missing_reply_refs_table,
    create_tables,
    create_target_link_indexes,
    ensure_export_target_columns,
    ensure_retry_queue_columns,
    ensure_sync_target_columns,
    migrate_existing_links,
    migrate_message_context_links_to_chat_safe,
    migrate_message_target_links_metadata,
    migrate_sync_targets_to_composite_pk,
    normalize_context_link_types,
    reclassify_target_link_types,
    resolve_legacy_context_link_chat_id,
    resolve_legacy_target_link_chat_id,
    run_migrations,
    sync_targets_has_composite_primary_key,
    table_exists,
    target_links_has_chat_scope,
    target_links_has_metadata,
)

logger = logging.getLogger(__name__)


class SQLiteSchemaMixin:
    def _init_db(self):
        """Initializes database schema and applies migrations."""
        conn = self._conn
        self._create_tables(conn)
        self._ensure_user_identity_schema(conn)
        self._ensure_export_target_columns(conn)
        self._ensure_sync_target_columns(conn)
        self._ensure_retry_queue_columns(conn)
        self._create_indexes(conn)
        self._run_migrations(conn)
        conn.commit()
        logger.info(
            f"SQLite Storage initialized at {self.db_path} with target attribution support."
        )

    def _create_tables(self, conn: sqlite3.Connection):
        create_tables(conn)

    def _create_indexes(self, conn: sqlite3.Connection):
        create_indexes(
            conn, create_user_identity_indexes=self._create_user_identity_indexes
        )

    def _ensure_sync_target_columns(self, conn: sqlite3.Connection):
        ensure_sync_target_columns(conn)

    def _ensure_export_target_columns(self, conn: sqlite3.Connection):
        ensure_export_target_columns(conn)

    def _ensure_retry_queue_columns(self, conn: sqlite3.Connection):
        ensure_retry_queue_columns(conn)

    def _run_migrations(self, conn: sqlite3.Connection):
        run_migrations(
            conn,
            migrate_existing_links=self.migrate_existing_links,
            sync_targets_has_composite_primary_key=(
                self._sync_targets_has_composite_primary_key
            ),
            migrate_sync_targets_to_composite_pk=(
                self._migrate_sync_targets_to_composite_pk
            ),
            ensure_user_identity_schema=self._ensure_user_identity_schema,
            create_user_identity_indexes=self._create_user_identity_indexes,
            backfill_user_identity_state=self._backfill_user_identity_state,
            migrate_message_context_links_to_chat_safe=(
                self._migrate_message_context_links_to_chat_safe
            ),
            migrate_message_target_links_metadata=(
                self._migrate_message_target_links_metadata
            ),
            backfill_export_targets=self._backfill_export_targets,
            create_export_runs_table=self._create_export_runs_table,
            create_export_runs_indexes=self._create_export_runs_indexes,
            create_missing_reply_refs_table=self._create_missing_reply_refs_table,
            create_missing_reply_ref_indexes=self._create_missing_reply_ref_indexes,
            backfill_missing_reply_refs=self._backfill_missing_reply_refs,
            normalize_context_link_types=self._normalize_context_link_types,
            create_context_link_indexes=self._create_context_link_indexes,
            reclassify_target_link_types=self._reclassify_target_link_types,
            ensure_export_target_columns=self._ensure_export_target_columns,
        )

    def _create_context_link_indexes(self, conn: sqlite3.Connection):
        create_context_link_indexes(conn)

    def _create_target_link_indexes(self, conn: sqlite3.Connection):
        create_target_link_indexes(conn)

    def _create_missing_reply_ref_indexes(self, conn: sqlite3.Connection):
        create_missing_reply_ref_indexes(conn)

    def _context_links_has_chat_scope(self, conn: sqlite3.Connection) -> bool:
        return context_links_has_chat_scope(conn)

    def _target_links_has_chat_scope(self, conn: sqlite3.Connection) -> bool:
        return target_links_has_chat_scope(conn)

    def _target_links_has_metadata(self, conn: sqlite3.Connection) -> bool:
        return target_links_has_metadata(conn)

    def _migrate_message_context_links_to_chat_safe(self, conn: sqlite3.Connection):
        migrate_message_context_links_to_chat_safe(conn)

    def _normalize_context_link_types(self, conn: sqlite3.Connection):
        normalize_context_link_types(conn)

    def _migrate_message_target_links_metadata(self, conn: sqlite3.Connection):
        migrate_message_target_links_metadata(conn)

    def _reclassify_target_link_types(self, conn: sqlite3.Connection):
        reclassify_target_link_types(conn)

    def _resolve_legacy_context_link_chat_id(
        self,
        conn: sqlite3.Connection,
        *,
        message_id: int,
        context_message_id: int,
    ) -> int:
        return resolve_legacy_context_link_chat_id(
            conn,
            message_id=message_id,
            context_message_id=context_message_id,
        )

    def _resolve_legacy_target_link_chat_id(
        self,
        conn: sqlite3.Connection,
        *,
        message_id: int,
    ) -> int:
        return resolve_legacy_target_link_chat_id(conn, message_id=message_id)

    def _table_exists(self, conn: sqlite3.Connection, table_name: str) -> bool:
        return table_exists(conn, table_name)

    def _backfill_export_targets(self, conn: sqlite3.Connection):
        backfill_export_targets(conn)

    def _create_export_runs_table(self, conn: sqlite3.Connection):
        create_export_runs_table(conn)

    def _create_export_runs_indexes(self, conn: sqlite3.Connection):
        create_export_runs_indexes(conn)

    def _create_missing_reply_refs_table(self, conn: sqlite3.Connection):
        create_missing_reply_refs_table(conn)

    def _backfill_missing_reply_refs(self, conn: sqlite3.Connection):
        backfill_missing_reply_refs(conn)

    def _migrate_sync_targets_to_composite_pk(self):
        """Migration helper to move sync_targets to composite PRIMARY KEY."""
        migrate_sync_targets_to_composite_pk(self._conn)

    @staticmethod
    def _sync_targets_has_composite_primary_key(conn: sqlite3.Connection) -> bool:
        return sync_targets_has_composite_primary_key(conn)

    def migrate_existing_links(self):
        """
        Retroactively populates message_target_links for existing data.
        """
        migrate_existing_links(self._write_transaction)
