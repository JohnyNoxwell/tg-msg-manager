import sqlite3


def create_sqlite_connection(
    db_path: str, *, enable_wal: bool = True
) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    if enable_wal:
        conn.execute("PRAGMA journal_mode=WAL;")
    conn.row_factory = sqlite3.Row
    return conn
