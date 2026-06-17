import sqlite3
from collections.abc import Callable


StartupPhase = Callable[[], None]


def run_startup_phases(
    *,
    create_current_schema: StartupPhase,
    ensure_compatibility_columns: StartupPhase,
    create_indexes: StartupPhase,
    run_legacy_migrations: StartupPhase,
    final_commit: StartupPhase,
) -> None:
    create_current_schema()
    ensure_compatibility_columns()
    create_indexes()
    run_legacy_migrations()
    final_commit()


def create_current_schema(
    conn: sqlite3.Connection,
    *,
    create_tables: Callable[[sqlite3.Connection], None],
    ensure_user_identity_schema: Callable[[sqlite3.Connection], None],
) -> None:
    create_tables(conn)
    ensure_user_identity_schema(conn)


def ensure_compatibility_columns(
    conn: sqlite3.Connection,
    *,
    ensure_export_target_columns: Callable[[sqlite3.Connection], None],
    ensure_sync_target_columns: Callable[[sqlite3.Connection], None],
    ensure_retry_queue_columns: Callable[[sqlite3.Connection], None],
) -> None:
    ensure_export_target_columns(conn)
    ensure_sync_target_columns(conn)
    ensure_retry_queue_columns(conn)
