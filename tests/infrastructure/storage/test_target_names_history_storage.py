import os
import tempfile
import unittest

from tg_msg_manager.infrastructure.storage.records import (
    TargetNameResolutionRecord,
    TargetNameSnapshotRecord,
    TargetNameTargetRecord,
)
from tg_msg_manager.infrastructure.storage.sqlite import SQLiteStorage


class TestTargetNamesHistoryStorage(unittest.TestCase):
    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(prefix="target-names-", suffix=".db")
        os.close(fd)
        self.storage = SQLiteStorage(self.db_path)

    def tearDown(self):
        self.storage._conn.close()
        for suffix in ("", "-wal", "-shm"):
            path = f"{self.db_path}{suffix}"
            if os.path.exists(path):
                os.remove(path)

    def test_resolves_numeric_user_and_reads_identity_snapshots(self):
        with self.storage._write_transaction() as conn:
            conn.execute(
                """
                INSERT INTO users (user_id, username, current_author_name)
                VALUES (?, ?, ?)
            """,
                (1001, "new_handle", "New Name"),
            )
            conn.execute(
                """
                INSERT INTO sync_targets (user_id, chat_id, author_name, added_at, last_sync_at)
                VALUES (?, ?, ?, ?, ?)
            """,
                (1001, 2001, "New Name", 1700000000, 1700000030),
            )
            conn.executemany(
                """
                INSERT INTO user_identity_history (
                    user_id, observed_at, author_name, username, chat_id, source_message_id
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                [
                    (1001, 1700000000, "Old Name", "old_handle", 2001, 1),
                    (1001, 1700000030, "New Name", "new_handle", 2001, 2),
                ],
            )

        resolution = self.storage.resolve_target_name_target("1001")
        snapshots = self.storage.get_target_name_snapshots(resolution.matches[0])

        self.assertIsInstance(resolution, TargetNameResolutionRecord)
        self.assertEqual(resolution.status, "found")
        self.assertEqual(resolution.matches[0].target_type, "user")
        self.assertEqual(resolution.matches[0].current_username, "new_handle")
        self.assertEqual(resolution.matches[0].current_display_name, "New Name")
        self.assertTrue(all(isinstance(item, TargetNameSnapshotRecord) for item in snapshots))
        self.assertEqual([item.display_name for item in snapshots], ["Old Name", "New Name"])

    def test_resolves_user_by_locally_stored_username_history(self):
        with self.storage._write_transaction() as conn:
            conn.execute("INSERT INTO users (user_id) VALUES (?)", (1002,))
            conn.execute(
                """
                INSERT INTO user_identity_history (user_id, observed_at, author_name, username)
                VALUES (?, ?, ?, ?)
            """,
                (1002, 1700000000, "History Name", "history_handle"),
            )

        resolution = self.storage.resolve_target_name_target("@History_Handle")

        self.assertEqual(resolution.status, "found")
        self.assertEqual(resolution.matches[0].target_id, 1002)
        self.assertEqual(resolution.matches[0].current_username, "history_handle")

    def test_reports_ambiguous_local_username(self):
        with self.storage._write_transaction() as conn:
            conn.executemany(
                "INSERT INTO users (user_id, username) VALUES (?, ?)",
                [(1003, "shared_handle"), (1004, "shared_handle")],
            )

        resolution = self.storage.resolve_target_name_target("shared_handle")

        self.assertEqual(resolution.status, "ambiguous")
        self.assertEqual([item.target_id for item in resolution.matches], [1003, 1004])

    def test_resolves_chat_current_title_without_title_history(self):
        self.storage.upsert_chat(-1002001, "Synthetic Channel", "channel")

        resolution = self.storage.resolve_target_name_target("-1002001")
        snapshots = self.storage.get_target_name_snapshots(resolution.matches[0])

        self.assertIsInstance(resolution.matches[0], TargetNameTargetRecord)
        self.assertEqual(resolution.status, "found")
        self.assertEqual(resolution.matches[0].target_type, "channel")
        self.assertEqual(resolution.matches[0].current_title, "Synthetic Channel")
        self.assertEqual(snapshots, [])

    def test_reports_unknown_target(self):
        resolution = self.storage.resolve_target_name_target("missing_handle")

        self.assertEqual(resolution.status, "not_found")
        self.assertEqual(resolution.matches, ())


if __name__ == "__main__":
    unittest.main()
