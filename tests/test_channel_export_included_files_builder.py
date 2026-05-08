import unittest
from pathlib import Path

from tg_msg_manager.services.channel_export.included_files_builder import (
    build_included_files,
)
from tg_msg_manager.services.channel_export.models import ChannelExportOptions


def make_options(**overrides):
    values = {
        "channel": "@daily",
        "limit": None,
        "media_mode": "metadata",
        "output_dir": Path("/exports"),
    }
    values.update(overrides)
    return ChannelExportOptions(**values)


class TestChannelExportIncludedFilesBuilder(unittest.TestCase):
    def test_metadata_mode_default_files_preserve_ordering(self):
        included = build_included_files(make_options())

        self.assertEqual(
            included,
            (
                "manifest.json",
                "media_manifest.jsonl",
                "messages.jsonl",
                "messages.txt",
            ),
        )

    def test_full_media_mode_includes_media_directory(self):
        included = build_included_files(make_options(media_mode="full"))

        self.assertEqual(included[-1], "media/")

    def test_include_jsonl_false_excludes_messages_jsonl(self):
        included = build_included_files(make_options(include_jsonl=False))

        self.assertNotIn("messages.jsonl", included)
        self.assertIn("messages.txt", included)

    def test_include_txt_false_excludes_messages_txt(self):
        included = build_included_files(make_options(include_txt=False))

        self.assertIn("messages.jsonl", included)
        self.assertNotIn("messages.txt", included)

    def test_discussion_result_none_excludes_discussion_files(self):
        included = build_included_files(make_options(), discussion_result=None)

        self.assertNotIn("discussion_comments.jsonl", included)
        self.assertNotIn("discussion_export_state.json", included)

    def test_discussion_result_includes_discussion_files(self):
        included = build_included_files(make_options(), discussion_result=object())

        self.assertEqual(
            included[-4:],
            (
                "discussion_comments.jsonl",
                "discussion_comments.txt",
                "discussion_threads.jsonl",
                "discussion_export_state.json",
            ),
        )


if __name__ == "__main__":
    unittest.main()
