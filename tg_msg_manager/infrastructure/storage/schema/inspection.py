import sqlite3


def context_links_has_chat_scope(conn: sqlite3.Connection) -> bool:
    columns = {
        row["name"]
        for row in conn.execute("PRAGMA table_info(message_context_links)").fetchall()
    }
    return "chat_id" in columns and "algorithm_version" in columns


def target_links_has_chat_scope(conn: sqlite3.Connection) -> bool:
    columns = {
        row["name"]
        for row in conn.execute("PRAGMA table_info(message_target_links)").fetchall()
    }
    return "chat_id" in columns


def target_links_has_metadata(conn: sqlite3.Connection) -> bool:
    columns = {
        row["name"]
        for row in conn.execute("PRAGMA table_info(message_target_links)").fetchall()
    }
    return "chat_id" in columns and "link_type" in columns and "created_at" in columns


def table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE type = 'table' AND name = ?
    """,
        (table_name,),
    ).fetchone()
    return row is not None


def sync_targets_has_composite_primary_key(conn: sqlite3.Connection) -> bool:
    rows = conn.execute("PRAGMA table_info(sync_targets)").fetchall()
    pk_columns = [
        row[1]
        for row in sorted(
            (item for item in rows if item[5]),
            key=lambda item: item[5],
        )
    ]
    return pk_columns == ["user_id", "chat_id"]
