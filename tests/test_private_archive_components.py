import unittest
from datetime import datetime
from types import SimpleNamespace

from tg_msg_manager.core.models.message import MessageData
from tg_msg_manager.services.private_archive.archive_writer import PrivateArchiveWriter
from tg_msg_manager.services.private_archive.media_policy import (
    PrivateArchiveMediaPolicy,
)
from tg_msg_manager.services.private_archive.planner import PrivateArchivePlanner
from tg_msg_manager.services.private_archive.source_resolver import (
    PrivateArchiveSourceResolver,
)


class TestPrivateArchiveComponents(unittest.TestCase):
    def test_source_resolver_and_planner_create_deterministic_context(self):
        entity = SimpleNamespace(
            id=42,
            first_name="PM",
            last_name="User",
            username="pmuser",
        )

        descriptor = PrivateArchiveSourceResolver().resolve(entity)
        context = PrivateArchivePlanner(base_dir="/tmp/archive").build_context(
            descriptor
        )

        self.assertEqual(descriptor.user_id, 42)
        self.assertTrue(context.user_dir.endswith("PM_User_42"))
        self.assertTrue(context.chat_log_path.endswith("chat_log.txt"))

    def test_media_policy_categorizes_known_media_types(self):
        policy = PrivateArchiveMediaPolicy()

        self.assertEqual(policy.media_category("Photo"), "photos")
        self.assertEqual(policy.media_category("Video"), "videos")
        self.assertEqual(policy.media_category("Voice"), "voices")
        self.assertEqual(policy.media_category("Document"), "documents")

    def test_archive_writer_formats_pm_log(self):
        message = MessageData(
            message_id=5,
            chat_id=1,
            user_id=9,
            author_name="PM User",
            timestamp=datetime.fromtimestamp(1700000000),
            text="hello",
            media_type="Photo",
            reply_to_id=None,
            fwd_from_id=None,
            context_group_id=None,
            raw_payload={},
        )

        rendered = PrivateArchiveWriter().format_pm_log(message)

        self.assertIn("<PM User>", rendered)
        self.assertIn("<Attached Photo>", rendered)
        self.assertIn("hello", rendered)


if __name__ == "__main__":
    unittest.main()
