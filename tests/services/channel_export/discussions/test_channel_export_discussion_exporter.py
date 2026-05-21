import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from tg_msg_manager.services.channel_export.discussions.exporter import (
    ChannelDiscussionExporter,
)
from tg_msg_manager.services.channel_export.discussions.models import (
    DISCUSSION_SOURCE_STATUS_NOT_LINKED,
    DISCUSSION_SOURCE_STATUS_RESOLVED,
    ChannelDiscussionFetchResult,
    ChannelDiscussionOptions,
    ChannelDiscussionSource,
)
from tg_msg_manager.services.channel_export.plan_builder import ChannelExportPlanBuilder
from tg_msg_manager.services.channel_export.models import (
    ChannelIdentity,
    ChannelPostRecord,
)


class FakeDiscussionFetcher:
    def __init__(self, results):
        self.results = results
        self.calls = []

    async def fetch_comments_for_post(
        self,
        *,
        channel_entity,
        discussion_entity,
        channel_post_record,
        max_comments_per_post,
    ):
        self.calls.append(
            {
                "channel_entity": channel_entity,
                "discussion_entity": discussion_entity,
                "message_id": channel_post_record.message_id,
                "max_comments_per_post": max_comments_per_post,
            }
        )
        result = self.results[channel_post_record.message_id]
        if isinstance(result, Exception):
            return ChannelDiscussionFetchResult(comments=(), error=str(result))
        return result


def make_post(
    message_id: int, *, replies_count=None, raw_payload=None
) -> ChannelPostRecord:
    return ChannelPostRecord(
        message_id=message_id,
        channel_id=111,
        channel_title="Example",
        channel_username="example",
        timestamp=datetime(2026, 5, 8, 12, 0, tzinfo=timezone.utc),
        text=f"post {message_id}",
        views=None,
        forwards=None,
        replies_count=replies_count,
        reactions={},
        media=(),
        raw_payload=raw_payload or {},
    )


def make_comment(message_id: int):
    return SimpleNamespace(
        id=message_id,
        sender_id=123,
        author_name="User",
        username="user",
        date=datetime(2026, 5, 8, 12, message_id % 60, tzinfo=timezone.utc),
        message=f"comment {message_id}",
        reply_to_id=98765,
        raw_payload={"id": message_id},
    )


class TestChannelDiscussionExporter(unittest.IsolatedAsyncioTestCase):
    def _build_plan(self, tmpdir: str):
        return ChannelExportPlanBuilder().build(
            Path(tmpdir),
            ChannelIdentity(channel_id=111, title="Example", username="example"),
        )

    async def test_exports_comments_for_current_run_posts(self):
        fetcher = FakeDiscussionFetcher(
            {
                5001: ChannelDiscussionFetchResult(
                    comments=(make_comment(1), make_comment(2)),
                    has_more=False,
                )
            }
        )

        with tempfile.TemporaryDirectory(prefix="tg_discussion_exporter_") as tmpdir:
            plan = self._build_plan(tmpdir)
            result = await ChannelDiscussionExporter(fetcher=fetcher).export_for_posts(
                channel_entity=SimpleNamespace(id=111),
                channel_identity=ChannelIdentity(
                    channel_id=111,
                    title="Example",
                    username="example",
                ),
                discussion_source=ChannelDiscussionSource(
                    status=DISCUSSION_SOURCE_STATUS_RESOLVED,
                    discussion_chat_id=222,
                    discussion_entity=SimpleNamespace(id=222),
                    error=None,
                ),
                posts=[make_post(5001, replies_count=2)],
                plan=plan,
                discussion_options=ChannelDiscussionOptions(
                    mode="full",
                    max_comments_per_post=100,
                ),
                run_mode="full",
            )

            self.assertEqual(fetcher.calls[0]["channel_entity"].id, 111)
            self.assertEqual(fetcher.calls[0]["discussion_entity"].id, 222)
            self.assertEqual(result.thread_count, 1)
            self.assertEqual(result.comment_count, 2)
            self.assertTrue(result.state_path.exists())
            comments = [
                json.loads(line)
                for line in plan.discussion_comments_jsonl_path.read_text(
                    encoding="utf-8"
                ).splitlines()
            ]
            threads = [
                json.loads(line)
                for line in plan.discussion_threads_jsonl_path.read_text(
                    encoding="utf-8"
                ).splitlines()
            ]
            self.assertEqual([comment["message_id"] for comment in comments], [1, 2])
            self.assertEqual(threads[0]["status"], "exported")

    async def test_metadata_mode_writes_metadata_without_fetching_comments(self):
        fetcher = FakeDiscussionFetcher({})

        with tempfile.TemporaryDirectory(
            prefix="tg_discussion_exporter_metadata_"
        ) as tmpdir:
            plan = self._build_plan(tmpdir)
            result = await ChannelDiscussionExporter(fetcher=fetcher).export_for_posts(
                channel_entity=SimpleNamespace(id=111),
                channel_identity=ChannelIdentity(
                    channel_id=111,
                    title="Example",
                    username="example",
                ),
                discussion_source=ChannelDiscussionSource(
                    status="disabled",
                    discussion_chat_id=None,
                    discussion_entity=None,
                    error=None,
                ),
                posts=[
                    make_post(
                        5001,
                        raw_payload={
                            "replies": {
                                "comments": True,
                                "channel_id": 222,
                                "replies": "90",
                            }
                        },
                    )
                ],
                plan=plan,
                discussion_options=ChannelDiscussionOptions(mode="metadata"),
                run_mode="full",
            )

            records = [
                json.loads(line)
                for line in plan.discussion_metadata_jsonl_path.read_text(
                    encoding="utf-8"
                ).splitlines()
            ]

            self.assertEqual(fetcher.calls, [])
            self.assertEqual(result.metadata_count, 1)
            self.assertEqual(result.comment_count, 0)
            self.assertEqual(result.discussion_chat_id, 222)
            self.assertEqual(records[0]["discussion_chat_id"], 222)
            self.assertEqual(records[0]["replies_count"], 90)
            self.assertTrue(records[0]["has_comments"])
            self.assertFalse(records[0]["comments_exported"])
            self.assertEqual(records[0]["source"], "raw_payload.replies")
            self.assertFalse(plan.discussion_comments_jsonl_path.exists())

    async def test_failed_thread_does_not_fail_whole_export(self):
        fetcher = FakeDiscussionFetcher(
            {
                5001: RuntimeError("thread unavailable"),
                5002: ChannelDiscussionFetchResult(
                    comments=(make_comment(3),),
                    has_more=False,
                ),
            }
        )

        with tempfile.TemporaryDirectory(
            prefix="tg_discussion_exporter_failed_"
        ) as tmpdir:
            plan = self._build_plan(tmpdir)
            result = await ChannelDiscussionExporter(fetcher=fetcher).export_for_posts(
                channel_entity=SimpleNamespace(id=111),
                channel_identity=ChannelIdentity(
                    channel_id=111,
                    title="Example",
                    username="example",
                ),
                discussion_source=ChannelDiscussionSource(
                    status=DISCUSSION_SOURCE_STATUS_RESOLVED,
                    discussion_chat_id=222,
                    discussion_entity=SimpleNamespace(id=222),
                    error=None,
                ),
                posts=[make_post(5001), make_post(5002)],
                plan=plan,
                discussion_options=ChannelDiscussionOptions(mode="full"),
                run_mode="full",
            )

            self.assertEqual(result.thread_count, 2)
            self.assertEqual(result.comment_count, 1)
            self.assertEqual(result.failed_thread_count, 1)
            thread_statuses = [
                json.loads(line)["status"]
                for line in plan.discussion_threads_jsonl_path.read_text(
                    encoding="utf-8"
                ).splitlines()
            ]
            self.assertEqual(thread_statuses, ["failed", "exported"])

    async def test_no_linked_discussion_writes_thread_statuses_without_fetching(self):
        fetcher = FakeDiscussionFetcher({})

        with tempfile.TemporaryDirectory(
            prefix="tg_discussion_exporter_not_linked_"
        ) as tmpdir:
            plan = self._build_plan(tmpdir)
            result = await ChannelDiscussionExporter(fetcher=fetcher).export_for_posts(
                channel_entity=SimpleNamespace(id=111),
                channel_identity=ChannelIdentity(
                    channel_id=111,
                    title="Example",
                    username="example",
                ),
                discussion_source=ChannelDiscussionSource(
                    status=DISCUSSION_SOURCE_STATUS_NOT_LINKED,
                    discussion_chat_id=None,
                    discussion_entity=None,
                    error=None,
                ),
                posts=[make_post(5001), make_post(5002)],
                plan=plan,
                discussion_options=ChannelDiscussionOptions(mode="full"),
                run_mode="full",
            )

            self.assertEqual(result.thread_count, 2)
            self.assertEqual(result.comment_count, 0)
            self.assertEqual(fetcher.calls, [])
            thread_statuses = [
                json.loads(line)["status"]
                for line in plan.discussion_threads_jsonl_path.read_text(
                    encoding="utf-8"
                ).splitlines()
            ]
            self.assertEqual(thread_statuses, ["not_linked", "not_linked"])

    async def test_post_without_discussion_replies_does_not_call_fetcher(self):
        fetcher = FakeDiscussionFetcher({})

        with tempfile.TemporaryDirectory(
            prefix="tg_discussion_exporter_no_replies_"
        ) as tmpdir:
            plan = self._build_plan(tmpdir)
            result = await ChannelDiscussionExporter(fetcher=fetcher).export_for_posts(
                channel_entity=SimpleNamespace(id=111),
                channel_identity=ChannelIdentity(
                    channel_id=111,
                    title="Example",
                    username="example",
                ),
                discussion_source=ChannelDiscussionSource(
                    status=DISCUSSION_SOURCE_STATUS_RESOLVED,
                    discussion_chat_id=222,
                    discussion_entity=SimpleNamespace(id=222),
                    error=None,
                ),
                posts=[make_post(5001, raw_payload={"replies": None})],
                plan=plan,
                discussion_options=ChannelDiscussionOptions(mode="full"),
                run_mode="full",
            )

            thread = json.loads(
                plan.discussion_threads_jsonl_path.read_text(
                    encoding="utf-8"
                ).splitlines()[0]
            )

            self.assertEqual(fetcher.calls, [])
            self.assertEqual(result.failed_thread_count, 0)
            self.assertEqual(thread["status"], "no_comments")
            self.assertEqual(thread["comments_count"], 0)

    async def test_max_comments_limit_produces_partial_status(self):
        fetcher = FakeDiscussionFetcher(
            {
                5001: ChannelDiscussionFetchResult(
                    comments=(make_comment(1), make_comment(2)),
                    has_more=True,
                )
            }
        )

        with tempfile.TemporaryDirectory(
            prefix="tg_discussion_exporter_partial_"
        ) as tmpdir:
            plan = self._build_plan(tmpdir)
            await ChannelDiscussionExporter(fetcher=fetcher).export_for_posts(
                channel_entity=SimpleNamespace(id=111),
                channel_identity=ChannelIdentity(
                    channel_id=111,
                    title="Example",
                    username="example",
                ),
                discussion_source=ChannelDiscussionSource(
                    status=DISCUSSION_SOURCE_STATUS_RESOLVED,
                    discussion_chat_id=222,
                    discussion_entity=SimpleNamespace(id=222),
                    error=None,
                ),
                posts=[make_post(5001)],
                plan=plan,
                discussion_options=ChannelDiscussionOptions(
                    mode="full",
                    max_comments_per_post=2,
                ),
                run_mode="full",
            )

            thread = json.loads(
                plan.discussion_threads_jsonl_path.read_text(
                    encoding="utf-8"
                ).splitlines()[0]
            )
            self.assertEqual(thread["status"], "partial")
            self.assertEqual(fetcher.calls[0]["max_comments_per_post"], 2)

    async def test_resolved_discussion_with_empty_fetch_writes_no_comments_status(self):
        fetcher = FakeDiscussionFetcher(
            {
                5001: ChannelDiscussionFetchResult(comments=(), has_more=False),
            }
        )

        with tempfile.TemporaryDirectory(
            prefix="tg_discussion_exporter_no_comments_"
        ) as tmpdir:
            plan = self._build_plan(tmpdir)
            result = await ChannelDiscussionExporter(fetcher=fetcher).export_for_posts(
                channel_entity=SimpleNamespace(id=111),
                channel_identity=ChannelIdentity(
                    channel_id=111,
                    title="Example",
                    username="example",
                ),
                discussion_source=ChannelDiscussionSource(
                    status=DISCUSSION_SOURCE_STATUS_RESOLVED,
                    discussion_chat_id=222,
                    discussion_entity=SimpleNamespace(id=222),
                    error=None,
                ),
                posts=[make_post(5001, replies_count=3)],
                plan=plan,
                discussion_options=ChannelDiscussionOptions(
                    mode="full",
                    max_comments_per_post=100,
                ),
                run_mode="full",
            )

            self.assertEqual(result.thread_count, 1)
            self.assertEqual(result.comment_count, 0)
            self.assertEqual(fetcher.calls[0]["message_id"], 5001)
            thread = json.loads(
                plan.discussion_threads_jsonl_path.read_text(
                    encoding="utf-8"
                ).splitlines()[0]
            )
            self.assertEqual(thread["status"], "no_comments")
            self.assertEqual(thread["discussion_chat_id"], 222)
            self.assertEqual(thread["comments_count"], 3)


if __name__ == "__main__":
    unittest.main()
