import json
import unittest
from pathlib import Path

from tg_msg_manager.core.models.message import MessageData
from tg_msg_manager.services.rendering import (
    ContextReadableTxtRenderer,
    LegacyTxtRenderer,
    TxtRenderOptions,
)


FIXTURE_ROOT = Path(__file__).resolve().parents[2] / "fixtures"
NON_CHANNEL_FIXTURES = FIXTURE_ROOT / "non_channel_export"
DB_EXPORT_FIXTURES = FIXTURE_ROOT / "db_export"


def _read_messages():
    corpus = NON_CHANNEL_FIXTURES / "corpus.jsonl"
    return [
        MessageData.from_dict(json.loads(line))
        for line in corpus.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class TestNonChannelContractRenderingFixtures(unittest.TestCase):
    def test_fixture_corpus_is_parseable_synthetic_jsonl(self):
        messages = _read_messages()

        self.assertEqual(
            [message.message_id for message in messages], [1001, 1002, 1003, 2001, 2002]
        )
        self.assertEqual({message.user_id for message in messages}, {5001, 5101, 5102})
        self.assertTrue(
            all("Synthetic" in (message.author_name or "") for message in messages)
        )

    def test_context_readable_renderer_matches_non_channel_fixture(self):
        rendered = ContextReadableTxtRenderer().render(
            _read_messages(),
            TxtRenderOptions(
                profile="context-readable",
                target_user_id=5001,
                target_author_name="Synthetic Target",
                chat_title="multiple chats",
            ),
        )
        expected = (
            NON_CHANNEL_FIXTURES / "expected_export_context_readable.txt"
        ).read_text(encoding="utf-8")

        self.assertEqual(rendered, expected)
        for marker in (
            "# Telegram Export",
            "TXT profile: context-readable",
            "CONTEXT BLOCK #0001",
            "[REPLIED MESSAGE]",
            "[CONTEXT BEFORE]",
            "[TARGET MESSAGE]",
            "[TARGET MESSAGES]",
            "[CONTEXT AFTER]",
            "↪ missing reply #2999",
        ):
            self.assertIn(marker, rendered)

    def test_db_context_readable_fixture_matches_non_channel_fixture(self):
        export_expected = (
            NON_CHANNEL_FIXTURES / "expected_export_context_readable.txt"
        ).read_text(encoding="utf-8")
        db_expected = (
            DB_EXPORT_FIXTURES / "expected_db_context_readable.txt"
        ).read_text(encoding="utf-8")

        self.assertEqual(db_expected, export_expected)

    def test_legacy_renderer_matches_non_channel_fixture(self):
        rendered = LegacyTxtRenderer().render(
            _read_messages(),
            TxtRenderOptions(profile="legacy", target_user_id=5001),
        )
        expected = (NON_CHANNEL_FIXTURES / "expected_export_legacy.txt").read_text(
            encoding="utf-8"
        )

        self.assertEqual(rendered, expected)
        self.assertIn(
            "==================== 01 January 2026 ====================", rendered
        )
        self.assertIn('re: "Synthetic fixture context before alpha."', rendered)
        self.assertIn(
            "[reply_to: 2999 - original message not found in local DB]",
            rendered,
        )

    def test_fixture_readmes_keep_privacy_and_export_pm_boundaries(self):
        for readme_path in (
            NON_CHANNEL_FIXTURES / "README.md",
            DB_EXPORT_FIXTURES / "README.md",
        ):
            text = readme_path.read_text(encoding="utf-8")
            self.assertIn("All records in this directory are artificial", text)
            self.assertIn("real Telegram data", text)
            self.assertIn("sessions, credentials, logs", text)
            self.assertIn("`export-pm`", text)
            self.assertIn("private archive outputs", text)

    def test_fixture_payloads_do_not_contain_private_artifact_markers(self):
        forbidden = (
            "api_id",
            "api_hash",
            ".session",
            "PRIVAT_DIALOGS/",
            "messages.db",
            "DB_TARGETS.txt",
            "export-pm",
            "real_username",
        )
        for path in NON_CHANNEL_FIXTURES.glob("*"):
            if path.name == "README.md":
                continue
            text = path.read_text(encoding="utf-8")
            for marker in forbidden:
                self.assertNotIn(marker, text)


if __name__ == "__main__":
    unittest.main()
