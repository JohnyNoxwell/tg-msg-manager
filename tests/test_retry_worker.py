import sys
import os
import unittest
from unittest.mock import AsyncMock, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tg_msg_manager.infrastructure.storage.sqlite import SQLiteStorage
from tg_msg_manager.services.retry_worker import RetryBackoffPolicy, RetryWorker


class TestRetryWorker(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db_path = "test_retry_worker.db"
        self.storage = SQLiteStorage(self.db_path)
        self.client = AsyncMock()
        self.exporter = MagicMock()
        self.exporter.sync_chat = AsyncMock(return_value=0)
        self.private_archive = MagicMock()
        self.private_archive.archive_pm = AsyncMock(return_value="/tmp/pm")

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    async def test_retry_worker_completes_due_sync_target_task(self):
        self.storage.enqueue_retry_task(
            "sync_target:200:999",
            200,
            "sync_target",
            "fail",
            target_user_id=999,
            payload={"chat_id": 200, "user_id": 999},
            next_retry_timestamp=0,
        )
        self.client.get_entity = AsyncMock(return_value=MagicMock(id=200))
        self.storage.get_sync_status = MagicMock(return_value={"is_complete": 0})
        worker = RetryWorker(
            storage=self.storage,
            client=self.client,
            exporter=self.exporter,
            private_archive=self.private_archive,
        )

        stats = await worker.run_due_tasks()

        self.assertEqual(stats.succeeded, 1)
        self.exporter.sync_chat.assert_awaited_once()
        task = self.storage.list_retry_tasks()[0]
        self.assertEqual(task.status, "completed")

    async def test_retry_worker_reschedules_failed_task_with_deterministic_backoff(
        self,
    ):
        self.storage.enqueue_retry_task(
            "archive_pm:555",
            555,
            "archive_pm",
            "fail",
            target_user_id=555,
            payload={"user_id": 555},
            next_retry_timestamp=0,
        )
        self.client.get_entity = AsyncMock(return_value=MagicMock(id=555))
        self.private_archive.archive_pm = AsyncMock(side_effect=RuntimeError("boom"))
        worker = RetryWorker(
            storage=self.storage,
            client=self.client,
            exporter=self.exporter,
            private_archive=self.private_archive,
            backoff_policy=RetryBackoffPolicy(
                base_delay_seconds=11, max_delay_seconds=99
            ),
        )

        stats = await worker.run_due_tasks()

        self.assertEqual(stats.rescheduled, 1)
        task = self.storage.list_retry_tasks()[0]
        self.assertEqual(task.status, "retrying")
        self.assertEqual(task.retry_count, 1)
        self.assertGreater(task.next_retry_timestamp, 0)

    async def asyncTearDown(self):
        await self.storage.close()
