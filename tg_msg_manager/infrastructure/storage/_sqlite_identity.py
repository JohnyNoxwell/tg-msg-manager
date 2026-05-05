import json
import time
from typing import Optional


class SQLiteIdentityMixin:
    def _ensure_user_identity_schema(self, conn) -> None:
        try:
            conn.execute("ALTER TABLE users ADD COLUMN current_author_name TEXT")
        except Exception:
            pass

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_identity_history (
                user_id INTEGER NOT NULL,
                observed_at INTEGER NOT NULL,
                author_name TEXT,
                username TEXT,
                chat_id INTEGER,
                source_message_id INTEGER,
                PRIMARY KEY (user_id, observed_at)
            )
        """
        )

    def _create_user_identity_indexes(self, conn) -> None:
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_users_current_author_name
            ON users (current_author_name)
        """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_user_identity_history_user_observed
            ON user_identity_history (user_id, observed_at DESC)
        """
        )

    def _normalize_identity_text(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _extract_username_from_raw_payload(self, raw_payload) -> Optional[str]:
        payload = raw_payload
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except Exception:
                return None
        if not isinstance(payload, dict):
            return None

        username = payload.get("username")
        if username:
            return self._normalize_identity_text(username)

        sender = payload.get("sender") or payload.get("_sender") or {}
        if isinstance(sender, dict):
            return self._normalize_identity_text(sender.get("username"))
        return None

    def _record_user_identity_in_conn(
        self,
        conn,
        *,
        user_id: int,
        author_name: Optional[str] = None,
        username: Optional[str] = None,
        observed_at: Optional[int] = None,
        chat_id: Optional[int] = None,
        source_message_id: Optional[int] = None,
    ) -> None:
        normalized_author = self._normalize_identity_text(author_name)
        normalized_username = self._normalize_identity_text(username)
        if normalized_author is None and normalized_username is None:
            return

        latest = conn.execute(
            """
            SELECT author_name, username
            FROM user_identity_history
            WHERE user_id = ?
            ORDER BY observed_at DESC, COALESCE(source_message_id, 0) DESC
            LIMIT 1
        """,
            (user_id,),
        ).fetchone()
        if (
            latest
            and latest["author_name"] == normalized_author
            and latest["username"] == normalized_username
        ):
            return

        resolved_observed_at = int(observed_at or time.time())
        conn.execute(
            """
            INSERT INTO user_identity_history (
                user_id,
                observed_at,
                author_name,
                username,
                chat_id,
                source_message_id
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, observed_at) DO UPDATE SET
                author_name = COALESCE(user_identity_history.author_name, excluded.author_name),
                username = COALESCE(user_identity_history.username, excluded.username),
                chat_id = COALESCE(user_identity_history.chat_id, excluded.chat_id),
                source_message_id = COALESCE(user_identity_history.source_message_id, excluded.source_message_id)
        """,
            (
                user_id,
                resolved_observed_at,
                normalized_author,
                normalized_username,
                chat_id,
                source_message_id,
            ),
        )

    def _refresh_target_author_name_in_conn(
        self, conn, user_id: int, author_name: Optional[str]
    ) -> None:
        normalized_author = self._normalize_identity_text(author_name)
        if normalized_author is None:
            return
        conn.execute(
            """
            UPDATE sync_targets
            SET author_name = ?
            WHERE user_id = ?
        """,
            (normalized_author, user_id),
        )

    def _backfill_user_identity_state(self, conn) -> None:
        conn.execute(
            """
            INSERT OR IGNORE INTO users (user_id)
            SELECT DISTINCT user_id
            FROM messages
            WHERE user_id IS NOT NULL
        """
        )
        conn.execute(
            """
            INSERT OR IGNORE INTO users (user_id, current_author_name)
            SELECT DISTINCT user_id, author_name
            FROM sync_targets
            WHERE user_id IS NOT NULL
        """
        )

        rows = conn.execute(
            """
            SELECT user_id, chat_id, message_id, timestamp, author_name, raw_payload
            FROM messages
            WHERE user_id IS NOT NULL
            ORDER BY user_id ASC, timestamp ASC, message_id ASC
        """
        ).fetchall()

        for row in rows:
            self._record_user_identity_in_conn(
                conn,
                user_id=int(row["user_id"]),
                author_name=row["author_name"],
                username=self._extract_username_from_raw_payload(row["raw_payload"]),
                observed_at=int(row["timestamp"] or 0),
                chat_id=int(row["chat_id"] or 0),
                source_message_id=int(row["message_id"] or 0),
            )

        target_rows = conn.execute(
            """
            SELECT
                t.user_id,
                t.chat_id,
                t.author_name,
                u.username,
                COALESCE(NULLIF(t.last_sync_at, 0), NULLIF(t.added_at, 0), ?) AS observed_at
            FROM sync_targets t
            LEFT JOIN users u ON u.user_id = t.user_id
            WHERE COALESCE(TRIM(t.author_name), '') != ''
            ORDER BY t.user_id ASC, observed_at ASC, t.chat_id ASC
        """,
            (int(time.time()),),
        ).fetchall()

        for row in target_rows:
            self._record_user_identity_in_conn(
                conn,
                user_id=int(row["user_id"]),
                author_name=row["author_name"],
                username=row["username"],
                observed_at=int(row["observed_at"] or 0),
                chat_id=int(row["chat_id"] or 0),
                source_message_id=None,
            )

        conn.execute(
            """
            UPDATE users
            SET current_author_name = (
                SELECT m.author_name
                FROM messages m
                WHERE m.user_id = users.user_id
                  AND COALESCE(TRIM(m.author_name), '') != ''
                ORDER BY m.timestamp DESC, m.message_id DESC
                LIMIT 1
            )
            WHERE EXISTS (
                SELECT 1
                FROM messages m
                WHERE m.user_id = users.user_id
                  AND COALESCE(TRIM(m.author_name), '') != ''
            )
        """
        )

        conn.execute(
            """
            UPDATE users
            SET current_author_name = (
                SELECT t.author_name
                FROM sync_targets t
                WHERE t.user_id = users.user_id
                  AND COALESCE(TRIM(t.author_name), '') != ''
                ORDER BY COALESCE(NULLIF(t.last_sync_at, 0), NULLIF(t.added_at, 0), 0) DESC, t.chat_id DESC
                LIMIT 1
            )
            WHERE COALESCE(TRIM(current_author_name), '') = ''
              AND EXISTS (
                  SELECT 1
                  FROM sync_targets t
                  WHERE t.user_id = users.user_id
                    AND COALESCE(TRIM(t.author_name), '') != ''
              )
        """
        )
