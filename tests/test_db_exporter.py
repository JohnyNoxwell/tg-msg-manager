import sys
import os
import json
import asyncio
import unittest
import tempfile
import shutil
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tg_msg_manager.core.models.message import MessageData
from tg_msg_manager.core.telemetry import telemetry
from tg_msg_manager.services.db_exporter import DBExportService


class TestDBExporter(unittest.TestCase):
    def setUp(self):
        self.storage = MagicMock()
        self._export_targets = {}

        def get_export_target(user_id):
            return self._export_targets.get(user_id)

        def upsert_export_target(**kwargs):
            target_user_id = int(kwargs["target_user_id"])
            current = dict(self._export_targets.get(target_user_id) or {})
            current["target_user_id"] = target_user_id
            for key, value in kwargs.items():
                if key == "target_user_id":
                    continue
                if value is not None or key not in current:
                    current[key] = value
            self._export_targets[target_user_id] = current

        self.storage.get_export_target.side_effect = get_export_target
        self.storage.upsert_export_target.side_effect = upsert_export_target
        self.storage.get_user_export_summary.return_value = None
        self.storage.get_user_export_summary_since.return_value = None
        self.storage.get_user_export_rows.return_value = None
        self.storage.get_user_export_rows_since.return_value = None
        self.storage.iter_user_export_rows.return_value = iter(())
        self.storage.iter_user_export_rows_since.return_value = iter(())
        self.storage.start_export_run.return_value = 44
        self.service = DBExportService(self.storage)
        self.tmpdir = tempfile.mkdtemp(prefix="tg_db_export_test_")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_ai_json_profile_is_default_and_keeps_graph_fields(self):
        msg = MessageData(
            message_id=101,
            chat_id=202,
            user_id=303,
            author_name="Graph User",
            timestamp=datetime.fromtimestamp(1700000000),
            text="hello",
            media_type=None,
            reply_to_id=None,
            fwd_from_id=None,
            context_group_id="cluster-1",
            raw_payload={
                "reply_to": {
                    "reply_to_msg_id": 77,
                    "reply_to_top_id": 55,
                    "forum_topic": True,
                },
                "edit_date": "2025-01-01T12:00:00+00:00",
                "reactions": {
                    "results": [
                        {
                            "reaction": {"_": "ReactionEmoji", "emoticon": "👍"},
                            "count": 3,
                        }
                    ]
                },
            },
        )

        payload = json.loads(self.service.format_message(msg, as_json=True))

        self.assertNotIn("raw_payload", payload)
        self.assertEqual(payload["reply_to_id"], 77)
        self.assertEqual(payload["reply_to_top_id"], 55)
        self.assertTrue(payload["forum_topic"])
        self.assertEqual(payload["context_group_id"], "cluster-1")
        self.assertEqual(payload["reactions"], [{"emoji": "👍", "count": 3}])
        self.assertEqual(payload["edit_date"], "2025-01-01T12:00:00+00:00")
        rendered = self.service.format_message(msg, as_json=True)
        self.assertTrue(rendered.startswith('{"edit_date":"2025-01-01T12:00:00+00:00"'))

    def test_full_json_profile_keeps_raw_payload(self):
        msg = MessageData(
            message_id=1,
            chat_id=2,
            user_id=3,
            author_name="Full User",
            timestamp=datetime.fromtimestamp(1700000000),
            text="full",
            media_type=None,
            reply_to_id=9,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={"reply_to": {"reply_to_msg_id": 9}},
        )

        payload = json.loads(
            self.service.format_message(msg, as_json=True, json_profile="full")
        )

        self.assertIn("raw_payload", payload)
        self.assertEqual(payload["reply_to_id"], 9)

    def test_resolve_export_author_name_prefers_message_author_when_user_card_is_empty(
        self,
    ):
        self.storage.get_user.return_value = {
            "user_id": 2142333070,
            "first_name": "",
            "last_name": "",
            "username": "",
        }
        msg = MessageData(
            message_id=1,
            chat_id=2,
            user_id=2142333070,
            author_name="Никто",
            timestamp=datetime.fromtimestamp(1700000000),
            text="hello",
            media_type=None,
            reply_to_id=None,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={},
        )

        name = self.service._resolve_export_author_name(2142333070, [msg])

        self.assertEqual(name, "Никто")

    def test_write_batch_size_prefers_larger_batches_for_ai_json(self):
        self.assertEqual(
            self.service._write_batch_size(as_json=False, json_profile="ai"), 100
        )
        self.assertEqual(
            self.service._write_batch_size(as_json=True, json_profile="full"), 500
        )
        self.assertEqual(
            self.service._write_batch_size(as_json=True, json_profile="ai"), 1000
        )

    def test_export_user_messages_skips_full_rewrite_when_fingerprint_is_unchanged(
        self,
    ):
        telemetry.reset()
        message = MessageData(
            message_id=1,
            chat_id=2,
            user_id=3,
            author_name="Stable User",
            timestamp=datetime.fromtimestamp(1700000000),
            text="hello",
            media_type=None,
            reply_to_id=None,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={},
        )
        self.storage.get_user_messages.return_value = [message]
        self.storage.get_user.return_value = {
            "user_id": 3,
            "first_name": "Stable",
            "last_name": "User",
            "username": "stable",
        }

        first_path = asyncio.run(
            self.service.export_user_messages(3, output_dir=self.tmpdir, as_json=True)
        )
        with open(first_path, "r", encoding="utf-8") as f:
            first_content = f.read()

        second_path = asyncio.run(
            self.service.export_user_messages(3, output_dir=self.tmpdir, as_json=True)
        )
        with open(second_path, "r", encoding="utf-8") as f:
            second_content = f.read()

        self.assertEqual(first_path, second_path)
        self.assertEqual(first_content, second_content)
        summary = telemetry.get_summary()
        self.assertEqual(summary["counters"]["db_export.skipped_unchanged"], 1)

    def test_export_user_messages_skips_multipart_rewrite_when_parts_are_unchanged(
        self,
    ):
        telemetry.reset()
        messages = []
        base_ts = 1700000000
        for idx in range(5001):
            messages.append(
                MessageData(
                    message_id=idx + 1,
                    chat_id=2,
                    user_id=3,
                    author_name="Stable User",
                    timestamp=datetime.fromtimestamp(base_ts + idx),
                    text=f"hello {idx}",
                    media_type=None,
                    reply_to_id=None,
                    fwd_from_id=None,
                    context_group_id=None,
                    raw_payload={},
                )
            )
        self.storage.get_user_messages.return_value = messages
        self.storage.get_user.return_value = {
            "user_id": 3,
            "first_name": "Stable",
            "last_name": "User",
            "username": "stable",
        }

        first_path = asyncio.run(
            self.service.export_user_messages(3, output_dir=self.tmpdir, as_json=True)
        )
        second_path = asyncio.run(
            self.service.export_user_messages(3, output_dir=self.tmpdir, as_json=True)
        )

        self.assertEqual(first_path, second_path)
        self.assertTrue(os.path.exists(first_path))
        self.assertTrue(os.path.exists(first_path.replace(".jsonl", "_part2.jsonl")))
        summary = telemetry.get_summary()
        self.assertEqual(summary["counters"]["db_export.skipped_unchanged"], 1)

    def test_export_user_messages_uses_streaming_row_fast_path_for_ai_json(self):
        row = {
            "message_id": 1,
            "chat_id": 2,
            "user_id": 3,
            "author_name": "Fast User",
            "timestamp": 1700000000,
            "text": "hello",
            "media_type": None,
            "reply_to_id": None,
            "fwd_from_id": None,
            "context_group_id": None,
            "raw_payload": "{}",
            "is_service": 0,
        }
        self.storage.get_user_export_summary.return_value = {
            "message_count": 1,
            "first_message_id": 1,
            "last_message_id": 1,
            "first_timestamp": 1700000000,
            "last_timestamp": 1700000000,
            "target_author_name": "Fast User",
        }
        self.storage.iter_user_export_rows.side_effect = lambda user_id: iter([row])
        self.storage.get_user.return_value = {
            "user_id": 3,
            "first_name": "Fast",
            "last_name": "User",
            "username": "fast",
        }

        output_path = asyncio.run(
            self.service.export_user_messages(3, output_dir=self.tmpdir, as_json=True)
        )

        self.storage.get_user_messages.assert_not_called()
        self.storage.get_user_export_rows.assert_not_called()
        self.assertTrue(os.path.exists(output_path))

    def test_export_user_messages_updates_db_backed_export_target_state(self):
        message = MessageData(
            message_id=7,
            chat_id=2,
            user_id=3,
            author_name="Stable User",
            timestamp=datetime.fromtimestamp(1700001234),
            text="hello",
            media_type=None,
            reply_to_id=None,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={},
        )
        self.storage.get_user_messages.return_value = [message]
        self.storage.get_user.return_value = {
            "user_id": 3,
            "first_name": "Stable",
            "last_name": "User",
            "username": "stable",
        }

        output_path = asyncio.run(
            self.service.export_user_messages(3, output_dir=self.tmpdir, as_json=True)
        )

        self.storage.upsert_export_target.assert_called_once()
        kwargs = self.storage.upsert_export_target.call_args.kwargs
        self.assertEqual(kwargs["target_user_id"], 3)
        self.assertEqual(kwargs["export_filename"], os.path.basename(output_path))
        self.assertEqual(kwargs["export_dir"], os.path.dirname(output_path))
        self.assertEqual(kwargs["last_exported_message_ts"], 1700001234)
        self.assertEqual(kwargs["last_exported_message_id"], 7)
        self.assertEqual(kwargs["export_part_count"], 1)
        self.assertEqual(kwargs["artifact_message_count"], 1)
        self.assertEqual(kwargs["artifact_first_message_id"], 7)
        self.assertEqual(kwargs["artifact_last_message_id"], 7)
        self.assertEqual(kwargs["artifact_first_timestamp"], 1700001234)
        self.assertEqual(kwargs["artifact_last_timestamp"], 1700001234)
        self.assertTrue(kwargs["artifact_as_json"])
        self.assertFalse(kwargs["artifact_include_date"])
        self.assertEqual(kwargs["artifact_json_profile"], "ai")
        self.assertEqual(kwargs["last_known_author_name"], "Stable User")
        self.assertEqual(kwargs["last_known_username"], "stable")
        self.storage.start_export_run.assert_called_once_with(target_user_id=3)
        self.storage.finish_export_run.assert_called_once_with(
            44,
            status="success",
            new_messages_count=1,
            last_new_message_ts=1700001234,
            error=None,
        )

    def test_export_user_messages_skip_path_still_updates_export_target_state(self):
        telemetry.reset()
        message = MessageData(
            message_id=9,
            chat_id=2,
            user_id=3,
            author_name="Stable User",
            timestamp=datetime.fromtimestamp(1700002222),
            text="hello",
            media_type=None,
            reply_to_id=None,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={},
        )
        self.storage.get_user_messages.return_value = [message]
        self.storage.get_user.return_value = {
            "user_id": 3,
            "first_name": "Stable",
            "last_name": "User",
            "username": "stable",
        }

        first_path = asyncio.run(
            self.service.export_user_messages(3, output_dir=self.tmpdir, as_json=True)
        )
        self.storage.upsert_export_target.reset_mock()

        second_path = asyncio.run(
            self.service.export_user_messages(3, output_dir=self.tmpdir, as_json=True)
        )

        self.assertEqual(first_path, second_path)
        self.storage.upsert_export_target.assert_called_once()
        kwargs = self.storage.upsert_export_target.call_args.kwargs
        self.assertEqual(kwargs["target_user_id"], 3)
        self.assertEqual(kwargs["export_filename"], os.path.basename(second_path))
        self.assertEqual(kwargs["export_dir"], os.path.dirname(second_path))
        self.assertEqual(kwargs["last_exported_message_ts"], 1700002222)
        self.assertEqual(kwargs["last_exported_message_id"], 9)
        self.assertEqual(kwargs["export_part_count"], 1)
        self.assertEqual(kwargs["artifact_message_count"], 1)
        self.assertEqual(kwargs["last_known_author_name"], "Stable User")
        self.assertEqual(kwargs["last_known_username"], "stable")
        self.storage.finish_export_run.assert_called_with(
            44,
            status="success",
            new_messages_count=0,
            last_new_message_ts=None,
            error=None,
        )

    def test_export_user_messages_does_not_write_legacy_manifest_sidecar(self):
        message = MessageData(
            message_id=10,
            chat_id=2,
            user_id=3,
            author_name="Stable User",
            timestamp=datetime.fromtimestamp(1700003333),
            text="hello",
            media_type=None,
            reply_to_id=None,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={},
        )
        self.storage.get_user_messages.return_value = [message]
        self.storage.get_user.return_value = {
            "user_id": 3,
            "first_name": "Stable",
            "last_name": "User",
            "username": "stable",
        }

        output_path = asyncio.run(
            self.service.export_user_messages(3, output_dir=self.tmpdir, as_json=True)
        )

        self.assertTrue(os.path.exists(output_path))
        self.assertFalse(
            os.path.exists(os.path.join(self.tmpdir, ".export_state", "3.json"))
        )

    def test_export_user_messages_legacy_manifest_fallback_backfills_db_state(self):
        telemetry.reset()
        message = MessageData(
            message_id=11,
            chat_id=2,
            user_id=3,
            author_name="Stable User",
            timestamp=datetime.fromtimestamp(1700004444),
            text="hello",
            media_type=None,
            reply_to_id=None,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={},
        )
        self.storage.get_user_messages.return_value = [message]
        self.storage.get_user.return_value = {
            "user_id": 3,
            "first_name": "Stable",
            "last_name": "User",
            "username": "stable",
        }

        output_path = os.path.join(self.tmpdir, "Stable_User_3.jsonl")
        with open(output_path, "w", encoding="utf-8") as handle:
            handle.write('{"message_id":11,"text":"hello"}\n')

        os.makedirs(os.path.join(self.tmpdir, ".export_state"), exist_ok=True)
        with open(
            os.path.join(self.tmpdir, ".export_state", "3.json"),
            "w",
            encoding="utf-8",
        ) as handle:
            json.dump(
                {
                    "output_path": output_path,
                    "part_count": 1,
                    "fingerprint": {
                        "user_id": 3,
                        "message_count": 1,
                        "first_message_id": 11,
                        "last_message_id": 11,
                        "first_timestamp": 1700004444,
                        "last_timestamp": 1700004444,
                        "as_json": True,
                        "include_date": False,
                        "json_profile": "ai",
                    },
                },
                handle,
            )

        unchanged_path = asyncio.run(
            self.service.export_user_messages(3, output_dir=self.tmpdir, as_json=True)
        )

        self.assertEqual(unchanged_path, output_path)
        self.storage.upsert_export_target.assert_called_once()
        kwargs = self.storage.upsert_export_target.call_args.kwargs
        self.assertEqual(kwargs["target_user_id"], 3)
        self.assertEqual(kwargs["export_part_count"], 1)
        self.assertEqual(kwargs["artifact_message_count"], 1)
        self.assertEqual(self._export_targets[3]["artifact_last_message_id"], 11)
        summary = telemetry.get_summary()
        self.assertEqual(summary["counters"]["db_export.skipped_unchanged"], 1)

    def test_export_user_messages_records_failed_export_run_without_cursor_update(self):
        message = MessageData(
            message_id=9,
            chat_id=2,
            user_id=3,
            author_name="Stable User",
            timestamp=datetime.fromtimestamp(1700002222),
            text="hello",
            media_type=None,
            reply_to_id=None,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={},
        )
        self.storage.get_user_messages.return_value = [message]
        self.storage.get_user.return_value = {
            "user_id": 3,
            "first_name": "Stable",
            "last_name": "User",
            "username": "stable",
        }
        self.service._write_export_payloads = AsyncMock(side_effect=RuntimeError("disk full"))

        with self.assertRaisesRegex(RuntimeError, "disk full"):
            asyncio.run(
                self.service.export_user_messages(
                    3, output_dir=self.tmpdir, as_json=True
                )
            )

        self.storage.upsert_export_target.assert_not_called()
        self.storage.finish_export_run.assert_called_once_with(
            44,
            status="failed",
            new_messages_count=0,
            last_new_message_ts=None,
            error="disk full",
        )

    def test_update_user_messages_appends_only_new_rows_from_db_cursor(self):
        initial_path = os.path.join(self.tmpdir, "Stable_User_3.jsonl")
        with open(initial_path, "w", encoding="utf-8") as handle:
            handle.write('{"message_id":7,"text":"old"}\n')

        self._export_targets[3] = {
            "target_user_id": 3,
            "export_filename": "Stable_User_3.jsonl",
            "export_dir": self.tmpdir,
            "last_exported_message_ts": 1700001234,
            "last_exported_message_id": 7,
            "last_known_author_name": "Stable User",
            "last_known_username": "stable",
        }
        self.storage.get_user_export_summary_since.return_value = {
            "message_count": 1,
            "first_message_id": 8,
            "last_message_id": 8,
            "first_timestamp": 1700002234,
            "last_timestamp": 1700002234,
            "target_author_name": "Stable User",
        }
        row = {
            "message_id": 8,
            "chat_id": 2,
            "user_id": 3,
            "author_name": "Stable User",
            "timestamp": 1700002234,
            "text": "new",
            "media_type": None,
            "reply_to_id": None,
            "fwd_from_id": None,
            "context_group_id": None,
            "raw_payload": "{}",
            "is_service": 0,
        }
        self.storage.iter_user_export_rows_since.side_effect = (
            lambda user_id, last_ts, last_message_id: iter([row])
        )
        self.storage.get_user_export_summary.return_value = {
            "message_count": 2,
            "first_message_id": 7,
            "last_message_id": 8,
            "first_timestamp": 1700001234,
            "last_timestamp": 1700002234,
            "target_author_name": "Stable User",
        }
        self.storage.get_user.return_value = {
            "user_id": 3,
            "first_name": "Stable",
            "last_name": "User",
            "username": "stable",
        }

        output_path = asyncio.run(
            self.service.update_user_messages(3, output_dir=self.tmpdir, as_json=True)
        )

        self.assertEqual(output_path, initial_path)
        with open(initial_path, "r", encoding="utf-8") as handle:
            lines = handle.readlines()
        self.assertEqual(len(lines), 2)
        self.assertIn('"message_id":7', lines[0])
        self.assertIn('"message_id":8', lines[1])
        self.storage.upsert_export_target.assert_called_once()
        kwargs = self.storage.upsert_export_target.call_args.kwargs
        self.assertEqual(kwargs["target_user_id"], 3)
        self.assertEqual(kwargs["export_filename"], "Stable_User_3.jsonl")
        self.assertEqual(kwargs["export_dir"], self.tmpdir)
        self.assertEqual(kwargs["last_exported_message_ts"], 1700002234)
        self.assertEqual(kwargs["last_exported_message_id"], 8)
        self.assertEqual(kwargs["export_part_count"], 1)
        self.assertEqual(kwargs["artifact_message_count"], 2)
        self.assertEqual(kwargs["artifact_first_message_id"], 7)
        self.assertEqual(kwargs["artifact_last_message_id"], 8)
        self.assertEqual(kwargs["last_known_author_name"], "Stable User")
        self.assertEqual(kwargs["last_known_username"], "stable")
        self.storage.finish_export_run.assert_called_once_with(
            44,
            status="success",
            new_messages_count=1,
            last_new_message_ts=1700002234,
            error=None,
        )

    def test_update_user_messages_returns_existing_path_when_no_new_rows(self):
        initial_path = os.path.join(self.tmpdir, "Stable_User_3.jsonl")
        with open(initial_path, "w", encoding="utf-8") as handle:
            handle.write('{"message_id":7,"text":"old"}\n')

        self._export_targets[3] = {
            "target_user_id": 3,
            "export_filename": "Stable_User_3.jsonl",
            "export_dir": self.tmpdir,
            "last_exported_message_ts": 1700001234,
            "last_exported_message_id": 7,
            "last_known_author_name": "Stable User",
            "last_known_username": "stable",
        }
        self.storage.get_user_export_summary_since.return_value = None

        output_path = asyncio.run(
            self.service.update_user_messages(3, output_dir=self.tmpdir, as_json=True)
        )

        self.assertEqual(output_path, initial_path)
        self.storage.upsert_export_target.assert_not_called()
        self.storage.finish_export_run.assert_called_once_with(
            44,
            status="success",
            new_messages_count=0,
            last_new_message_ts=None,
            error=None,
        )

    def test_export_user_messages_txt_marks_missing_reply_reference(self):
        message = MessageData(
            message_id=7,
            chat_id=2,
            user_id=3,
            author_name="Stable User",
            timestamp=datetime.fromtimestamp(1700001234),
            text="hello",
            media_type=None,
            reply_to_id=99,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={},
        )
        self.storage.get_user_messages.return_value = [message]
        self.storage.get_user.return_value = {
            "user_id": 3,
            "first_name": "Stable",
            "last_name": "User",
            "username": "stable",
        }

        output_path = asyncio.run(
            self.service.export_user_messages(3, output_dir=self.tmpdir, as_json=False)
        )

        with open(output_path, "r", encoding="utf-8") as handle:
            content = handle.read()
        self.assertIn(
            "[reply_to: 99 - original message not found in local DB]",
            content,
        )

    def test_export_user_messages_streaming_row_fast_path_skips_unchanged_without_len_none_crash(
        self,
    ):
        telemetry.reset()
        row = {
            "message_id": 1,
            "chat_id": 2,
            "user_id": 3,
            "author_name": "Fast User",
            "timestamp": 1700000000,
            "text": "hello",
            "media_type": None,
            "reply_to_id": None,
            "fwd_from_id": None,
            "context_group_id": None,
            "raw_payload": "{}",
            "is_service": 0,
        }
        self.storage.get_user_export_summary.return_value = {
            "message_count": 1,
            "first_message_id": 1,
            "last_message_id": 1,
            "first_timestamp": 1700000000,
            "last_timestamp": 1700000000,
            "target_author_name": "Fast User",
        }
        self.storage.iter_user_export_rows.side_effect = lambda user_id: iter([row])
        self.storage.get_user.return_value = {
            "user_id": 3,
            "first_name": "Fast",
            "last_name": "User",
            "username": "fast",
        }

        first_path = asyncio.run(
            self.service.export_user_messages(3, output_dir=self.tmpdir, as_json=True)
        )
        second_path = asyncio.run(
            self.service.export_user_messages(3, output_dir=self.tmpdir, as_json=True)
        )

        self.assertEqual(first_path, second_path)
        self.storage.get_user_messages.assert_not_called()
        summary = telemetry.get_summary()
        self.assertEqual(summary["counters"]["db_export.skipped_unchanged"], 1)

    def test_export_user_messages_falls_back_to_materialized_rows_when_streaming_helpers_are_unavailable(
        self,
    ):
        row = {
            "message_id": 1,
            "chat_id": 2,
            "user_id": 3,
            "author_name": "Legacy Fast User",
            "timestamp": 1700000000,
            "text": "hello",
            "media_type": None,
            "reply_to_id": None,
            "fwd_from_id": None,
            "context_group_id": None,
            "raw_payload": "{}",
            "is_service": 0,
        }
        self.storage.get_user_export_rows.return_value = [row]
        self.storage.get_user.return_value = {
            "user_id": 3,
            "first_name": "Legacy",
            "last_name": "User",
            "username": "legacy",
        }

        output_path = asyncio.run(
            self.service.export_user_messages(3, output_dir=self.tmpdir, as_json=True)
        )

        self.storage.get_user_messages.assert_not_called()
        self.assertTrue(os.path.exists(output_path))
        with open(output_path, "r", encoding="utf-8") as f:
            payload = json.loads(f.readline())
        self.assertEqual(payload["author_name"], "Legacy Fast User")


if __name__ == "__main__":
    unittest.main()
