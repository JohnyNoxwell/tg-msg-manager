import sys
import os
import json
import unittest
from datetime import datetime
from unittest.mock import MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tg_msg_manager.core.models.message import MessageData
from tg_msg_manager.services.db_exporter import DBExportService


class TestDBExporter(unittest.TestCase):
    def setUp(self):
        self.storage = MagicMock()
        self.service = DBExportService(self.storage)

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

        payload = json.loads(self.service.format_message(msg, as_json=True, json_profile="full"))

        self.assertIn("raw_payload", payload)
        self.assertEqual(payload["reply_to_id"], 9)

    def test_resolve_export_author_name_prefers_message_author_when_user_card_is_empty(self):
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


if __name__ == "__main__":
    unittest.main()
