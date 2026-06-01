import unittest
from pathlib import Path
from types import SimpleNamespace

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
                "run_changelog.jsonl",
                "messages.jsonl",
                "messages.txt",
            ),
        )

    def test_full_media_mode_includes_media_directory(self):
        included = build_included_files(make_options(media_mode="full"))

        self.assertEqual(included[-1], "media/")

    def test_media_none_keeps_media_manifest_without_media_directory(self):
        included = build_included_files(make_options(media_mode="none"))

        self.assertIn("media_manifest.jsonl", included)
        self.assertNotIn("media/", included)

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

    def test_discussion_mode_included_files_matrix(self):
        cases = (
            (
                "none",
                None,
                (),
                (
                    "discussion_metadata.jsonl",
                    "discussion_comments.jsonl",
                    "discussion_comments.txt",
                    "discussion_threads.jsonl",
                    "discussion_export_state.json",
                ),
            ),
            (
                "metadata",
                SimpleNamespace(
                    mode="metadata",
                    metadata_jsonl_path=Path("/exports/discussion_metadata.jsonl"),
                ),
                ("discussion_metadata.jsonl",),
                (
                    "discussion_comments.jsonl",
                    "discussion_comments.txt",
                    "discussion_threads.jsonl",
                    "discussion_export_state.json",
                ),
            ),
            (
                "full",
                SimpleNamespace(mode="full"),
                (
                    "discussion_comments.jsonl",
                    "discussion_comments.txt",
                    "discussion_threads.jsonl",
                    "discussion_export_state.json",
                ),
                ("discussion_metadata.jsonl",),
            ),
        )

        for mode, result, expected, excluded in cases:
            with self.subTest(mode=mode):
                included = build_included_files(
                    make_options(discussion_mode=mode),
                    discussion_result=result,
                )

                for path in expected:
                    self.assertIn(path, included)
                for path in excluded:
                    self.assertNotIn(path, included)


if __name__ == "__main__":
    unittest.main()
