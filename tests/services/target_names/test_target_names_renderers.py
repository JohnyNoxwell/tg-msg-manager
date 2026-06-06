import json
import unittest
from datetime import datetime

from tg_msg_manager.services.target_names.models import (
    TargetNameCurrent,
    TargetNameHistoryItem,
    TargetNamesResult,
)
from tg_msg_manager.services.target_names.renderers import (
    render_target_names_error,
    render_target_names_json,
    render_target_names_text,
)


def _fmt(value: int) -> str:
    return datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M:%S")


class TestTargetNamesRenderers(unittest.TestCase):
    def test_renders_text_all_fields_with_current_and_history(self):
        result = TargetNamesResult(
            status="found",
            target="1001",
            target_type="user",
            current=TargetNameCurrent(
                username="new_handle",
                display_name="New Name",
                first_seen=1700000000,
                last_seen=1700000030,
            ),
            history=(
                TargetNameHistoryItem(1700000000, "username", None, "old_handle"),
                TargetNameHistoryItem(
                    1700000030, "username", "old_handle", "new_handle"
                ),
            ),
        )

        rendered = render_target_names_text(result)

        self.assertIn("Target: 1001", rendered)
        self.assertIn("Type: user", rendered)
        self.assertIn("Current:", rendered)
        self.assertIn("username: @new_handle", rendered)
        self.assertIn(f"first_seen: {_fmt(1700000000)}", rendered)
        self.assertIn(f"last_seen: {_fmt(1700000030)}", rendered)
        self.assertIn("Name history:", rendered)
        self.assertIn(_fmt(1700000000), rendered)
        self.assertIn("-                -> @old_handle", rendered)
        self.assertIn("@old_handle      -> @new_handle", rendered)

    def test_renders_text_filtered_empty_history(self):
        result = TargetNamesResult(
            status="found",
            target="-1002001",
            target_type="channel",
            current=TargetNameCurrent(title="Synthetic Channel"),
        )

        rendered = render_target_names_text(result, field="title")

        self.assertEqual(
            rendered,
            "Target: -1002001\nType: channel\n\nTitle history:\n  No changes recorded.",
        )

    def test_renders_json_with_nulls_and_filtered_history(self):
        result = TargetNamesResult(
            status="found",
            target="1001",
            target_type="user",
            current=TargetNameCurrent(username="new_handle"),
            history=(
                TargetNameHistoryItem(1700000000, "username", None, "old_handle"),
                TargetNameHistoryItem(1700000030, "display_name", None, "New Name"),
            ),
        )

        payload = json.loads(render_target_names_json(result, field="username"))

        self.assertEqual(payload["target"], "1001")
        self.assertEqual(payload["target_type"], "user")
        self.assertEqual(payload["current"], {"username": "@new_handle"})
        self.assertEqual(
            payload["history"],
            [
                {
                    "observed_at": 1700000000,
                    "field": "username",
                    "old_value": None,
                    "new_value": "@old_handle",
                }
            ],
        )

    def test_renders_json_error(self):
        payload = json.loads(
            render_target_names_error(
                code="target_not_found", target="missing", json_output=True
            )
        )

        self.assertEqual(payload["error"]["code"], "target_not_found")
        self.assertEqual(payload["error"]["target"], "missing")


if __name__ == "__main__":
    unittest.main()
