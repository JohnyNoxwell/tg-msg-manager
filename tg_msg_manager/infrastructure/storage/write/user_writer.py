from typing import Optional


def upsert_user(
    storage,
    user_id: int,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    username: Optional[str] = None,
    phone: Optional[str] = None,
    author_name: Optional[str] = None,
):
    with storage._write_transaction() as conn:
        upsert_user_in_conn(
            storage,
            conn,
            user_id,
            first_name,
            last_name,
            username,
            phone,
            author_name,
        )
        storage._record_user_identity_in_conn(
            conn,
            user_id=user_id,
            author_name=author_name,
            username=username,
        )


def upsert_user_in_conn(
    storage,
    conn,
    user_id: int,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    username: Optional[str] = None,
    phone: Optional[str] = None,
    author_name: Optional[str] = None,
):
    normalized_author_name = storage._normalize_identity_text(author_name)
    conn.execute(
        """
        INSERT INTO users (user_id, first_name, last_name, username, phone, current_author_name)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            first_name = COALESCE(excluded.first_name, users.first_name),
            last_name = COALESCE(excluded.last_name, users.last_name),
            username = COALESCE(excluded.username, users.username),
            phone = COALESCE(excluded.phone, users.phone),
            current_author_name = COALESCE(excluded.current_author_name, users.current_author_name)
    """,
        (user_id, first_name, last_name, username, phone, normalized_author_name),
    )
    storage._refresh_target_author_name_in_conn(conn, user_id, normalized_author_name)


def register_target(
    storage,
    user_id: int,
    author_name: str,
    chat_id: int,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    username: Optional[str] = None,
    deep_mode: bool = False,
    recursive_depth: int = 0,
):
    import time

    now = int(time.time())
    with storage._write_transaction() as conn:
        conn.execute(
            """
            INSERT INTO sync_targets (user_id, chat_id, author_name, added_at, last_sync_at, deep_mode, recursive_depth)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, chat_id) DO UPDATE SET
                author_name = excluded.author_name,
                deep_mode = MAX(sync_targets.deep_mode, excluded.deep_mode),
                recursive_depth = MAX(sync_targets.recursive_depth, excluded.recursive_depth)
        """,
            (
                user_id,
                chat_id,
                author_name,
                now,
                now,
                1 if deep_mode else 0,
                recursive_depth,
            ),
        )
        upsert_user_in_conn(
            storage,
            conn,
            user_id,
            first_name,
            last_name,
            username,
            None,
            author_name,
        )
        storage._record_user_identity_in_conn(
            conn,
            user_id=user_id,
            author_name=author_name,
            username=username,
            observed_at=now,
            chat_id=chat_id,
            source_message_id=None,
        )


def upsert_chat(storage, chat_id: int, title: str, chat_type: Optional[str] = None):
    with storage._write_transaction() as conn:
        upsert_chat_in_conn(storage, conn, chat_id, title, chat_type)


def upsert_chat_in_conn(
    storage,
    conn,
    chat_id: int,
    title: str,
    chat_type: Optional[str] = None,
):
    del storage
    conn.execute(
        """
        INSERT INTO chats (chat_id, title, type)
        VALUES (?, ?, ?)
        ON CONFLICT(chat_id) DO UPDATE SET
            title = COALESCE(NULLIF(excluded.title, ''), chats.title),
            type = COALESCE(excluded.type, chats.type)
    """,
        (chat_id, title, chat_type),
    )


def upsert_user_from_payload_in_conn(
    storage,
    conn,
    user_id: int,
    raw: dict,
    *,
    author_name: Optional[str] = None,
    observed_at: Optional[int] = None,
    chat_id: Optional[int] = None,
    source_message_id: Optional[int] = None,
):
    first_name = raw.get("first_name") or ""
    last_name = raw.get("last_name") or ""
    username = raw.get("username") or ""
    phone = raw.get("phone") or ""

    sender = raw.get("sender") or raw.get("_sender") or {}
    if isinstance(sender, dict):
        first_name = first_name or sender.get("first_name", "")
        last_name = last_name or sender.get("last_name", "")
        username = username or sender.get("username", "")
        phone = phone or sender.get("phone", "")

    upsert_user_in_conn(
        storage,
        conn,
        user_id,
        first_name,
        last_name,
        username,
        phone,
        author_name,
    )
    storage._record_user_identity_in_conn(
        conn,
        user_id=user_id,
        author_name=author_name,
        username=username,
        observed_at=observed_at,
        chat_id=chat_id,
        source_message_id=source_message_id,
    )
