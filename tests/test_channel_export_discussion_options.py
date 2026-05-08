import unittest

from tg_msg_manager.services.channel_export.discussions.options import (
    validate_discussion_mode,
    validate_max_comments_per_post,
)


class TestChannelDiscussionOptions(unittest.TestCase):
    def test_validate_discussion_mode_accepts_none(self):
        self.assertEqual(validate_discussion_mode("none"), "none")

    def test_validate_discussion_mode_accepts_full(self):
        self.assertEqual(validate_discussion_mode("full"), "full")

    def test_validate_discussion_mode_normalizes_input(self):
        self.assertEqual(validate_discussion_mode(" FULL "), "full")

    def test_validate_discussion_mode_rejects_invalid_mode(self):
        with self.assertRaises(ValueError):
            validate_discussion_mode("summary")

    def test_validate_max_comments_accepts_positive_values(self):
        self.assertEqual(validate_max_comments_per_post(1), 1)
        self.assertEqual(validate_max_comments_per_post(100), 100)

    def test_validate_max_comments_rejects_zero(self):
        with self.assertRaises(ValueError):
            validate_max_comments_per_post(0)

    def test_validate_max_comments_rejects_negative_value(self):
        with self.assertRaises(ValueError):
            validate_max_comments_per_post(-1)


if __name__ == "__main__":
    unittest.main()
