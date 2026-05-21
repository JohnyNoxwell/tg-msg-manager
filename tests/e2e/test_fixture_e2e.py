import os
import sys
import unittest
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tg_msg_manager.core.models.retry import RetryTaskStatus
from tg_msg_manager.infrastructure.storage.records import SyncStatus
from tg_msg_manager.testing import (
    FixtureRuntime,
    load_export_jsonl,
    load_telegram_fixture,
    normalize_export_rows,
)


FIXTURE_DIR = Path(__file__).parents[1] / "fixtures" / "stage5"


class TestFixtureBackedE2E(unittest.IsolatedAsyncioTestCase):
    async def test_sync_context_export_pipeline_is_fixture_backed(self):
        runtime = await FixtureRuntime.create(
            load_telegram_fixture(FIXTURE_DIR / "group_sync_context.jsonl")
        )
        try:
            chat_entity = await runtime.client.get_entity(1001)

            processed = await runtime.exporter.sync_chat(
                chat_entity,
                from_user_id=5001,
                deep_mode=True,
                recursive_depth=2,
                force_resync=True,
                context_window=2,
                max_cluster=6,
            )

            await runtime.storage.flush()
            self.assertGreater(processed, 0)

            breakdown = runtime.storage.get_target_message_breakdown(1001, 5001)
            self.assertGreaterEqual(breakdown["own_messages"], 2)
            self.assertGreaterEqual(breakdown["with_context"], 1)

            stored_target = runtime.storage.get_message(1001, 13)
            stored_parent = runtime.storage.get_message(1001, 14)
            self.assertIsNotNone(stored_target)
            self.assertIsNotNone(stored_parent)
            self.assertEqual(stored_parent.text, "Parent context reply")

            get_message_calls = [
                call
                for call in runtime.client.call_history
                if call["method"] == "get_messages"
            ]
            self.assertTrue(
                any(call.get("message_ids") == [14] for call in get_message_calls)
            )

            export_path = await runtime.db_exporter.export_user_messages(
                5001,
                as_json=True,
                include_date=False,
            )
            normalized_rows = normalize_export_rows(
                load_export_jsonl(export_path),
                drop_fields=("timestamp", "edit_date"),
            )
            exported_ids = [row["message_id"] for row in normalized_rows]
            self.assertEqual(exported_ids.count(13), 1)
            self.assertIn(14, exported_ids)
            self.assertEqual(
                [row["text"] for row in normalized_rows if row["message_id"] == 13],
                ["Target alpha baseline"],
            )

            report = runtime.build_report(now_ts=2_000_000_000)
            export_state = next(item for item in report.exports if item.user_id == 5001)
            self.assertEqual(export_state.artifact_count, 1)
            self.assertNotIn(
                "missing_export_state",
                [
                    warning.code
                    for warning in report.warnings
                    if warning.user_id == 5001
                ],
            )
        finally:
            await runtime.close()

    async def test_fixture_revision_updates_edited_payload_without_duplication(self):
        runtime = await FixtureRuntime.create(
            load_telegram_fixture(FIXTURE_DIR / "group_sync_context.jsonl")
        )
        try:
            chat_entity = await runtime.client.get_entity(1001)
            await runtime.exporter.sync_chat(
                chat_entity,
                from_user_id=5001,
                deep_mode=True,
                recursive_depth=2,
                force_resync=True,
                context_window=2,
                max_cluster=6,
            )
            await runtime.storage.flush()
            initial_count = runtime.storage.get_message_count(1001, target_id=5001)

            runtime.replace_dataset(
                load_telegram_fixture(FIXTURE_DIR / "group_sync_context_edited.jsonl")
            )
            updated_count = await runtime.exporter.sync_chat(
                chat_entity,
                from_user_id=5001,
                deep_mode=True,
                recursive_depth=2,
                force_resync=True,
                context_window=2,
                max_cluster=6,
            )
            await runtime.storage.flush()

            stored_target = runtime.storage.get_message(1001, 13)
            final_count = runtime.storage.get_message_count(1001, target_id=5001)
            self.assertGreaterEqual(updated_count, 0)
            self.assertEqual(final_count, initial_count)
            self.assertEqual(stored_target.text, "Target alpha edited")
            self.assertEqual(
                stored_target.raw_payload.get("edit_date"),
                1704067440,
            )
        finally:
            await runtime.close()

    async def test_interrupted_sync_leaves_resumeable_state_without_network(self):
        runtime = await FixtureRuntime.create(
            load_telegram_fixture(FIXTURE_DIR / "group_sync_context.jsonl")
        )
        try:
            chat_entity = await runtime.client.get_entity(1001)
            original_save_messages = runtime.storage.save_messages
            stop_once = {"armed": True}

            async def stop_after_first_save(*args, **kwargs):
                result = await original_save_messages(*args, **kwargs)
                if stop_once["armed"]:
                    stop_once["armed"] = False
                    runtime.storage.request_stop()
                return result

            runtime.storage.save_messages = stop_after_first_save
            await runtime.exporter.sync_chat(
                chat_entity,
                from_user_id=5001,
                deep_mode=False,
                force_resync=True,
            )
            await runtime.storage.flush()

            status = SyncStatus.coerce(runtime.storage.get_sync_status(1001, 5001))
            report = runtime.build_report(now_ts=2_000_000_000)
            self.assertFalse(status.is_complete)
            self.assertGreaterEqual(status.last_msg_id, 15)
            self.assertIn(
                "incomplete_target",
                [
                    warning.code
                    for warning in report.warnings
                    if warning.user_id == 5001
                ],
            )
        finally:
            await runtime.close()

    async def test_retry_and_report_pipeline_recovers_from_fixture_failure(self):
        runtime = await FixtureRuntime.create(
            load_telegram_fixture(FIXTURE_DIR / "tracked_retry.jsonl")
        )
        try:
            runtime.storage.upsert_chat(2001, "Retry Fixture Group", "Chat")
            runtime.storage.register_target(6001, "Retry Target", 2001)

            stats = await runtime.exporter.sync_all_tracked()
            self.assertFalse(stats[6001]["dirty"])

            pending_tasks = runtime.storage.list_retry_tasks()
            self.assertEqual(len(pending_tasks), 1)
            self.assertEqual(pending_tasks[0].status, RetryTaskStatus.PENDING.value)
            with runtime.storage._write_transaction() as conn:
                conn.execute("UPDATE retry_queue SET next_retry_timestamp = 0")

            report_before_retry = runtime.build_report(now_ts=2_000_000_000)
            self.assertIn(
                "retry_queue_not_empty",
                [warning.code for warning in report_before_retry.warnings],
            )

            retry_stats = await runtime.retry_worker.run_due_tasks(limit=5)
            await runtime.storage.flush()
            self.assertEqual(retry_stats.succeeded, 1)

            report_without_export = runtime.build_report(now_ts=2_000_000_000)
            self.assertIn(
                "missing_export_state",
                [warning.code for warning in report_without_export.warnings],
            )

            await runtime.db_exporter.export_user_messages(
                6001,
                as_json=True,
                include_date=False,
            )
            with runtime.storage._write_transaction() as conn:
                conn.execute(
                    "UPDATE sync_targets SET last_sync_at = 0 WHERE chat_id = 2001 AND user_id = 6001"
                )

            report_after_export = runtime.build_report(now_ts=2_000_000_000)
            warning_codes = [warning.code for warning in report_after_export.warnings]
            self.assertNotIn("retry_queue_not_empty", warning_codes)
            self.assertNotIn("missing_export_state", warning_codes)
            self.assertIn("stale_sync", warning_codes)
        finally:
            await runtime.close()
