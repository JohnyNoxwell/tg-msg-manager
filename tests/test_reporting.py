import json
import os
import sys
import unittest
from datetime import datetime
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tg_msg_manager.core.models.message import MessageData
from tg_msg_manager.services.reporting import (
    ReportCollector,
    render_report_json,
    render_report_markdown,
)
from tg_msg_manager.infrastructure.storage.sqlite import SQLiteStorage


class TestReporting(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db_path = "test_reporting.db"
        self.exports_dir = Path("test_reporting_exports")
        self.exports_dir.mkdir(exist_ok=True)
        self.storage = SQLiteStorage(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        if os.path.exists(f"{self.db_path}-wal"):
            os.remove(f"{self.db_path}-wal")
        if os.path.exists(f"{self.db_path}-shm"):
            os.remove(f"{self.db_path}-shm")
        if self.exports_dir.exists():
            for path in self.exports_dir.iterdir():
                if path.is_file():
                    path.unlink()
            self.exports_dir.rmdir()

    async def test_report_collector_builds_deterministic_warnings_and_exports(self):
        self.storage.upsert_chat(500, "Audit Chat", "chat")
        self.storage.register_target(111, "Target One", 500)
        self.storage.register_target(222, "Target Two", 500)
        self.storage.register_target(333, "Target Three", 500)

        target_message = MessageData(
            message_id=1,
            chat_id=500,
            user_id=111,
            author_name="Target One",
            timestamp=datetime.now(),
            text="Own only",
            media_type=None,
            reply_to_id=999,
            fwd_from_id=None,
            context_group_id="cluster-1",
            raw_payload={},
        )
        await self.storage.save_message(target_message, target_id=111)
        second_target_message = MessageData(
            message_id=2,
            chat_id=500,
            user_id=222,
            author_name="Target Two",
            timestamp=datetime.now(),
            text="Needs export",
            media_type=None,
            reply_to_id=None,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={},
        )
        await self.storage.save_message(second_target_message, target_id=222)
        self.storage.enqueue_retry_task(
            "sync_target:500:111",
            500,
            "sync_target",
            "boom",
            target_user_id=111,
            payload={"chat_id": 500, "user_id": 111},
            next_retry_timestamp=0,
        )
        self.storage.mark_retry_task_failed("sync_target:500:111", "boom")

        with self.storage._write_transaction() as conn:
            conn.execute(
                "UPDATE sync_targets SET is_complete = 0, last_sync_at = 0 WHERE user_id = 111 AND chat_id = 500"
            )
            conn.execute(
                "UPDATE sync_targets SET is_complete = 0, last_sync_at = 0 WHERE user_id = 222 AND chat_id = 500"
            )
            conn.execute(
                "UPDATE sync_targets SET is_complete = 0, last_sync_at = 0 WHERE user_id = 333 AND chat_id = 500"
            )

        export_path = self.exports_dir / "Target_One_111.jsonl"
        export_path.write_text("{}\n", encoding="utf-8")

        collector = ReportCollector(
            storage=self.storage,
            exports_dir=self.exports_dir,
            now_ts=2_000_000_000,
        )
        report = collector.collect()

        self.assertEqual(report.database.targets_count, 3)
        self.assertEqual(report.retry.failed_tasks, 1)
        self.assertEqual(len(report.targets), 3)
        self.assertEqual(report.exports[0].artifact_count, 1)
        warning_codes = [warning.code for warning in report.warnings]
        self.assertIn("incomplete_target", warning_codes)
        self.assertIn("no_context_coverage", warning_codes)
        self.assertIn("no_target_messages", warning_codes)
        self.assertIn("retry_failed_tasks", warning_codes)
        self.assertIn("stale_sync", warning_codes)
        self.assertNotIn(
            "missing_export_state",
            [w.code for w in report.warnings if w.user_id == 111],
        )
        self.assertIn(
            "missing_export_state",
            [w.code for w in report.warnings if w.user_id == 222],
        )

    async def test_report_renderers_are_deterministic(self):
        collector = ReportCollector(
            storage=self.storage,
            exports_dir=self.exports_dir,
            now_ts=1_900_000_000,
        )
        report = collector.collect()

        markdown = render_report_markdown(report)
        payload = json.loads(render_report_json(report))

        self.assertIn("# Audit Report", markdown)
        self.assertEqual(payload["generated_at"], 1_900_000_000)
        self.assertIn("database", payload)
        self.assertIn("warnings", payload)

    async def asyncTearDown(self):
        await self.storage.close()
