import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from tg_msg_manager.services.channel_export.discussions.jsonl_renderer import (
    ChannelDiscussionJsonlRenderer,
)
from tg_msg_manager.services.channel_export.discussions.models import (
    ChannelDiscussionCommentRecord,
    ChannelDiscussionThreadRecord,
)
from tg_msg_manager.services.channel_export.discussions.payload_writer import (
    WRITE_MODE_APPEND,
    ChannelDiscussionPayloadWriter,
)
from tg_msg_manager.services.channel_export.discussions.txt_renderer import (
    ChannelDiscussionTxtRenderer,
)


def make_comment(message_id: int) -> ChannelDiscussionCommentRecord:
    return ChannelDiscussionCommentRecord(
        message_id=message_id,
        discussion_chat_id=222,
        channel_id=111,
        channel_message_id=5001,
        discussion_root_message_id=98765,
        author_id=123,
        author_name="User",
        username="user",
        timestamp=datetime(2026, 5, 8, 12, 0, tzinfo=timezone.utc),
        text=f"comment {message_id}",
        reply_to_id=98765,
    )


def make_thread(status: str = "exported") -> ChannelDiscussionThreadRecord:
    return ChannelDiscussionThreadRecord(
        channel_id=111,
        channel_username="example",
        channel_message_id=5001,
        discussion_chat_id=222,
        discussion_root_message_id=98765,
        comments_count=1,
        exported_comments_count=1,
        status=status,
        error="boom" if status == "failed" else None,
    )


class TestChannelDiscussionPayloadWriter(unittest.TestCase):
    def _open_session(
        self, tmpdir: str, *, mode: str = "full", write_mode: str = "write"
    ):
        output_dir = Path(tmpdir)
        return ChannelDiscussionPayloadWriter().open_session(
            comments_jsonl_path=output_dir / "discussion_comments.jsonl",
            comments_txt_path=output_dir / "discussion_comments.txt",
            threads_jsonl_path=output_dir / "discussion_threads.jsonl",
            jsonl_renderer=ChannelDiscussionJsonlRenderer(),
            txt_renderer=ChannelDiscussionTxtRenderer(),
            run_mode=mode,
            write_mode=write_mode,
        )

    def test_writes_comments_txt_and_threads_with_stats(self):
        with tempfile.TemporaryDirectory(prefix="tg_discussion_writer_") as tmpdir:
            with self._open_session(tmpdir) as session:
                session.write_thread(make_thread())
                session.write_comment(make_comment(1))
                stats = session.finish()

            output_dir = Path(tmpdir)
            comments = (
                (output_dir / "discussion_comments.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
            )
            threads = (
                (output_dir / "discussion_threads.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
            )
            txt = (output_dir / "discussion_comments.txt").read_text(encoding="utf-8")
            self.assertEqual(json.loads(comments[0])["message_id"], 1)
            self.assertEqual(json.loads(threads[0])["status"], "exported")
            self.assertIn("comment 1", txt)
            self.assertEqual(stats.thread_count, 1)
            self.assertEqual(stats.comment_count, 1)

    def test_overwrite_mode_replaces_files_and_append_mode_appends(self):
        with tempfile.TemporaryDirectory(
            prefix="tg_discussion_writer_modes_"
        ) as tmpdir:
            with self._open_session(tmpdir) as session:
                session.write_thread(make_thread())
                session.write_comment(make_comment(1))

            with self._open_session(tmpdir) as session:
                session.write_thread(make_thread())
                session.write_comment(make_comment(2))

            output_dir = Path(tmpdir)
            comments_path = output_dir / "discussion_comments.jsonl"
            self.assertEqual(
                len(comments_path.read_text(encoding="utf-8").splitlines()), 1
            )
            self.assertEqual(
                json.loads(comments_path.read_text(encoding="utf-8").splitlines()[0])[
                    "message_id"
                ],
                2,
            )

            with self._open_session(
                tmpdir,
                mode="incremental",
                write_mode=WRITE_MODE_APPEND,
            ) as session:
                session.write_thread(make_thread())
                session.write_comment(make_comment(3))

            self.assertEqual(
                len(comments_path.read_text(encoding="utf-8").splitlines()), 2
            )

    def test_overwrite_failure_does_not_replace_existing_discussion_files(self):
        with tempfile.TemporaryDirectory(
            prefix="tg_discussion_writer_overwrite_fail_"
        ) as tmpdir:
            with self._open_session(tmpdir) as session:
                session.write_thread(make_thread())
                session.write_comment(make_comment(1))

            output_dir = Path(tmpdir)
            comments_path = output_dir / "discussion_comments.jsonl"
            original_comments = comments_path.read_text(encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "discussion write failed"):
                with self._open_session(tmpdir) as session:
                    session.write_thread(make_thread())
                    session.write_comment(make_comment(2))
                    raise RuntimeError("discussion write failed")

            self.assertEqual(
                comments_path.read_text(encoding="utf-8"),
                original_comments,
            )
            self.assertEqual(list(output_dir.glob("*.tmp")), [])

    def test_append_failure_does_not_partially_append_discussion_files(self):
        with tempfile.TemporaryDirectory(
            prefix="tg_discussion_writer_append_fail_"
        ) as tmpdir:
            with self._open_session(tmpdir) as session:
                session.write_thread(make_thread())
                session.write_comment(make_comment(1))

            output_dir = Path(tmpdir)
            comments_path = output_dir / "discussion_comments.jsonl"

            with self.assertRaisesRegex(RuntimeError, "discussion append failed"):
                with self._open_session(
                    tmpdir,
                    mode="incremental",
                    write_mode=WRITE_MODE_APPEND,
                ) as session:
                    session.write_thread(make_thread())
                    session.write_comment(make_comment(2))
                    raise RuntimeError("discussion append failed")

            comments = comments_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(comments), 1)
            self.assertEqual(json.loads(comments[0])["message_id"], 1)
            self.assertEqual(list(output_dir.glob("*.tmp")), [])

    def test_stats_count_failed_threads(self):
        with tempfile.TemporaryDirectory(
            prefix="tg_discussion_writer_failed_"
        ) as tmpdir:
            with self._open_session(tmpdir) as session:
                session.write_thread(make_thread(status="failed"))
                stats = session.finish()

            self.assertEqual(stats.thread_count, 1)
            self.assertEqual(stats.failed_thread_count, 1)


if __name__ == "__main__":
    unittest.main()
