import json
import unittest
from pathlib import Path

from tg_msg_manager.core.models.message import MessageData
from tg_msg_manager.services.db_export.jsonl_writer import serialize_json_message


FIXTURE_ROOT = Path(__file__).resolve().parents[2] / "fixtures"
NON_CHANNEL_FIXTURES = FIXTURE_ROOT / "non_channel_export"
DB_EXPORT_FIXTURES = FIXTURE_ROOT / "db_export"

ALLOWED_AI_KEYS = {
    "edit_date",
    "message_id",
    "chat_id",
    "user_id",
    "author_name",
    "timestamp",
    "text",
    "reply_to_id",
    "reply_to_top_id",
    "forum_topic",
    "media_type",
    "fwd_from_id",
    "context_group_id",
    "is_service",
    "reactions",
}


def _jsonl(path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _messages():
    return [
        MessageData.from_dict(row)
        for row in _jsonl(NON_CHANNEL_FIXTURES / "corpus.jsonl")
    ]


class TestNonChannelContractJsonlFixtures(unittest.TestCase):
    def test_compact_ai_jsonl_uses_contract_key_set_and_omits_empty_values(self):
        rows = _jsonl(DB_EXPORT_FIXTURES / "expected_db_ai.jsonl")

        self.assertEqual(len(rows), 5)
        for row in rows:
            self.assertLessEqual(set(row), ALLOWED_AI_KEYS)
            for value in row.values():
                self.assertNotIn(value, (None, "", []))

    def test_compact_ai_jsonl_preserves_reply_media_and_reaction_fields(self):
        rows = {
            row["message_id"]: row
            for row in _jsonl(DB_EXPORT_FIXTURES / "expected_db_ai.jsonl")
        }

        self.assertEqual(rows[1002]["reply_to_id"], 1001)
        self.assertEqual(rows[2001]["reply_to_id"], 2999)
        self.assertEqual(rows[2001]["reply_to_top_id"], 2000)
        self.assertTrue(rows[2001]["forum_topic"])
        self.assertEqual(rows[2002]["media_type"], "photo")
        self.assertEqual(rows[2002]["fwd_from_id"], 7001)
        self.assertEqual(rows[2002]["edit_date"], 1767358920)
        self.assertEqual(rows[2002]["reactions"], [{"emoji": "+", "count": 2}])

    def test_db_export_ai_serializer_matches_fixture(self):
        rendered = "\n".join(
            serialize_json_message(message, profile="ai") for message in _messages()
        )
        expected = (
            (DB_EXPORT_FIXTURES / "expected_db_ai.jsonl")
            .read_text(encoding="utf-8")
            .rstrip("\n")
        )

        self.assertEqual(rendered, expected)

    def test_writer_state_fixture_shape_is_current_part_and_count_only(self):
        payload = json.loads(
            (DB_EXPORT_FIXTURES / "expected_writer_state.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(
            payload["path"],
            "DB_EXPORTS/.writer_state/Synthetic_Target_5001.json",
        )
        self.assertEqual(set(payload["state"]), {"current_part", "current_count"})
        self.assertEqual(payload["state"]["current_part"], 1)
        self.assertEqual(payload["state"]["current_count"], 5)

    def test_export_state_fixture_remains_deferred(self):
        self.assertFalse((DB_EXPORT_FIXTURES / "expected_export_state.json").exists())


if __name__ == "__main__":
    unittest.main()
