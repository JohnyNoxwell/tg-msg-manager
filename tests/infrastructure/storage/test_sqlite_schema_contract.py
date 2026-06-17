import sqlite3

from tg_msg_manager.infrastructure.storage.sqlite import SQLiteStorage


CURRENT_SCHEMA_VERSION = 14


def _close_storage(storage: SQLiteStorage) -> None:
    storage._conn.close()


def _connect(path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _user_version(path) -> int:
    with _connect(path) as conn:
        return int(conn.execute("PRAGMA user_version").fetchone()[0])


def _table_names(conn: sqlite3.Connection) -> set[str]:
    return {
        row["name"]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
        if not row["name"].startswith("sqlite_")
    }


def _columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}


def _primary_key(conn: sqlite3.Connection, table: str) -> list[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return [
        row["name"]
        for row in sorted((row for row in rows if row["pk"]), key=lambda row: row["pk"])
    ]


def _index_names(conn: sqlite3.Connection) -> set[str]:
    return {
        row["name"]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'index'"
        ).fetchall()
        if not row["name"].startswith("sqlite_")
    }


def _schema_snapshot(
    path,
) -> tuple[list[tuple[str, str, str, str]], dict[str, tuple[tuple]]]:
    with _connect(path) as conn:
        objects = [
            (row["type"], row["name"], row["tbl_name"], row["sql"] or "")
            for row in conn.execute(
                """
                SELECT type, name, tbl_name, sql
                FROM sqlite_master
                WHERE type IN ('table', 'index')
                  AND name NOT LIKE 'sqlite_%'
                ORDER BY type, name
                """
            ).fetchall()
        ]
        columns = {
            table: tuple(
                tuple(row) for row in conn.execute(f"PRAGMA table_info({table})")
            )
            for table in sorted(_table_names(conn))
        }
    return objects, columns


def _row_counts(path) -> dict[str, int]:
    with _connect(path) as conn:
        return {
            table: int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
            for table in sorted(_table_names(conn))
        }


def _create_common_legacy_tables(
    conn: sqlite3.Connection, *, legacy_sync_pk: bool = False
) -> None:
    conn.execute(
        """
        CREATE TABLE users (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            username TEXT,
            phone TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE messages (
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
        """
    )
    pk = "PRIMARY KEY (user_id)" if legacy_sync_pk else "PRIMARY KEY (user_id, chat_id)"
    conn.execute(
        f"""
        CREATE TABLE sync_targets (
            user_id INTEGER,
            chat_id INTEGER,
            author_name TEXT,
            last_msg_id INTEGER DEFAULT 0,
            tail_msg_id INTEGER DEFAULT 0,
            is_complete INTEGER DEFAULT 0,
            added_at INTEGER,
            last_sync_at INTEGER,
            {pk}
        )
        """
    )
    conn.execute(
        "INSERT INTO users (user_id, username) VALUES (?, ?)",
        (1001, "legacy_user"),
    )
    conn.execute(
        """
        INSERT INTO messages (
            chat_id, message_id, user_id, author_name, timestamp, text, media_type,
            reply_to_id, fwd_from_id, context_group_id, raw_payload, payload_hash, schema_version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            5001,
            10,
            1001,
            "Legacy User",
            1700000010,
            "legacy message",
            None,
            None,
            None,
            None,
            '{"username":"legacy_user"}',
            "h10",
            1,
        ),
    )
    conn.execute(
        """
        INSERT INTO sync_targets (
            user_id, chat_id, author_name, added_at, last_sync_at
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (1001, 5001, "Legacy User", 1700000000, 1700000100),
    )


def _create_legacy_database(path, version: int) -> None:
    conn = _connect(path)
    try:
        if version == 0:
            _create_common_legacy_tables(conn, legacy_sync_pk=True)
            conn.execute(
                """
                CREATE TABLE message_target_links (
                    chat_id INTEGER,
                    message_id INTEGER,
                    target_user_id INTEGER,
                    PRIMARY KEY (chat_id, message_id, target_user_id)
                )
                """
            )
        elif version == 5:
            _create_common_legacy_tables(conn)
        elif version == 9:
            _create_common_legacy_tables(conn)
            conn.execute(
                """
                CREATE TABLE export_targets (
                    target_user_id INTEGER PRIMARY KEY,
                    export_filename TEXT,
                    export_dir TEXT,
                    last_exported_message_ts INTEGER,
                    last_exported_message_id INTEGER,
                    last_known_author_name TEXT,
                    last_known_username TEXT,
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL
                )
                """
            )
            conn.execute(
                """
                INSERT INTO export_targets (
                    target_user_id, last_known_author_name, last_known_username, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (1001, "Legacy User", "legacy_user", 1700000000, 1700000100),
            )
        elif version == 10:
            _create_common_legacy_tables(conn)
            conn.execute(
                """
                INSERT INTO messages (
                    chat_id, message_id, user_id, author_name, timestamp, text, media_type,
                    reply_to_id, fwd_from_id, context_group_id, raw_payload, payload_hash, schema_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    5001,
                    11,
                    1001,
                    "Legacy User",
                    1700000020,
                    "orphan reply",
                    None,
                    9999,
                    None,
                    None,
                    "{}",
                    "h11",
                    1,
                ),
            )
        elif version in (12, 13):
            _create_common_legacy_tables(conn)
            if version == 12:
                conn.execute(
                    """
                    CREATE TABLE message_target_links (
                        chat_id INTEGER NOT NULL,
                        message_id INTEGER NOT NULL,
                        target_user_id INTEGER NOT NULL,
                        link_type TEXT NOT NULL DEFAULT 'legacy',
                        created_at INTEGER NOT NULL,
                        PRIMARY KEY (chat_id, message_id, target_user_id)
                    )
                    """
                )
                conn.execute(
                    """
                    INSERT INTO message_target_links (
                        chat_id, message_id, target_user_id, link_type, created_at
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (5001, 10, 1001, "legacy", 1700000200),
                )
            else:
                conn.execute(
                    """
                    CREATE TABLE export_targets (
                        target_user_id INTEGER PRIMARY KEY,
                        export_filename TEXT,
                        export_dir TEXT,
                        last_exported_message_ts INTEGER,
                        last_exported_message_id INTEGER,
                        last_known_author_name TEXT,
                        last_known_username TEXT,
                        created_at INTEGER NOT NULL,
                        updated_at INTEGER NOT NULL
                    )
                    """
                )
                conn.execute(
                    """
                    INSERT INTO export_targets (
                        target_user_id, last_known_author_name, last_known_username, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (1001, "Legacy User", "legacy_user", 1700000000, 1700000100),
                )
        else:
            raise AssertionError(f"unsupported legacy version: {version}")

        conn.execute(f"PRAGMA user_version = {version}")
        conn.commit()
    finally:
        conn.close()


def test_fresh_database_startup_schema_contract(tmp_path):
    db_path = tmp_path / "fresh.db"

    storage = SQLiteStorage(str(db_path))
    _close_storage(storage)

    with _connect(db_path) as conn:
        assert _user_version(db_path) == CURRENT_SCHEMA_VERSION
        assert {
            "messages",
            "users",
            "chats",
            "message_context_links",
            "message_target_links",
            "sync_state",
            "retry_queue",
            "sync_targets",
            "export_targets",
            "export_runs",
            "missing_reply_refs",
            "user_identity_history",
        }.issubset(_table_names(conn))
        assert {
            "chat_id",
            "message_id",
            "user_id",
            "payload_hash",
            "schema_version",
        }.issubset(_columns(conn, "messages"))
        assert {"current_author_name"}.issubset(_columns(conn, "users"))
        assert {"link_type", "distance", "algorithm_version"}.issubset(
            _columns(conn, "message_context_links")
        )
        assert {"link_type", "created_at"}.issubset(
            _columns(conn, "message_target_links")
        )
        assert {"target_user_id", "payload_json", "completed_at"}.issubset(
            _columns(conn, "retry_queue")
        )
        assert {"artifact_message_count", "artifact_json_profile"}.issubset(
            _columns(conn, "export_targets")
        )
        assert _primary_key(conn, "messages") == ["chat_id", "message_id"]
        assert _primary_key(conn, "sync_targets") == ["user_id", "chat_id"]
        assert _primary_key(conn, "message_context_links") == [
            "chat_id",
            "message_id",
            "context_message_id",
            "link_type",
            "algorithm_version",
        ]
        assert _primary_key(conn, "message_target_links") == [
            "chat_id",
            "message_id",
            "target_user_id",
        ]
        assert _primary_key(conn, "missing_reply_refs") == [
            "chat_id",
            "message_id",
            "missing_reply_to_id",
        ]
        assert {
            "idx_msg_user_chat_time",
            "idx_msg_standalone_id",
            "idx_msg_chat_reply",
            "idx_context_links_source",
            "idx_context_links_context",
            "idx_context_links_type",
            "idx_mt_link_target",
            "idx_mt_link_message",
            "idx_mt_link_chat_target_msg",
            "idx_export_targets_updated_at",
            "idx_export_runs_target_started_at",
            "idx_export_runs_status",
            "idx_msg_context_group",
            "idx_retry_queue_due",
            "idx_retry_queue_type",
            "idx_missing_reply_refs_status",
            "idx_missing_reply_refs_parent",
            "idx_users_current_author_name",
            "idx_user_identity_history_user_observed",
        }.issubset(_index_names(conn))


def test_legacy_database_startup_migrations_preserve_data(tmp_path):
    for version in (0, 5, 9, 10, 12, 13):
        db_path = tmp_path / f"legacy_v{version}.db"
        _create_legacy_database(db_path, version)

        storage = SQLiteStorage(str(db_path))
        _close_storage(storage)

        with _connect(db_path) as conn:
            message = conn.execute(
                "SELECT text FROM messages WHERE chat_id = ? AND message_id = ?",
                (5001, 10),
            ).fetchone()
            target = conn.execute(
                "SELECT author_name FROM sync_targets WHERE user_id = ? AND chat_id = ?",
                (1001, 5001),
            ).fetchone()

            assert _user_version(db_path) == CURRENT_SCHEMA_VERSION
            assert message["text"] == "legacy message"
            assert target["author_name"] == "Legacy User"
            assert _primary_key(conn, "sync_targets") == ["user_id", "chat_id"]
            assert "artifact_json_profile" in _columns(conn, "export_targets")

            if version <= 5:
                history = conn.execute(
                    "SELECT author_name FROM user_identity_history WHERE user_id = ?",
                    (1001,),
                ).fetchone()
                assert history["author_name"] == "Legacy User"

            if version == 10:
                missing = conn.execute(
                    """
                    SELECT status
                    FROM missing_reply_refs
                    WHERE chat_id = ? AND message_id = ? AND missing_reply_to_id = ?
                    """,
                    (5001, 11, 9999),
                ).fetchone()
                assert missing["status"] == "missing"

            if version == 12:
                link = conn.execute(
                    """
                    SELECT link_type
                    FROM message_target_links
                    WHERE chat_id = ? AND message_id = ? AND target_user_id = ?
                    """,
                    (5001, 10, 1001),
                ).fetchone()
                assert link["link_type"] == "target_author"


def test_sqlite_startup_is_idempotent_for_existing_database(tmp_path):
    db_path = tmp_path / "idempotent.db"
    _create_legacy_database(db_path, 0)

    storage = SQLiteStorage(str(db_path))
    _close_storage(storage)
    first_schema = _schema_snapshot(db_path)
    first_counts = _row_counts(db_path)
    first_version = _user_version(db_path)

    storage = SQLiteStorage(str(db_path))
    _close_storage(storage)
    second_schema = _schema_snapshot(db_path)
    second_counts = _row_counts(db_path)
    second_version = _user_version(db_path)

    assert first_version == CURRENT_SCHEMA_VERSION
    assert second_version == CURRENT_SCHEMA_VERSION
    assert second_schema == first_schema
    assert second_counts == first_counts
