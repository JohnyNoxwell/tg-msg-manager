import sys
import os
import sqlite3
import time
import unittest
from datetime import datetime

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tg_msg_manager.core.models.message import MessageData
from tg_msg_manager.infrastructure.storage.interface import (
    CleanerStorage,
    ContextStorage,
    DBExportStorage,
    ExportStorage,
    PrivateArchiveStorage,
)
from tg_msg_manager.infrastructure.storage.link_types import (
    CONTEXT_ALGO_REPLY_CONTEXT_V1,
    CONTEXT_LINK_REPLY_PARENT,
    validate_context_link_type,
)
from tg_msg_manager.infrastructure.storage.records import (
    DeleteUserDataResult,
    ExportRunRecord,
    ExportTargetRecord,
    PrimaryTarget,
    RetryTaskRecord,
    StoredUser,
    SyncStatus,
    TerminalRepairCandidate,
    TargetMessageBreakdown,
    UserIdentityRecord,
    UserExportRow,
    UserExportSummary,
)
from tg_msg_manager.infrastructure.storage.sqlite import SQLiteStorage


class TestSQLiteStorage(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Use a temporary test database
        self.db_path = "test_storage.db"
        for suffix in ("", "-wal", "-shm"):
            path = f"{self.db_path}{suffix}"
            if os.path.exists(path):
                os.remove(path)
        self.storage = SQLiteStorage(self.db_path)

    def tearDown(self):
        # Cleanup test database
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        if os.path.exists(f"{self.db_path}-wal"):
            os.remove(f"{self.db_path}-wal")
        if os.path.exists(f"{self.db_path}-shm"):
            os.remove(f"{self.db_path}-shm")

    async def test_save_and_get_message(self):
        msg = MessageData(
            message_id=1,
            chat_id=123,
            user_id=456,
            author_name="Test User",
            timestamp=datetime.now(),
            text="Hello SQLite",
            media_type=None,
            reply_to_id=None,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={"test": "data"},
        )

        # Test save
        success = await self.storage.save_message(msg)
        self.assertTrue(success)

        # Test existence
        self.assertTrue(self.storage.message_exists(123, 1))

        # Test retrieval
        retrieved = self.storage.get_message(123, 1)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.message_id, 1)
        self.assertEqual(retrieved.text, "Hello SQLite")
        self.assertEqual(retrieved.raw_payload["test"], "data")

    async def test_sqlite_storage_satisfies_service_protocols(self):
        self.assertIsInstance(self.storage, CleanerStorage)
        self.assertIsInstance(self.storage, ContextStorage)
        self.assertIsInstance(self.storage, DBExportStorage)
        self.assertIsInstance(self.storage, ExportStorage)
        self.assertIsInstance(self.storage, PrivateArchiveStorage)

    async def test_batch_save(self):
        msgs = [
            MessageData(
                message_id=i,
                chat_id=789,
                user_id=1,
                author_name="Batch User",
                timestamp=datetime.now(),
                text=f"Batch {i}",
                media_type=None,
                reply_to_id=None,
                fwd_from_id=None,
                context_group_id=None,
                raw_payload={},
            )
            for i in range(1, 11)
        ]

        count = await self.storage.save_messages(msgs)
        self.assertEqual(count, 10)
        self.assertEqual(self.storage.get_last_msg_id(789), 10)

    async def test_upsert_logic(self):
        msg = MessageData(
            message_id=1,
            chat_id=1,
            user_id=1,
            author_name="Orig User",
            timestamp=datetime.now(),
            text="Original",
            media_type=None,
            reply_to_id=None,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={},
        )
        await self.storage.save_message(msg)

        # Update text for the same message_id
        updated_msg = MessageData(
            message_id=1,
            chat_id=1,
            user_id=1,
            author_name="Upd User",
            timestamp=datetime.now(),
            text="Updated",
            media_type=None,
            reply_to_id=None,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={},
        )
        await self.storage.save_message(updated_msg)

        retrieved = self.storage.get_message(1, 1)
        self.assertEqual(retrieved.text, "Updated")

    async def test_payload_hashing(self):
        msg = MessageData(
            message_id=55,
            chat_id=1,
            user_id=1,
            author_name="Hash User",
            timestamp=datetime.now(),
            text="Original",
            media_type=None,
            reply_to_id=None,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={"v": 1},
        )
        await self.storage.save_message(msg)
        h1 = msg.get_payload_hash()

        # Test hash detection
        msg2 = MessageData(
            message_id=55,
            chat_id=1,
            user_id=1,
            author_name="Hash User",
            timestamp=datetime.now(),
            text="Original",
            media_type=None,
            reply_to_id=None,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={"v": 2},
        )
        h2 = msg2.get_payload_hash()
        self.assertNotEqual(h1, h2)

        # Test that update occurs when hash changes
        await self.storage.save_message(msg2)
        retrieved = self.storage.get_message(1, 55)
        self.assertEqual(retrieved.raw_payload["v"], 2)

    async def test_target_checkpoint_uses_target_id(self):
        self.storage.register_target(999, "Target User", 321)
        self.storage.register_target(456, "Author User", 321)

        msg = MessageData(
            message_id=50,
            chat_id=321,
            user_id=456,
            author_name="Author User",
            timestamp=datetime.now(),
            text="Context message",
            media_type=None,
            reply_to_id=None,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={},
        )

        await self.storage.save_message(msg, target_id=999)

        target_status = self.storage.get_sync_status(321, 999)
        author_status = self.storage.get_sync_status(321, 456)
        self.assertIsInstance(target_status, SyncStatus)
        self.assertEqual(target_status["last_msg_id"], 50)
        self.assertEqual(target_status.last_msg_id, 50)
        self.assertEqual(author_status["last_msg_id"], 0)
        self.assertEqual(len(self.storage.get_user_messages(999)), 1)

    async def test_save_message_persists_chat_safe_context_link_metadata(self):
        parent = MessageData(
            message_id=1,
            chat_id=321,
            user_id=999,
            author_name="Parent User",
            timestamp=datetime.now(),
            text="parent",
            media_type=None,
            reply_to_id=None,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={},
        )
        child = MessageData(
            message_id=2,
            chat_id=321,
            user_id=999,
            author_name="Parent User",
            timestamp=datetime.now(),
            text="child",
            media_type=None,
            reply_to_id=1,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={},
        )

        await self.storage.save_message(parent)
        await self.storage.save_message(child)

        with self.storage._read_connection() as conn:
            row = conn.execute(
                """
                SELECT chat_id, message_id, context_message_id, link_type, distance, algorithm_version, created_at
                FROM message_context_links
                WHERE chat_id = ? AND message_id = ? AND context_message_id = ?
            """,
                (321, 2, 1),
            ).fetchone()

        self.assertEqual(row["chat_id"], 321)
        self.assertEqual(row["message_id"], 2)
        self.assertEqual(row["context_message_id"], 1)
        self.assertEqual(row["link_type"], CONTEXT_LINK_REPLY_PARENT)
        self.assertIsNone(row["distance"])
        self.assertEqual(row["algorithm_version"], CONTEXT_ALGO_REPLY_CONTEXT_V1)
        self.assertGreater(row["created_at"], 0)

    async def test_validate_context_link_type_helper_accepts_only_canonical_values(self):
        self.assertTrue(validate_context_link_type(CONTEXT_LINK_REPLY_PARENT))
        self.assertTrue(validate_context_link_type("legacy"))
        self.assertFalse(validate_context_link_type("reply"))
        self.assertFalse(validate_context_link_type("same_topic"))

    async def test_user_export_summary_and_iterator_preserve_deterministic_order(self):
        self.storage.register_target(999, "Target User", 321)
        ts = datetime.fromtimestamp(1700000000)
        msgs = [
            MessageData(
                message_id=2,
                chat_id=321,
                user_id=999,
                author_name="Target User",
                timestamp=ts,
                text="second by id",
                media_type=None,
                reply_to_id=None,
                fwd_from_id=None,
                context_group_id=None,
                raw_payload={},
            ),
            MessageData(
                message_id=1,
                chat_id=321,
                user_id=999,
                author_name="Target User",
                timestamp=ts,
                text="first by id",
                media_type=None,
                reply_to_id=None,
                fwd_from_id=None,
                context_group_id="cluster-1",
                raw_payload={},
            ),
            MessageData(
                message_id=3,
                chat_id=321,
                user_id=555,
                author_name="Context User",
                timestamp=datetime.fromtimestamp(1700000001),
                text="context",
                media_type=None,
                reply_to_id=1,
                fwd_from_id=None,
                context_group_id=None,
                raw_payload={},
            ),
        ]

        await self.storage.save_messages(msgs, target_id=999)

        user = self.storage.get_user(999)
        summary = self.storage.get_user_export_summary(999)
        rows = list(self.storage.iter_user_export_rows(999, chunk_size=2))
        targets = self.storage.get_primary_targets()

        self.assertIsInstance(user, StoredUser)
        self.assertIsInstance(summary, UserExportSummary)
        self.assertTrue(targets)
        self.assertIsInstance(targets[0], PrimaryTarget)
        self.assertIsInstance(rows[0], UserExportRow)
        self.assertEqual(user.user_id, 999)
        self.assertEqual(user.current_author_name, "Target User")
        self.assertEqual(summary["message_count"], 3)
        self.assertEqual(summary.message_count, 3)
        self.assertEqual(summary["first_message_id"], 1)
        self.assertEqual(summary["last_message_id"], 3)
        self.assertEqual(summary["target_author_name"], "Target User")
        self.assertEqual(targets[0].user_id, 999)
        self.assertEqual(targets[0].user_msg_count, 2)
        self.assertEqual(targets[0].context_msg_count, 1)
        self.assertEqual([row["message_id"] for row in rows], [1, 2, 3])
        self.assertEqual(rows[0].context_group_id, "cluster-1")

    async def test_register_target_preserves_last_sync_at_on_existing_target(self):
        self.storage.register_target(999, "Target User", 321)
        with self.storage._read_connection() as conn:
            before = conn.execute(
                "SELECT last_sync_at FROM sync_targets WHERE user_id = ? AND chat_id = ?",
                (999, 321),
            ).fetchone()["last_sync_at"]

        time.sleep(1)
        self.storage.register_target(999, "Target User Renamed", 321)

        with self.storage._read_connection() as conn:
            row = conn.execute(
                "SELECT author_name, last_sync_at FROM sync_targets WHERE user_id = ? AND chat_id = ?",
                (999, 321),
            ).fetchone()

        self.assertEqual(row["author_name"], "Target User Renamed")
        self.assertEqual(row["last_sync_at"], before)

        user = self.storage.get_user(999)
        history = self.storage.get_user_identity_history(999)

        self.assertEqual(user.current_author_name, "Target User Renamed")
        self.assertEqual([item.author_name for item in history], ["Target User", "Target User Renamed"])

    async def test_save_message_refreshes_target_current_author_name_and_history(self):
        self.storage.register_target(999, "Target User", 321)
        ts = datetime.now()

        await self.storage.save_message(
            MessageData(
                message_id=10,
                chat_id=321,
                user_id=999,
                author_name="Target User",
                timestamp=ts,
                text="before rename",
                media_type=None,
                reply_to_id=None,
                fwd_from_id=None,
                context_group_id=None,
                raw_payload={"username": "target_user"},
            ),
            target_id=999,
        )
        await self.storage.save_message(
            MessageData(
                message_id=11,
                chat_id=321,
                user_id=999,
                author_name="Renamed User",
                timestamp=datetime.fromtimestamp(int(ts.timestamp()) + 10),
                text="after rename",
                media_type=None,
                reply_to_id=None,
                fwd_from_id=None,
                context_group_id=None,
                raw_payload={"username": "target_user"},
            ),
            target_id=999,
        )

        user = self.storage.get_user(999)
        status = self.storage.get_sync_status(321, 999)
        targets = self.storage.get_primary_targets()
        history = self.storage.get_user_identity_history(999)

        self.assertEqual(user.current_author_name, "Renamed User")
        self.assertEqual(status.author_name, "Renamed User")
        self.assertEqual(targets[0].author_name, "Renamed User")
        self.assertTrue(all(isinstance(item, UserIdentityRecord) for item in history))
        self.assertEqual([item.author_name for item in history], ["Target User", "Renamed User"])
        self.assertEqual(history[-1].chat_id, 321)
        self.assertEqual(history[-1].source_message_id, 11)

    async def test_checkpoint_updates_do_not_refresh_last_sync_at(self):
        self.storage.register_target(999, "Target User", 321)
        with self.storage._read_connection() as conn:
            before = conn.execute(
                "SELECT last_sync_at FROM sync_targets WHERE user_id = ? AND chat_id = ?",
                (999, 321),
            ).fetchone()["last_sync_at"]

        time.sleep(1)
        self.storage.update_last_msg_id(321, 999, 50)
        self.storage.update_sync_tail(321, 999, 10, is_complete=False)

        with self.storage._read_connection() as conn:
            row = conn.execute(
                "SELECT last_msg_id, tail_msg_id, is_complete, last_sync_at FROM sync_targets WHERE user_id = ? AND chat_id = ?",
                (999, 321),
            ).fetchone()

        self.assertEqual(row["last_msg_id"], 50)
        self.assertEqual(row["tail_msg_id"], 10)
        self.assertEqual(row["is_complete"], 0)
        self.assertEqual(row["last_sync_at"], before)

    async def test_identity_migration_backfills_current_name_and_history(self):
        await self.storage.close()
        for suffix in ("", "-wal", "-shm"):
            path = f"{self.db_path}{suffix}"
            if os.path.exists(path):
                os.remove(path)

        conn = sqlite3.connect(self.db_path)
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
        conn.execute(
            """
            CREATE TABLE sync_targets (
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
        """
        )
        conn.execute(
            "INSERT INTO users (user_id, username) VALUES (?, ?)",
            (999, "stable_user"),
        )
        conn.execute(
            """
            INSERT INTO messages (
                chat_id, message_id, user_id, author_name, timestamp, text, media_type,
                reply_to_id, fwd_from_id, context_group_id, raw_payload, payload_hash, schema_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                321,
                1,
                999,
                "Old Name",
                1700000000,
                "before",
                None,
                None,
                None,
                None,
                '{"username":"stable_user"}',
                "h1",
                1,
            ),
        )
        conn.execute(
            """
            INSERT INTO messages (
                chat_id, message_id, user_id, author_name, timestamp, text, media_type,
                reply_to_id, fwd_from_id, context_group_id, raw_payload, payload_hash, schema_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                321,
                2,
                999,
                "New Name",
                1700001000,
                "after",
                None,
                None,
                None,
                None,
                '{"username":"stable_user"}',
                "h2",
                1,
            ),
        )
        conn.execute(
            """
            INSERT INTO sync_targets (
                user_id, chat_id, author_name, added_at, last_sync_at
            ) VALUES (?, ?, ?, ?, ?)
        """,
            (999, 321, "Old Name", 1700000000, 1700001000),
        )
        conn.execute("PRAGMA user_version = 5")
        conn.commit()
        conn.close()

        self.storage = SQLiteStorage(self.db_path)

        user = self.storage.get_user(999)
        history = self.storage.get_user_identity_history(999)

        self.assertEqual(user.current_author_name, "New Name")
        self.assertEqual([item.author_name for item in history], ["Old Name", "New Name"])

    async def test_upsert_and_get_export_target(self):
        self.storage.upsert_export_target(
            target_user_id=999,
            export_filename="Stable_User_999.jsonl",
            export_dir="DB_EXPORTS",
            last_exported_message_ts=1700001000,
            last_exported_message_id=77,
            last_known_author_name="Stable User",
            last_known_username="stable",
        )

        record = self.storage.get_export_target(999)

        self.assertIsInstance(record, ExportTargetRecord)
        self.assertEqual(record.target_user_id, 999)
        self.assertEqual(record.export_filename, "Stable_User_999.jsonl")
        self.assertEqual(record.export_dir, "DB_EXPORTS")
        self.assertEqual(record.last_exported_message_ts, 1700001000)
        self.assertEqual(record.last_exported_message_id, 77)
        self.assertEqual(record.last_known_author_name, "Stable User")
        self.assertEqual(record.last_known_username, "stable")

    async def test_start_finish_and_list_export_runs(self):
        self.storage.upsert_export_target(
            target_user_id=999,
            last_known_author_name="Stable User",
        )

        run_id = self.storage.start_export_run(target_user_id=999)
        self.storage.finish_export_run(
            run_id,
            status="success",
            new_messages_count=12,
            last_new_message_ts=1700001234,
        )

        runs = self.storage.list_export_runs(999)

        self.assertEqual(len(runs), 1)
        self.assertIsInstance(runs[0], ExportRunRecord)
        self.assertEqual(runs[0].id, run_id)
        self.assertEqual(runs[0].target_user_id, 999)
        self.assertEqual(runs[0].status, "success")
        self.assertEqual(runs[0].new_messages_count, 12)
        self.assertEqual(runs[0].last_new_message_ts, 1700001234)
        self.assertIsNotNone(runs[0].finished_at)

    async def test_get_incremental_export_rows_and_summary_since_cursor(self):
        self.storage.register_target(999, "Stable User", 321)
        old_message = MessageData(
            message_id=7,
            chat_id=321,
            user_id=999,
            author_name="Stable User",
            timestamp=datetime.fromtimestamp(1700001234),
            text="old",
            media_type=None,
            reply_to_id=None,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={},
        )
        new_message = MessageData(
            message_id=8,
            chat_id=321,
            user_id=999,
            author_name="Stable User",
            timestamp=datetime.fromtimestamp(1700002234),
            text="new",
            media_type=None,
            reply_to_id=None,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={},
        )
        await self.storage.save_message(old_message, target_id=999)
        await self.storage.save_message(new_message, target_id=999)

        summary = self.storage.get_user_export_summary_since(999, 1700001234, 7)
        rows = list(self.storage.iter_user_export_rows_since(999, 1700001234, 7))

        self.assertIsNotNone(summary)
        self.assertEqual(summary.message_count, 1)
        self.assertEqual(summary.first_message_id, 8)
        self.assertEqual(summary.last_message_id, 8)
        self.assertEqual(summary.first_timestamp, 1700002234)
        self.assertEqual(summary.last_timestamp, 1700002234)
        self.assertEqual([row.message_id for row in rows], [8])

    async def test_missing_reply_refs_track_missing_and_resolved_parent(self):
        child = MessageData(
            message_id=2,
            chat_id=321,
            user_id=999,
            author_name="Child",
            timestamp=datetime.fromtimestamp(1700000010),
            text="child",
            media_type=None,
            reply_to_id=1,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={},
        )
        await self.storage.save_message(child)

        with self.storage._read_connection() as conn:
            missing_row = conn.execute(
                """
                SELECT chat_id, message_id, missing_reply_to_id, status
                FROM missing_reply_refs
                WHERE chat_id = ? AND message_id = ? AND missing_reply_to_id = ?
            """,
                (321, 2, 1),
            ).fetchone()

        self.assertIsNotNone(missing_row)
        self.assertEqual(missing_row["status"], "missing")

        parent = MessageData(
            message_id=1,
            chat_id=321,
            user_id=555,
            author_name="Parent",
            timestamp=datetime.fromtimestamp(1700000000),
            text="parent",
            media_type=None,
            reply_to_id=None,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={},
        )
        await self.storage.save_message(parent)

        with self.storage._read_connection() as conn:
            resolved_row = conn.execute(
                """
                SELECT status
                FROM missing_reply_refs
                WHERE chat_id = ? AND message_id = ? AND missing_reply_to_id = ?
            """,
                (321, 2, 1),
            ).fetchone()

        self.assertEqual(resolved_row["status"], "resolved")

    async def test_missing_reply_refs_migration_backfills_existing_orphans(self):
        await self.storage.close()
        for suffix in ("", "-wal", "-shm"):
            path = f"{self.db_path}{suffix}"
            if os.path.exists(path):
                os.remove(path)

        conn = sqlite3.connect(self.db_path)
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
        conn.execute(
            """
            INSERT INTO messages (
                chat_id, message_id, user_id, author_name, timestamp, text, media_type,
                reply_to_id, fwd_from_id, context_group_id, raw_payload, payload_hash, schema_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (321, 2, 999, "Child", 1700000010, "child", None, 1, None, None, "{}", "p2", 1),
        )
        conn.execute("PRAGMA user_version = 10")
        conn.commit()
        conn.close()

        self.storage = SQLiteStorage(self.db_path)

        with self.storage._read_connection() as conn:
            row = conn.execute(
                """
                SELECT chat_id, message_id, missing_reply_to_id, status
                FROM missing_reply_refs
            """
            ).fetchone()
            version = conn.execute("PRAGMA user_version").fetchone()[0]

        self.assertEqual(row["chat_id"], 321)
        self.assertEqual(row["message_id"], 2)
        self.assertEqual(row["missing_reply_to_id"], 1)
        self.assertEqual(row["status"], "missing")
        self.assertEqual(version, 12)

    async def test_export_runs_migration_creates_table_for_version_9_databases(self):
        await self.storage.close()
        for suffix in ("", "-wal", "-shm"):
            path = f"{self.db_path}{suffix}"
            if os.path.exists(path):
                os.remove(path)

        conn = sqlite3.connect(self.db_path)
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
        conn.execute("PRAGMA user_version = 9")
        conn.commit()
        conn.close()

        self.storage = SQLiteStorage(self.db_path)

        with self.storage._read_connection() as conn:
            table = conn.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table' AND name = 'export_runs'
            """
            ).fetchone()
            version = conn.execute("PRAGMA user_version").fetchone()[0]

        self.assertIsNotNone(table)
        self.assertEqual(version, 12)

    async def test_export_targets_migration_backfills_tracked_users(self):
        await self.storage.close()
        for suffix in ("", "-wal", "-shm"):
            path = f"{self.db_path}{suffix}"
            if os.path.exists(path):
                os.remove(path)

        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                username TEXT,
                phone TEXT,
                current_author_name TEXT
            )
        """
        )
        conn.execute(
            """
            CREATE TABLE sync_targets (
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
        """
        )
        conn.execute(
            "INSERT INTO users (user_id, username, current_author_name) VALUES (?, ?, ?)",
            (999, "stable", "Stable User"),
        )
        conn.execute(
            """
            INSERT INTO sync_targets (
                user_id, chat_id, author_name, added_at, last_sync_at
            ) VALUES (?, ?, ?, ?, ?)
        """,
            (999, 321, "Old User", 1700000000, 1700001000),
        )
        conn.execute("PRAGMA user_version = 8")
        conn.commit()
        conn.close()

        self.storage = SQLiteStorage(self.db_path)

        record = self.storage.get_export_target(999)

        self.assertIsInstance(record, ExportTargetRecord)
        self.assertEqual(record.target_user_id, 999)
        self.assertIsNone(record.export_filename)
        self.assertIsNone(record.export_dir)
        self.assertIsNone(record.last_exported_message_ts)
        self.assertIsNone(record.last_exported_message_id)
        self.assertEqual(record.last_known_author_name, "Stable User")
        self.assertEqual(record.last_known_username, "stable")
        self.assertGreater(record.created_at, 0)
        self.assertGreater(record.updated_at, 0)

    async def test_context_link_migration_backfills_chat_safe_rows_and_keeps_backup(self):
        await self.storage.close()
        for suffix in ("", "-wal", "-shm"):
            path = f"{self.db_path}{suffix}"
            if os.path.exists(path):
                os.remove(path)

        conn = sqlite3.connect(self.db_path)
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
        conn.execute(
            """
            CREATE TABLE message_context_links (
                message_id INTEGER,
                context_message_id INTEGER,
                link_type TEXT,
                PRIMARY KEY (message_id, context_message_id)
            )
        """
        )
        conn.execute(
            """
            INSERT INTO messages (
                chat_id, message_id, user_id, author_name, timestamp, text, media_type,
                reply_to_id, fwd_from_id, context_group_id, raw_payload, payload_hash, schema_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (321, 1, 999, "Parent", 1700000000, "parent", None, None, None, None, "{}", "p1", 1),
        )
        conn.execute(
            """
            INSERT INTO messages (
                chat_id, message_id, user_id, author_name, timestamp, text, media_type,
                reply_to_id, fwd_from_id, context_group_id, raw_payload, payload_hash, schema_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (321, 2, 999, "Child", 1700000010, "child", None, 1, None, None, "{}", "p2", 1),
        )
        conn.execute(
            """
            INSERT INTO message_context_links (message_id, context_message_id, link_type)
            VALUES (?, ?, ?)
        """,
            (2, 1, "reply"),
        )
        conn.execute("PRAGMA user_version = 6")
        conn.commit()
        conn.close()

        self.storage = SQLiteStorage(self.db_path)

        with self.storage._read_connection() as conn:
            row = conn.execute(
                """
                SELECT chat_id, message_id, context_message_id, link_type, distance, algorithm_version, created_at
                FROM message_context_links
            """
            ).fetchone()
            backup_row = conn.execute(
                """
                SELECT message_id, context_message_id, link_type
                FROM message_context_links_legacy_backup
            """
            ).fetchone()

        self.assertEqual(row["chat_id"], 321)
        self.assertEqual(row["message_id"], 2)
        self.assertEqual(row["context_message_id"], 1)
        self.assertEqual(row["link_type"], "legacy")
        self.assertIsNone(row["distance"])
        self.assertEqual(row["algorithm_version"], "legacy")
        self.assertGreater(row["created_at"], 0)
        self.assertEqual(backup_row["message_id"], 2)
        self.assertEqual(backup_row["context_message_id"], 1)
        self.assertEqual(backup_row["link_type"], "reply")

    async def test_context_link_migration_fails_when_chat_id_is_ambiguous(self):
        await self.storage.close()
        for suffix in ("", "-wal", "-shm"):
            path = f"{self.db_path}{suffix}"
            if os.path.exists(path):
                os.remove(path)

        conn = sqlite3.connect(self.db_path)
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
        conn.execute(
            """
            CREATE TABLE message_context_links (
                message_id INTEGER,
                context_message_id INTEGER,
                link_type TEXT,
                PRIMARY KEY (message_id, context_message_id)
            )
        """
        )
        for chat_id in (321, 654):
            conn.execute(
                """
                INSERT INTO messages (
                    chat_id, message_id, user_id, author_name, timestamp, text, media_type,
                    reply_to_id, fwd_from_id, context_group_id, raw_payload, payload_hash, schema_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (chat_id, 1, 999, "Parent", 1700000000, "parent", None, None, None, None, "{}", f"p1-{chat_id}", 1),
            )
            conn.execute(
                """
                INSERT INTO messages (
                    chat_id, message_id, user_id, author_name, timestamp, text, media_type,
                    reply_to_id, fwd_from_id, context_group_id, raw_payload, payload_hash, schema_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (chat_id, 2, 999, "Child", 1700000010, "child", None, 1, None, None, "{}", f"p2-{chat_id}", 1),
            )
        conn.execute(
            """
            INSERT INTO message_context_links (message_id, context_message_id, link_type)
            VALUES (?, ?, ?)
        """,
            (2, 1, "reply"),
        )
        conn.execute("PRAGMA user_version = 6")
        conn.commit()
        conn.close()

        with self.assertRaises(RuntimeError):
            self.storage = SQLiteStorage(self.db_path)

    async def test_context_link_type_normalization_migrates_reply_rows(self):
        await self.storage.close()
        for suffix in ("", "-wal", "-shm"):
            path = f"{self.db_path}{suffix}"
            if os.path.exists(path):
                os.remove(path)

        conn = sqlite3.connect(self.db_path)
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
        conn.execute(
            """
            CREATE TABLE message_context_links (
                chat_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                context_message_id INTEGER NOT NULL,
                link_type TEXT NOT NULL DEFAULT 'unknown',
                distance INTEGER,
                algorithm_version TEXT NOT NULL DEFAULT 'legacy',
                created_at INTEGER NOT NULL,
                PRIMARY KEY (chat_id, message_id, context_message_id, link_type, algorithm_version)
            )
        """
        )
        conn.execute(
            """
            INSERT INTO messages (
                chat_id, message_id, user_id, author_name, timestamp, text, media_type,
                reply_to_id, fwd_from_id, context_group_id, raw_payload, payload_hash, schema_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (321, 1, 111, "Parent", 1700000000, "parent", None, None, None, None, "{}", "p1", 1),
        )
        conn.execute(
            """
            INSERT INTO messages (
                chat_id, message_id, user_id, author_name, timestamp, text, media_type,
                reply_to_id, fwd_from_id, context_group_id, raw_payload, payload_hash, schema_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (321, 2, 222, "Child", 1700000010, "child", None, 1, None, None, "{}", "p2", 1),
        )
        conn.execute(
            """
            INSERT INTO message_context_links (
                chat_id,
                message_id,
                context_message_id,
                link_type,
                distance,
                algorithm_version,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (321, 2, 1, "reply", 1, "reply_chain_v1", 1700000020),
        )
        conn.execute("PRAGMA user_version = 11")
        conn.commit()
        conn.close()

        self.storage = SQLiteStorage(self.db_path)

        with self.storage._read_connection() as conn:
            row = conn.execute(
                """
                SELECT link_type, distance, algorithm_version
                FROM message_context_links
            """
            ).fetchone()
            index_row = conn.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'index' AND name = 'idx_context_links_type'
            """
            ).fetchone()
            version = conn.execute("PRAGMA user_version").fetchone()[0]

        self.assertEqual(row["link_type"], CONTEXT_LINK_REPLY_PARENT)
        self.assertIsNone(row["distance"])
        self.assertEqual(row["algorithm_version"], CONTEXT_ALGO_REPLY_CONTEXT_V1)
        self.assertIsNotNone(index_row)
        self.assertEqual(version, 12)

    async def test_repair_terminal_incomplete_targets_marks_only_tail_threshold_rows_complete(
        self,
    ):
        self.storage.register_target(999, "Tail One", 321)
        self.storage.register_target(888, "Still Incomplete", 321)

        with self.storage._write_transaction() as conn:
            conn.execute(
                """
                UPDATE sync_targets
                SET last_msg_id = ?, tail_msg_id = ?, is_complete = ?, last_sync_at = ?
                WHERE user_id = ? AND chat_id = ?
                """,
                (50, 1, 0, 1234567890, 999, 321),
            )
            conn.execute(
                """
                UPDATE sync_targets
                SET last_msg_id = ?, tail_msg_id = ?, is_complete = ?, last_sync_at = ?
                WHERE user_id = ? AND chat_id = ?
                """,
                (60, 5, 0, 1234567891, 888, 321),
            )

        repaired = self.storage.repair_terminal_incomplete_targets()

        self.assertEqual(len(repaired), 1)
        self.assertIsInstance(repaired[0], TerminalRepairCandidate)
        self.assertEqual(repaired[0]["user_id"], 999)
        self.assertEqual(repaired[0].user_id, 999)

        with self.storage._read_connection() as conn:
            repaired_row = conn.execute(
                "SELECT tail_msg_id, is_complete, last_sync_at FROM sync_targets WHERE user_id = ? AND chat_id = ?",
                (999, 321),
            ).fetchone()
            pending_row = conn.execute(
                "SELECT tail_msg_id, is_complete, last_sync_at FROM sync_targets WHERE user_id = ? AND chat_id = ?",
                (888, 321),
            ).fetchone()

        self.assertEqual(repaired_row["tail_msg_id"], 0)
        self.assertEqual(repaired_row["is_complete"], 1)
        self.assertEqual(repaired_row["last_sync_at"], 1234567890)
        self.assertEqual(pending_row["tail_msg_id"], 5)
        self.assertEqual(pending_row["is_complete"], 0)
        self.assertEqual(pending_row["last_sync_at"], 1234567891)

    async def test_get_all_message_ids(self):
        msg = MessageData(
            1, 100, 1, "Test User", datetime.now(), "Test", None, None, None, None, {}
        )
        await self.storage.save_message(msg)
        ids = self.storage.get_all_message_ids_for_chat(100)
        self.assertEqual(ids, [1])

    async def test_delete_messages_cleans_target_links(self):
        self.storage.register_target(1, "Target User", 777)
        msg = MessageData(
            message_id=1,
            chat_id=777,
            user_id=1,
            author_name="Target User",
            timestamp=datetime.now(),
            text="Delete me",
            media_type=None,
            reply_to_id=None,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={},
        )

        await self.storage.save_message(msg, target_id=1)
        self.assertEqual(self.storage.get_message_count(777, target_id=1), 1)

        deleted = self.storage.delete_messages(777, [1])
        self.assertEqual(deleted, 1)
        self.assertEqual(self.storage.get_message_count(777, target_id=1), 0)

        with self.storage._get_connection() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS count FROM message_target_links WHERE chat_id = ? AND message_id = ? AND target_user_id = ?",
                (777, 1, 1),
            ).fetchone()
            self.assertEqual(row["count"], 0)

    async def test_save_message_persists_target_link_metadata(self):
        self.storage.register_target(1, "Target User", 777)
        own_msg = MessageData(
            message_id=1,
            chat_id=777,
            user_id=1,
            author_name="Target User",
            timestamp=datetime.now(),
            text="Mine",
            media_type=None,
            reply_to_id=None,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={},
        )
        reply_context = MessageData(
            message_id=2,
            chat_id=777,
            user_id=2,
            author_name="Other User",
            timestamp=datetime.now(),
            text="Reply",
            media_type=None,
            reply_to_id=1,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={},
        )

        await self.storage.save_message(own_msg, target_id=1)
        await self.storage.save_message(reply_context, target_id=1)

        with self.storage._read_connection() as conn:
            own_row = conn.execute(
                """
                SELECT link_type, created_at
                FROM message_target_links
                WHERE chat_id = ? AND message_id = ? AND target_user_id = ?
            """,
                (777, 1, 1),
            ).fetchone()
            context_row = conn.execute(
                """
                SELECT link_type, created_at
                FROM message_target_links
                WHERE chat_id = ? AND message_id = ? AND target_user_id = ?
            """,
                (777, 2, 1),
            ).fetchone()

        self.assertEqual(own_row["link_type"], "target_author")
        self.assertGreater(own_row["created_at"], 0)
        self.assertEqual(context_row["link_type"], "reply_context")
        self.assertGreater(context_row["created_at"], 0)

    async def test_filter_missing_target_links_batches_existing_ids(self):
        self.storage.register_target(1, "Target User", 777)
        msg = MessageData(
            message_id=1,
            chat_id=777,
            user_id=1,
            author_name="Target User",
            timestamp=datetime.now(),
            text="Keep me",
            media_type=None,
            reply_to_id=None,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={},
        )

        await self.storage.save_message(msg, target_id=1)
        missing = self.storage.filter_missing_target_links(777, 1, [1, 2, 3])
        self.assertEqual(missing, [2, 3])

    async def test_get_target_message_breakdown_counts_own_and_context(self):
        self.storage.register_target(1, "Target User", 777)
        own_msg = MessageData(
            message_id=1,
            chat_id=777,
            user_id=1,
            author_name="Target User",
            timestamp=datetime.now(),
            text="Mine",
            media_type=None,
            reply_to_id=None,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={},
        )
        context_msg = MessageData(
            message_id=2,
            chat_id=777,
            user_id=2,
            author_name="Other User",
            timestamp=datetime.now(),
            text="Context",
            media_type=None,
            reply_to_id=1,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={},
        )

        await self.storage.save_message(own_msg, target_id=1)
        await self.storage.save_message(context_msg, target_id=1)
        breakdown = self.storage.get_target_message_breakdown(777, 1)
        self.assertIsInstance(breakdown, TargetMessageBreakdown)
        self.assertEqual(breakdown["own_messages"], 1)
        self.assertEqual(breakdown["with_context"], 2)
        self.assertEqual(breakdown.own_messages, 1)
        self.assertEqual(breakdown.with_context, 2)

    async def test_target_link_migration_adds_metadata_and_keeps_backup(self):
        await self.storage.close()
        for suffix in ("", "-wal", "-shm"):
            path = f"{self.db_path}{suffix}"
            if os.path.exists(path):
                os.remove(path)

        conn = sqlite3.connect(self.db_path)
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
        conn.execute(
            """
            INSERT INTO messages (
                chat_id, message_id, user_id, author_name, timestamp, text, media_type,
                reply_to_id, fwd_from_id, context_group_id, raw_payload, payload_hash, schema_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (777, 1, 1, "Target User", 1700000000, "mine", None, None, None, None, "{}", "h1", 1),
        )
        conn.execute(
            """
            INSERT INTO message_target_links (chat_id, message_id, target_user_id)
            VALUES (?, ?, ?)
        """,
            (777, 1, 1),
        )
        conn.execute("PRAGMA user_version = 7")
        conn.commit()
        conn.close()

        self.storage = SQLiteStorage(self.db_path)

        with self.storage._read_connection() as conn:
            row = conn.execute(
                """
                SELECT chat_id, message_id, target_user_id, link_type, created_at
                FROM message_target_links
            """
            ).fetchone()
            backup_row = conn.execute(
                """
                SELECT chat_id, message_id, target_user_id
                FROM message_target_links_legacy_backup
            """
            ).fetchone()

        self.assertEqual(row["chat_id"], 777)
        self.assertEqual(row["message_id"], 1)
        self.assertEqual(row["target_user_id"], 1)
        self.assertEqual(row["link_type"], "legacy")
        self.assertGreater(row["created_at"], 0)
        self.assertEqual(backup_row["chat_id"], 777)
        self.assertEqual(backup_row["message_id"], 1)
        self.assertEqual(backup_row["target_user_id"], 1)

    async def test_target_link_migration_recovers_missing_chat_id_when_unambiguous(self):
        await self.storage.close()
        for suffix in ("", "-wal", "-shm"):
            path = f"{self.db_path}{suffix}"
            if os.path.exists(path):
                os.remove(path)

        conn = sqlite3.connect(self.db_path)
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
        conn.execute(
            """
            CREATE TABLE message_target_links (
                message_id INTEGER,
                target_user_id INTEGER,
                PRIMARY KEY (message_id, target_user_id)
            )
        """
        )
        conn.execute(
            """
            INSERT INTO messages (
                chat_id, message_id, user_id, author_name, timestamp, text, media_type,
                reply_to_id, fwd_from_id, context_group_id, raw_payload, payload_hash, schema_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (777, 5, 1, "Target User", 1700000000, "mine", None, None, None, None, "{}", "h5", 1),
        )
        conn.execute(
            """
            INSERT INTO message_target_links (message_id, target_user_id)
            VALUES (?, ?)
        """,
            (5, 1),
        )
        conn.execute("PRAGMA user_version = 7")
        conn.commit()
        conn.close()

        self.storage = SQLiteStorage(self.db_path)

        with self.storage._read_connection() as conn:
            row = conn.execute(
                """
                SELECT chat_id, message_id, target_user_id, link_type
                FROM message_target_links
            """
            ).fetchone()

        self.assertEqual(row["chat_id"], 777)
        self.assertEqual(row["message_id"], 5)
        self.assertEqual(row["target_user_id"], 1)
        self.assertEqual(row["link_type"], "legacy")

    async def test_target_link_migration_fails_when_chat_id_is_ambiguous(self):
        await self.storage.close()
        for suffix in ("", "-wal", "-shm"):
            path = f"{self.db_path}{suffix}"
            if os.path.exists(path):
                os.remove(path)

        conn = sqlite3.connect(self.db_path)
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
        conn.execute(
            """
            CREATE TABLE message_target_links (
                message_id INTEGER,
                target_user_id INTEGER,
                PRIMARY KEY (message_id, target_user_id)
            )
        """
        )
        for chat_id in (777, 888):
            conn.execute(
                """
                INSERT INTO messages (
                    chat_id, message_id, user_id, author_name, timestamp, text, media_type,
                    reply_to_id, fwd_from_id, context_group_id, raw_payload, payload_hash, schema_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (chat_id, 5, 1, "Target User", 1700000000, "mine", None, None, None, None, "{}", f"h5-{chat_id}", 1),
            )
        conn.execute(
            """
            INSERT INTO message_target_links (message_id, target_user_id)
            VALUES (?, ?)
        """,
            (5, 1),
        )
        conn.execute("PRAGMA user_version = 7")
        conn.commit()
        conn.close()

        with self.assertRaises(RuntimeError):
            self.storage = SQLiteStorage(self.db_path)

    async def test_delete_user_data_returns_typed_result(self):
        self.storage.register_target(1, "Target User", 777)
        msg = MessageData(
            message_id=1,
            chat_id=777,
            user_id=1,
            author_name="Target User",
            timestamp=datetime.now(),
            text="Delete me",
            media_type=None,
            reply_to_id=None,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={},
        )

        await self.storage.save_message(msg, target_id=1)
        result = self.storage.delete_user_data(1)

        self.assertIsInstance(result, DeleteUserDataResult)
        self.assertEqual(result.deleted_messages, 1)
        self.assertEqual(result.deleted_targets, 1)

    async def test_get_retry_tasks_returns_typed_records(self):
        self.storage.enqueue_retry_task("task1", 123, "export", "Timeout")
        with self.storage._write_transaction() as conn:
            conn.execute(
                "UPDATE retry_queue SET next_retry_timestamp = 0 WHERE task_id = ?",
                ("task1",),
            )

        tasks = self.storage.get_retry_tasks()

        self.assertEqual(len(tasks), 1)
        self.assertIsInstance(tasks[0], RetryTaskRecord)
        self.assertEqual(tasks[0].task_id, "task1")
        self.assertEqual(tasks[0].chat_id, 123)
        self.assertEqual(tasks[0].target_user_id, 123)
        self.assertEqual(tasks[0].status, "pending")

    async def test_retry_task_lifecycle_updates_status_and_attempts(self):
        self.storage.enqueue_retry_task(
            "task1",
            123,
            "sync_target",
            "Timeout",
            target_user_id=456,
            payload={"chat_id": 123, "user_id": 456},
            next_retry_timestamp=0,
        )

        due = self.storage.get_due_retry_tasks()
        self.assertEqual(len(due), 1)
        self.assertEqual(due[0].payload["user_id"], 456)

        next_status = self.storage.mark_retry_task_rescheduled(
            "task1", "Still failing", next_retry_timestamp=999
        )
        self.assertEqual(next_status, "retrying")

        listed = self.storage.list_retry_tasks()
        self.assertEqual(listed[0].retry_count, 1)
        self.assertEqual(listed[0].status, "retrying")
        self.assertEqual(listed[0].next_retry_timestamp, 999)

        self.storage.mark_retry_task_completed("task1")
        listed = self.storage.list_retry_tasks()
        self.assertEqual(listed[0].status, "completed")

        cleaned = self.storage.cleanup_retry_tasks()
        self.assertEqual(cleaned, 1)
        self.assertEqual(self.storage.list_retry_tasks(), [])

    async def test_retry_queue_migration_adds_lifecycle_columns(self):
        await self.storage.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            CREATE TABLE retry_queue (
                task_id TEXT PRIMARY KEY,
                chat_id INTEGER,
                task_type TEXT,
                retry_count INTEGER DEFAULT 0,
                last_error TEXT,
                next_retry_timestamp INTEGER
            )
        """
        )
        conn.execute(
            """
            INSERT INTO retry_queue (task_id, chat_id, task_type, retry_count, last_error, next_retry_timestamp)
            VALUES ('legacy-task', 123, 'export', 2, 'Timeout', 0)
        """
        )
        conn.execute("PRAGMA user_version = 4")
        conn.commit()
        conn.close()

        self.storage = SQLiteStorage(self.db_path)
        tasks = self.storage.list_retry_tasks()

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_id, "legacy-task")
        self.assertEqual(tasks[0].target_user_id, 123)
        self.assertEqual(tasks[0].status, "retrying")
        self.assertGreaterEqual(tasks[0].max_attempts, 5)

    async def asyncTearDown(self):
        await self.storage.close()
