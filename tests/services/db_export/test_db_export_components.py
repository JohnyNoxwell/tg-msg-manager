import os
import shutil
import tempfile
import unittest
from datetime import datetime
from unittest.mock import MagicMock

from tg_msg_manager.core.models.message import MessageData
from tg_msg_manager.services.db_export.plan_builder import DBExportPlanBuilder
from tg_msg_manager.services.db_export.skip_policy import DBExportSkipPolicy
from tg_msg_manager.services.db_export.source_loader import DBExportSourceLoader
from tg_msg_manager.services.db_export.state_manager import DBExportStateManager
from tg_msg_manager.services.db_export.summary import DBExportSource
from tg_msg_manager.services.db_export.service import DBExportService


class TestDBExportComponents(unittest.TestCase):
    def setUp(self):
        self.storage = MagicMock()
        self.tmpdir = tempfile.mkdtemp(prefix="tg_db_export_components_")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_source_loader_prefers_streaming_ai_json_source(self):
        self.storage.get_user_export_summary.return_value = {
            "message_count": 1,
            "first_message_id": 10,
            "last_message_id": 10,
            "first_timestamp": 1700000000,
            "last_timestamp": 1700000000,
            "target_author_name": "Stream User",
        }
        self.storage.iter_user_export_rows.return_value = iter(
            [
                {
                    "message_id": 10,
                    "chat_id": 20,
                    "user_id": 30,
                    "author_name": "Stream User",
                    "timestamp": 1700000000,
                    "text": "hello",
                    "media_type": None,
                    "reply_to_id": None,
                    "fwd_from_id": None,
                    "context_group_id": None,
                    "raw_payload": "{}",
                    "is_service": 0,
                }
            ]
        )

        source = DBExportSourceLoader(self.storage).load_full_source(
            user_id=30,
            as_json=True,
            json_profile="ai",
        )

        self.assertIsNotNone(source)
        self.assertEqual(source.source_count, 1)
        self.assertIsNotNone(source.export_row_iter_factory)
        self.assertIsNone(source.messages)

    def test_plan_builder_creates_deterministic_filename_and_fingerprint(self):
        self.storage.get_user.return_value = {
            "user_id": 30,
            "first_name": "Plan",
            "last_name": "User",
            "username": "planuser",
        }
        source = DBExportSource(
            export_summary=None,
            export_rows=None,
            export_row_iter_factory=None,
            messages=[
                MessageData(
                    message_id=1,
                    chat_id=2,
                    user_id=30,
                    author_name="Plan User",
                    timestamp=datetime.fromtimestamp(1700000000),
                    text="hello",
                    media_type=None,
                    reply_to_id=None,
                    fwd_from_id=None,
                    context_group_id=None,
                    raw_payload={},
                )
            ],
            source_count=1,
        )

        plan = DBExportPlanBuilder(self.storage).prepare_plan(
            user_id=30,
            output_dir=self.tmpdir,
            source=source,
            as_json=True,
            include_date=False,
            json_profile="ai",
        )

        self.assertTrue(plan.output_path.endswith("Plan_User_30.jsonl"))
        self.assertEqual(plan.fingerprint["message_count"], 1)
        self.assertEqual(plan.fingerprint["user_id"], 30)

    def test_skip_policy_returns_skip_when_db_state_matches_fingerprint(self):
        output_path = os.path.join(self.tmpdir, "Stable_User_3.jsonl")
        with open(output_path, "w", encoding="utf-8") as handle:
            handle.write("{}\n")
        self.storage.get_export_target.return_value = {
            "target_user_id": 3,
            "export_filename": os.path.basename(output_path),
            "export_dir": self.tmpdir,
            "export_part_count": 1,
            "artifact_message_count": 1,
            "artifact_first_message_id": 1,
            "artifact_last_message_id": 1,
            "artifact_first_timestamp": 1700000000,
            "artifact_last_timestamp": 1700000000,
            "artifact_as_json": True,
            "artifact_include_date": False,
            "artifact_json_profile": "ai",
        }
        fingerprint = {
            "message_count": 1,
            "first_message_id": 1,
            "last_message_id": 1,
            "first_timestamp": 1700000000,
            "last_timestamp": 1700000000,
            "as_json": True,
            "include_date": False,
            "json_profile": "ai",
        }

        decision = DBExportSkipPolicy(self.storage).find_skip_decision(
            output_dir=self.tmpdir,
            user_id=3,
            fingerprint=fingerprint,
        )

        self.assertTrue(decision.should_skip)
        self.assertEqual(decision.reason, "unchanged")
        self.assertEqual(decision.artifact.output_path, output_path)

    def test_state_manager_finish_run_closes_storage_run(self):
        manager = DBExportStateManager(self.storage)

        manager.finish_run(
            44,
            status="success",
            new_messages_count=7,
            last_new_message_ts=1700000000,
        )

        self.storage.finish_export_run.assert_called_once_with(
            44,
            status="success",
            new_messages_count=7,
            last_new_message_ts=1700000000,
            error=None,
        )

    def test_compatibility_import_reexports_service(self):
        self.assertEqual(DBExportService.__name__, "DBExportService")


if __name__ == "__main__":
    unittest.main()
