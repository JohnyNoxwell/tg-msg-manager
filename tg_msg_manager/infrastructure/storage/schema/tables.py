import sqlite3


def create_tables(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            chat_id INTEGER,
            message_id INTEGER,
            user_id INTEGER,
            author_name TEXT,
            timestamp INTEGER,
            text TEXT,
            media_type TEXT,
            reply_to_id INTEGER,
            fwd_from_id INTEGER,
            context_group_id TEXT,
            raw_payload TEXT,
            payload_hash TEXT,
            schema_version INTEGER,
            PRIMARY KEY (chat_id, message_id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            username TEXT,
            phone TEXT,
            current_author_name TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            chat_id INTEGER PRIMARY KEY,
            title TEXT,
            type TEXT
        )
    """)
    # Legacy compatibility relation table. Active hot paths currently rely on
    # messages.reply_to_id, messages.context_group_id, and message_target_links.
    conn.execute("""
        CREATE TABLE IF NOT EXISTS message_context_links (
            chat_id INTEGER NOT NULL,
            message_id INTEGER,
            context_message_id INTEGER,
            link_type TEXT NOT NULL DEFAULT 'unknown',
            distance INTEGER,
            algorithm_version TEXT NOT NULL DEFAULT 'legacy',
            created_at INTEGER NOT NULL,
            PRIMARY KEY (chat_id, message_id, context_message_id, link_type, algorithm_version)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS message_target_links (
            chat_id INTEGER,
            message_id INTEGER,
            target_user_id INTEGER,
            link_type TEXT NOT NULL DEFAULT 'legacy',
            created_at INTEGER NOT NULL,
            PRIMARY KEY (chat_id, message_id, target_user_id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sync_state (
            chat_id INTEGER PRIMARY KEY,
            last_msg_id INTEGER DEFAULT 0,
            last_sync_timestamp INTEGER
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS retry_queue (
            task_id TEXT PRIMARY KEY,
            chat_id INTEGER,
            target_user_id INTEGER,
            task_type TEXT,
            status TEXT DEFAULT 'pending',
            payload_json TEXT DEFAULT '{}',
            retry_count INTEGER DEFAULT 0,
            max_attempts INTEGER DEFAULT 5,
            last_error TEXT,
            next_retry_timestamp INTEGER,
            created_at INTEGER DEFAULT 0,
            updated_at INTEGER DEFAULT 0,
            last_attempt_timestamp INTEGER DEFAULT 0,
            completed_at INTEGER DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sync_targets (
            user_id INTEGER,
            chat_id INTEGER,
            author_name TEXT,
            last_msg_id INTEGER DEFAULT 0,
            tail_msg_id INTEGER DEFAULT 0,
            is_complete INTEGER DEFAULT 0,
            deep_mode INTEGER DEFAULT 0,
            recursive_depth INTEGER DEFAULT 0,
            added_at INTEGER,
            last_sync_at INTEGER,
            PRIMARY KEY (user_id, chat_id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS export_targets (
            target_user_id INTEGER PRIMARY KEY,
            export_filename TEXT,
            export_dir TEXT,
            last_exported_message_ts INTEGER,
            last_exported_message_id INTEGER,
            export_part_count INTEGER,
            artifact_message_count INTEGER,
            artifact_first_message_id INTEGER,
            artifact_last_message_id INTEGER,
            artifact_first_timestamp INTEGER,
            artifact_last_timestamp INTEGER,
            artifact_as_json INTEGER,
            artifact_include_date INTEGER,
            artifact_json_profile TEXT,
            last_known_author_name TEXT,
            last_known_username TEXT,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL
        )
    """)
    create_export_runs_table(conn)
    create_missing_reply_refs_table(conn)


def create_export_runs_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS export_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_user_id INTEGER NOT NULL,
            started_at INTEGER NOT NULL,
            finished_at INTEGER,
            new_messages_count INTEGER NOT NULL DEFAULT 0,
            last_new_message_ts INTEGER,
            status TEXT NOT NULL,
            error TEXT,
            FOREIGN KEY (target_user_id)
                REFERENCES export_targets(target_user_id)
        )
    """
    )


def create_missing_reply_refs_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS missing_reply_refs (
            chat_id INTEGER NOT NULL,
            message_id INTEGER NOT NULL,
            missing_reply_to_id INTEGER NOT NULL,
            detected_at INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'missing',
            PRIMARY KEY (chat_id, message_id, missing_reply_to_id)
        )
    """
    )
