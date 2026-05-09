import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from tg_msg_manager.core.models.message import MessageData
from tg_msg_manager.services.channel_export import (
    ChannelExportOptions,
    ChannelExportService,
)
from tg_msg_manager.services.channel_export.discussions.exporter import (
    ChannelDiscussionExporter,
)
from tg_msg_manager.services.channel_export.discussions.resolver import (
    ChannelDiscussionResolver,
)
from tg_msg_manager.services.channel_export.discussions.models import (
    DISCUSSION_SOURCE_STATUS_RESOLVED,
    ChannelDiscussionFetchResult,
    ChannelDiscussionSource,
)


class FakeChannelEntity:
    def __init__(self, entity_id=123, title="Daily", username="daily"):
        self.id = entity_id
        self.title = title
        self.username = username
        self.broadcast = True
        self.is_channel = True


class FakeChannelClient:
    def __init__(self, entity, messages):
        self.entity = entity
        self.messages = list(messages)
        self.calls = []
        self.download_media_calls = 0

    async def get_entity(self, channel):
        self.calls.append(("get_entity", channel))
        return self.entity

    async def iter_messages(self, entity, limit=None, min_id=None):
        self.calls.append(
            ("iter_messages", getattr(entity, "id", entity), limit, min_id)
        )
        yielded = 0
        for message in self.messages:
            if min_id is not None and message.message_id <= min_id:
                continue
            yield message
            yielded += 1
            if limit is not None and yielded >= limit:
                break

    async def download_media(self, media, file=None):
        self.download_media_calls += 1
        if media is None:
            return None
        payload = media if isinstance(media, dict) else {"content": str(media)}
        if payload.get("raise_error"):
            raise RuntimeError(payload["raise_error"])
        if payload.get("return_none"):
            return None

        target_path = Path(file)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        content = payload.get("content", "")
        binary = payload.get("binary", False)
        if binary:
            target_path.write_bytes(
                content if isinstance(content, bytes) else str(content).encode("utf-8")
            )
        else:
            target_path.write_text(str(content), encoding="utf-8")
        return str(target_path)


class FailingManifestWriter:
    def write(self, path, manifest):
        del path, manifest
        raise RuntimeError("manifest write failed")


class FailingChannelPayloadSession:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return None

    def write_record(self, record):
        del record
        raise RuntimeError("channel payload write failed")

    def finish(self):
        raise RuntimeError("channel payload write failed")


class FailingChannelPayloadWriter:
    def open_session(self, **kwargs):
        del kwargs
        return FailingChannelPayloadSession()


class CountingDiscussionResolver:
    def __init__(self, source):
        self.source = source
        self.calls = []

    async def resolve(self, entity, posts=None):
        self.calls.append((entity, posts))
        return self.source


class FakeDiscussionFetcher:
    def __init__(self, results):
        self.results = dict(results)
        self.calls = []

    async def fetch_comments_for_post(
        self,
        *,
        channel_entity,
        discussion_entity,
        channel_post_record,
        max_comments_per_post,
    ):
        del discussion_entity
        self.calls.append(
            (channel_entity, channel_post_record.message_id, max_comments_per_post)
        )
        result = self.results[channel_post_record.message_id]
        if isinstance(result, Exception):
            return ChannelDiscussionFetchResult(comments=(), error=str(result))
        return result


class FailingDiscussionExporter:
    def __init__(self):
        self.calls = 0

    def load_state(self, path):
        del path
        return None

    async def export_for_posts(self, **kwargs):
        del kwargs
        self.calls += 1
        raise RuntimeError("discussion payload write failed")


def make_message(
    message_id,
    *,
    text,
    media_type=None,
    media_ref=None,
    is_service=False,
    raw_payload=None,
):
    return MessageData(
        message_id=message_id,
        chat_id=123,
        user_id=1,
        author_name="Poster",
        timestamp=datetime(2026, 5, 7, 10 + message_id, 0, tzinfo=timezone.utc),
        text=text,
        media_type=media_type,
        reply_to_id=None,
        fwd_from_id=None,
        context_group_id=None,
        raw_payload=raw_payload or {},
        is_service=is_service,
        media_ref=media_ref,
    )


def make_comment(message_id: int, *, text: str = "comment"):
    return type(
        "Comment",
        (),
        {
            "id": message_id,
            "sender_id": 123,
            "author_name": "Commenter",
            "username": "commenter",
            "date": datetime(2026, 5, 8, 12, message_id % 60, tzinfo=timezone.utc),
            "message": text,
            "reply_to_id": 98765,
            "raw_payload": {"id": message_id},
        },
    )()


def resolved_discussion_source():
    return ChannelDiscussionSource(
        status=DISCUSSION_SOURCE_STATUS_RESOLVED,
        discussion_chat_id=222,
        discussion_entity=FakeChannelEntity(entity_id=222, title="Comments"),
        error=None,
    )


class TestChannelExportService(unittest.IsolatedAsyncioTestCase):
    async def test_export_channel_writes_dataset_files_and_state(self):
        entity = FakeChannelEntity()
        client = FakeChannelClient(
            entity,
            [
                make_message(
                    1,
                    text="First",
                    media_type="Photo",
                    media_ref={"mime_type": "image/jpeg", "file_name": "a.jpg"},
                ),
                make_message(2, text="Second"),
            ],
        )

        with tempfile.TemporaryDirectory(prefix="tg_channel_service_") as tmpdir:
            service = ChannelExportService(client=client, base_dir=Path(tmpdir))
            result = await service.export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=10,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                )
            )

            self.assertEqual(result.run_mode, "full")
            self.assertEqual(result.message_count, 2)
            self.assertEqual(result.media_count, 1)
            self.assertEqual(result.posts_exported_this_run, 2)
            self.assertTrue(result.manifest_path.exists())
            self.assertTrue(result.state_path.exists())
            manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
            state = json.loads(result.state_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["export"]["message_count"], 2)
            self.assertEqual(manifest["export"]["media_count"], 1)
            self.assertEqual(manifest["discussion"], {"mode": "none"})
            self.assertEqual(manifest["source"]["username"], "daily")
            self.assertEqual(state["last_exported_message_id"], 2)
            self.assertFalse(
                (result.manifest_path.parent / "discussion_comments.jsonl").exists()
            )
            self.assertFalse(
                (result.manifest_path.parent / "discussion_threads.jsonl").exists()
            )
            self.assertFalse(
                (result.manifest_path.parent / "discussion_export_state.json").exists()
            )

    async def test_default_discussion_mode_does_not_call_discussion_components(self):
        entity = FakeChannelEntity()
        client = FakeChannelClient(entity, [make_message(1, text="First")])
        resolver = CountingDiscussionResolver(resolved_discussion_source())
        exporter = FailingDiscussionExporter()

        with tempfile.TemporaryDirectory(
            prefix="tg_channel_service_no_discussion_"
        ) as tmpdir:
            result = await ChannelExportService(
                client=client,
                base_dir=Path(tmpdir),
                discussion_resolver=resolver,
                discussion_exporter=exporter,
            ).export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                )
            )

            self.assertEqual(resolver.calls, [])
            self.assertEqual(exporter.calls, 0)
            self.assertEqual(result.discussion_mode, "none")
            self.assertFalse(
                (result.manifest_path.parent / "discussion_comments.jsonl").exists()
            )

    async def test_discussion_full_writes_dataset_files_state_and_manifest_summary(
        self,
    ):
        entity = FakeChannelEntity()
        client = FakeChannelClient(
            entity,
            [make_message(1, text="First"), make_message(2, text="Second")],
        )
        fetcher = FakeDiscussionFetcher(
            {
                1: ChannelDiscussionFetchResult(
                    comments=(make_comment(101, text="one"),),
                    has_more=False,
                ),
                2: ChannelDiscussionFetchResult(
                    comments=(make_comment(201, text="two"),),
                    has_more=False,
                ),
            }
        )

        with tempfile.TemporaryDirectory(
            prefix="tg_channel_service_discussion_"
        ) as tmpdir:
            result = await ChannelExportService(
                client=client,
                base_dir=Path(tmpdir),
                discussion_resolver=CountingDiscussionResolver(
                    resolved_discussion_source()
                ),
                discussion_exporter=ChannelDiscussionExporter(fetcher=fetcher),
            ).export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                    discussion_mode="full",
                    max_comments_per_post=100,
                )
            )

            manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
            discussion_state = json.loads(
                result.discussion_state_path.read_text(encoding="utf-8")
            )
            comments = [
                json.loads(line)
                for line in result.discussion_comments_jsonl_path.read_text(
                    encoding="utf-8"
                ).splitlines()
            ]
            threads = [
                json.loads(line)
                for line in result.discussion_threads_jsonl_path.read_text(
                    encoding="utf-8"
                ).splitlines()
            ]

            self.assertEqual(result.discussion_thread_count_this_run, 2)
            self.assertEqual(result.discussion_comment_count_this_run, 2)
            self.assertEqual(
                [(call[1], call[2]) for call in fetcher.calls],
                [(1, 100), (2, 100)],
            )
            self.assertTrue(all(call[0] is entity for call in fetcher.calls))
            self.assertEqual(
                [comment["message_id"] for comment in comments], [101, 201]
            )
            self.assertEqual(
                [thread["status"] for thread in threads], ["exported", "exported"]
            )
            self.assertEqual(manifest["discussion"]["mode"], "full")
            self.assertEqual(manifest["discussion"]["discussion_chat_id"], 222)
            self.assertEqual(manifest["discussion"]["thread_count"], 2)
            self.assertEqual(manifest["discussion"]["comment_count"], 2)
            self.assertIn(
                "discussion_comments.jsonl",
                manifest["export"]["included_files"],
            )
            self.assertEqual(discussion_state["comment_count_total"], 2)

    async def test_discussion_metadata_writes_metadata_without_fetching_comments(self):
        entity = FakeChannelEntity()
        client = FakeChannelClient(
            entity,
            [
                make_message(
                    1,
                    text="First",
                    raw_payload={
                        "replies": {
                            "comments": True,
                            "channel_id": 222,
                            "replies": "90",
                        }
                    },
                )
            ],
        )
        resolver = CountingDiscussionResolver(resolved_discussion_source())
        fetcher = FakeDiscussionFetcher({})

        with tempfile.TemporaryDirectory(
            prefix="tg_channel_service_discussion_metadata_"
        ) as tmpdir:
            result = await ChannelExportService(
                client=client,
                base_dir=Path(tmpdir),
                discussion_resolver=resolver,
                discussion_exporter=ChannelDiscussionExporter(fetcher=fetcher),
            ).export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                    discussion_mode="metadata",
                )
            )

            manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
            metadata = [
                json.loads(line)
                for line in result.discussion_metadata_jsonl_path.read_text(
                    encoding="utf-8"
                ).splitlines()
            ]

            self.assertEqual(resolver.calls, [])
            self.assertEqual(fetcher.calls, [])
            self.assertEqual(result.discussion_mode, "metadata")
            self.assertEqual(result.discussion_metadata_count_this_run, 1)
            self.assertEqual(result.discussion_comment_count_this_run, 0)
            self.assertEqual(result.discussion_chat_id, 222)
            self.assertEqual(metadata[0]["channel_message_id"], 1)
            self.assertTrue(metadata[0]["has_comments"])
            self.assertEqual(metadata[0]["discussion_chat_id"], 222)
            self.assertEqual(metadata[0]["replies_count"], 90)
            self.assertFalse(metadata[0]["comments_exported"])
            self.assertEqual(manifest["discussion"]["mode"], "metadata")
            self.assertEqual(manifest["discussion"]["metadata_count"], 1)
            self.assertFalse(manifest["discussion"]["comments_exported"])
            self.assertIn(
                "discussion_metadata.jsonl",
                manifest["export"]["included_files"],
            )
            self.assertFalse(
                (result.manifest_path.parent / "discussion_comments.jsonl").exists()
            )
            self.assertIsNone(result.discussion_state_path)

    async def test_discussion_full_uses_per_post_replies_metadata_fallback(self):
        entity = FakeChannelEntity()
        client = FakeChannelClient(
            entity,
            [
                make_message(
                    1,
                    text="First",
                    raw_payload={
                        "replies": {
                            "comments": True,
                            "channel_id": 222,
                            "replies": 3,
                        }
                    },
                )
            ],
        )
        fetcher = FakeDiscussionFetcher(
            {
                1: ChannelDiscussionFetchResult(comments=(), has_more=False),
            }
        )

        with tempfile.TemporaryDirectory(
            prefix="tg_channel_service_discussion_fallback_"
        ) as tmpdir:
            result = await ChannelExportService(
                client=client,
                base_dir=Path(tmpdir),
                discussion_resolver=ChannelDiscussionResolver(client),
                discussion_exporter=ChannelDiscussionExporter(fetcher=fetcher),
            ).export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                    discussion_mode="full",
                )
            )

            threads = [
                json.loads(line)
                for line in result.discussion_threads_jsonl_path.read_text(
                    encoding="utf-8"
                ).splitlines()
            ]

            self.assertEqual(result.discussion_chat_id, 222)
            self.assertEqual([(call[1], call[2]) for call in fetcher.calls], [(1, 100)])
            self.assertIs(fetcher.calls[0][0], entity)
            self.assertEqual(threads[0]["discussion_chat_id"], 222)
            self.assertEqual(threads[0]["status"], "no_comments")
            self.assertEqual(threads[0]["comments_count"], 3)
            self.assertNotEqual(threads[0]["status"], "not_linked")

    async def test_discussion_incremental_exports_only_new_posts(self):
        entity = FakeChannelEntity()
        first_fetcher = FakeDiscussionFetcher(
            {
                1: ChannelDiscussionFetchResult(comments=(make_comment(101),)),
                2: ChannelDiscussionFetchResult(comments=(make_comment(201),)),
            }
        )

        with tempfile.TemporaryDirectory(
            prefix="tg_channel_service_discussion_inc_"
        ) as tmpdir:
            await ChannelExportService(
                client=FakeChannelClient(
                    entity,
                    [make_message(1, text="First"), make_message(2, text="Second")],
                ),
                base_dir=Path(tmpdir),
                discussion_resolver=CountingDiscussionResolver(
                    resolved_discussion_source()
                ),
                discussion_exporter=ChannelDiscussionExporter(fetcher=first_fetcher),
            ).export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                    discussion_mode="full",
                )
            )

            second_fetcher = FakeDiscussionFetcher(
                {
                    3: ChannelDiscussionFetchResult(comments=(make_comment(301),)),
                }
            )
            result = await ChannelExportService(
                client=FakeChannelClient(
                    entity,
                    [
                        make_message(1, text="First"),
                        make_message(2, text="Second"),
                        make_message(3, text="Third"),
                    ],
                ),
                base_dir=Path(tmpdir),
                discussion_resolver=CountingDiscussionResolver(
                    resolved_discussion_source()
                ),
                discussion_exporter=ChannelDiscussionExporter(fetcher=second_fetcher),
            ).export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                    discussion_mode="full",
                )
            )

            comments = [
                json.loads(line)
                for line in result.discussion_comments_jsonl_path.read_text(
                    encoding="utf-8"
                ).splitlines()
            ]
            discussion_state = json.loads(
                result.discussion_state_path.read_text(encoding="utf-8")
            )
            self.assertEqual(result.run_mode, "incremental")
            self.assertEqual(
                [(call[1], call[2]) for call in second_fetcher.calls],
                [(3, 100)],
            )
            self.assertEqual(
                [comment["message_id"] for comment in comments], [101, 201, 301]
            )
            self.assertEqual(discussion_state["comment_count_total"], 3)

    async def test_discussion_no_new_posts_does_not_refetch_or_mutate_state(self):
        entity = FakeChannelEntity()

        with tempfile.TemporaryDirectory(
            prefix="tg_channel_service_discussion_nonew_"
        ) as tmpdir:
            first_fetcher = FakeDiscussionFetcher(
                {1: ChannelDiscussionFetchResult(comments=(make_comment(101),))}
            )
            first_result = await ChannelExportService(
                client=FakeChannelClient(entity, [make_message(1, text="Only")]),
                base_dir=Path(tmpdir),
                discussion_resolver=CountingDiscussionResolver(
                    resolved_discussion_source()
                ),
                discussion_exporter=ChannelDiscussionExporter(fetcher=first_fetcher),
            ).export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                    discussion_mode="full",
                )
            )
            initial_state = first_result.discussion_state_path.read_text(
                encoding="utf-8"
            )
            initial_comments = first_result.discussion_comments_jsonl_path.read_text(
                encoding="utf-8"
            )

            second_fetcher = FakeDiscussionFetcher({})
            resolver = CountingDiscussionResolver(resolved_discussion_source())
            second_result = await ChannelExportService(
                client=FakeChannelClient(entity, [make_message(1, text="Only")]),
                base_dir=Path(tmpdir),
                discussion_resolver=resolver,
                discussion_exporter=ChannelDiscussionExporter(fetcher=second_fetcher),
            ).export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                    discussion_mode="full",
                )
            )

            self.assertEqual(second_result.posts_exported_this_run, 0)
            self.assertEqual(resolver.calls, [])
            self.assertEqual(second_fetcher.calls, [])
            self.assertEqual(
                first_result.discussion_state_path.read_text(encoding="utf-8"),
                initial_state,
            )
            self.assertEqual(
                first_result.discussion_comments_jsonl_path.read_text(encoding="utf-8"),
                initial_comments,
            )

    async def test_force_discussion_export_overwrites_discussion_files_and_state(self):
        entity = FakeChannelEntity()

        with tempfile.TemporaryDirectory(
            prefix="tg_channel_service_discussion_force_"
        ) as tmpdir:
            await ChannelExportService(
                client=FakeChannelClient(entity, [make_message(1, text="First")]),
                base_dir=Path(tmpdir),
                discussion_resolver=CountingDiscussionResolver(
                    resolved_discussion_source()
                ),
                discussion_exporter=ChannelDiscussionExporter(
                    fetcher=FakeDiscussionFetcher(
                        {1: ChannelDiscussionFetchResult(comments=(make_comment(101),))}
                    )
                ),
            ).export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                    discussion_mode="full",
                )
            )

            result = await ChannelExportService(
                client=FakeChannelClient(entity, [make_message(2, text="Second")]),
                base_dir=Path(tmpdir),
                discussion_resolver=CountingDiscussionResolver(
                    resolved_discussion_source()
                ),
                discussion_exporter=ChannelDiscussionExporter(
                    fetcher=FakeDiscussionFetcher(
                        {2: ChannelDiscussionFetchResult(comments=(make_comment(201),))}
                    )
                ),
            ).export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                    discussion_mode="full",
                    force=True,
                )
            )

            comments = [
                json.loads(line)
                for line in result.discussion_comments_jsonl_path.read_text(
                    encoding="utf-8"
                ).splitlines()
            ]
            discussion_state = json.loads(
                result.discussion_state_path.read_text(encoding="utf-8")
            )
            self.assertEqual([comment["message_id"] for comment in comments], [201])
            self.assertEqual(discussion_state["comment_count_total"], 1)

    async def test_failed_discussion_thread_is_recorded_without_failing_export(self):
        entity = FakeChannelEntity()
        fetcher = FakeDiscussionFetcher(
            {
                1: RuntimeError("thread failed"),
                2: ChannelDiscussionFetchResult(comments=(make_comment(201),)),
            }
        )

        with tempfile.TemporaryDirectory(
            prefix="tg_channel_service_discussion_failed_"
        ) as tmpdir:
            result = await ChannelExportService(
                client=FakeChannelClient(
                    entity,
                    [make_message(1, text="First"), make_message(2, text="Second")],
                ),
                base_dir=Path(tmpdir),
                discussion_resolver=CountingDiscussionResolver(
                    resolved_discussion_source()
                ),
                discussion_exporter=ChannelDiscussionExporter(fetcher=fetcher),
            ).export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                    discussion_mode="full",
                )
            )

            threads = [
                json.loads(line)
                for line in result.discussion_threads_jsonl_path.read_text(
                    encoding="utf-8"
                ).splitlines()
            ]
            self.assertEqual(result.failed_discussion_thread_count_this_run, 1)
            self.assertEqual(
                [thread["status"] for thread in threads], ["failed", "exported"]
            )

    async def test_discussion_payload_failure_does_not_advance_state(self):
        entity = FakeChannelEntity()

        with tempfile.TemporaryDirectory(
            prefix="tg_channel_service_discussion_writer_fail_"
        ) as tmpdir:
            await ChannelExportService(
                client=FakeChannelClient(entity, [make_message(1, text="First")]),
                base_dir=Path(tmpdir),
                discussion_resolver=CountingDiscussionResolver(
                    resolved_discussion_source()
                ),
                discussion_exporter=ChannelDiscussionExporter(
                    fetcher=FakeDiscussionFetcher(
                        {1: ChannelDiscussionFetchResult(comments=(make_comment(101),))}
                    )
                ),
            ).export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                    discussion_mode="full",
                )
            )
            state_path = Path(tmpdir) / "@daily__123" / "channel_export_state.json"
            discussion_state_path = (
                Path(tmpdir) / "@daily__123" / "discussion_export_state.json"
            )
            initial_state = state_path.read_text(encoding="utf-8")
            initial_discussion_state = discussion_state_path.read_text(encoding="utf-8")

            with self.assertRaisesRegex(
                RuntimeError,
                "discussion payload write failed",
            ):
                await ChannelExportService(
                    client=FakeChannelClient(
                        entity,
                        [make_message(1, text="First"), make_message(2, text="Second")],
                    ),
                    base_dir=Path(tmpdir),
                    discussion_resolver=CountingDiscussionResolver(
                        resolved_discussion_source()
                    ),
                    discussion_exporter=FailingDiscussionExporter(),
                ).export_channel(
                    ChannelExportOptions(
                        channel="@daily",
                        limit=None,
                        media_mode="metadata",
                        output_dir=Path(tmpdir),
                        discussion_mode="full",
                    )
                )

            self.assertEqual(state_path.read_text(encoding="utf-8"), initial_state)
            self.assertEqual(
                discussion_state_path.read_text(encoding="utf-8"),
                initial_discussion_state,
            )

    async def test_second_incremental_export_appends_only_new_posts(self):
        entity = FakeChannelEntity()
        first_client = FakeChannelClient(
            entity,
            [make_message(1, text="First"), make_message(2, text="Second")],
        )
        second_client = FakeChannelClient(
            entity,
            [
                make_message(1, text="First"),
                make_message(2, text="Second"),
                make_message(3, text="Third"),
                make_message(4, text="Fourth"),
            ],
        )

        with tempfile.TemporaryDirectory(
            prefix="tg_channel_service_incremental_"
        ) as tmpdir:
            first_service = ChannelExportService(
                client=first_client,
                base_dir=Path(tmpdir),
            )
            await first_service.export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                )
            )

            second_service = ChannelExportService(
                client=second_client,
                base_dir=Path(tmpdir),
            )
            result = await second_service.export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                )
            )

            jsonl_lines = result.messages_jsonl_path.read_text(
                encoding="utf-8"
            ).splitlines()
            exported_ids = [json.loads(line)["message_id"] for line in jsonl_lines]
            state = json.loads(result.state_path.read_text(encoding="utf-8"))
            self.assertEqual(result.run_mode, "incremental")
            self.assertEqual(result.posts_exported_this_run, 2)
            self.assertEqual(result.message_count, 4)
            self.assertEqual(exported_ids, [1, 2, 3, 4])
            self.assertEqual(state["message_count_total"], 4)
            self.assertEqual(state["last_exported_message_id"], 4)
            self.assertEqual(second_client.calls[-1][-1], 2)

    async def test_no_new_posts_emits_event_and_keeps_state_unchanged(self):
        entity = FakeChannelEntity()
        client = FakeChannelClient(entity, [make_message(1, text="Only")])

        with tempfile.TemporaryDirectory(prefix="tg_channel_service_no_new_") as tmpdir:
            service = ChannelExportService(client=client, base_dir=Path(tmpdir))
            await service.export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                )
            )
            state_path = Path(tmpdir) / "@daily__123" / "channel_export_state.json"
            initial_state = state_path.read_text(encoding="utf-8")
            events = []
            second_service = ChannelExportService(
                client=client,
                base_dir=Path(tmpdir),
                event_sink=events.append,
            )

            result = await second_service.export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                )
            )

            self.assertEqual(result.run_mode, "incremental")
            self.assertEqual(result.posts_exported_this_run, 0)
            self.assertEqual(result.message_count, 1)
            self.assertEqual(state_path.read_text(encoding="utf-8"), initial_state)
            self.assertEqual(events[-2].name, "channel_export.no_new_posts")

    async def test_force_reexport_overwrites_existing_dataset(self):
        entity = FakeChannelEntity()
        first_client = FakeChannelClient(entity, [make_message(1, text="First")])
        second_client = FakeChannelClient(entity, [make_message(2, text="Second")])

        with tempfile.TemporaryDirectory(prefix="tg_channel_service_force_") as tmpdir:
            await ChannelExportService(
                client=first_client,
                base_dir=Path(tmpdir),
            ).export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                )
            )

            result = await ChannelExportService(
                client=second_client,
                base_dir=Path(tmpdir),
            ).export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                    force=True,
                )
            )

            exported_ids = [
                json.loads(line)["message_id"]
                for line in result.messages_jsonl_path.read_text(
                    encoding="utf-8"
                ).splitlines()
            ]
            self.assertEqual(result.run_mode, "force_full")
            self.assertEqual(exported_ids, [2])
            self.assertEqual(result.message_count, 1)

    async def test_state_is_not_updated_when_manifest_write_fails(self):
        entity = FakeChannelEntity()
        first_client = FakeChannelClient(entity, [make_message(1, text="First")])
        second_client = FakeChannelClient(
            entity,
            [make_message(1, text="First"), make_message(2, text="Second")],
        )

        with tempfile.TemporaryDirectory(
            prefix="tg_channel_service_failure_"
        ) as tmpdir:
            await ChannelExportService(
                client=first_client,
                base_dir=Path(tmpdir),
            ).export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                )
            )

            state_path = Path(tmpdir) / "@daily__123" / "channel_export_state.json"
            initial_state = json.loads(state_path.read_text(encoding="utf-8"))

            with self.assertRaisesRegex(RuntimeError, "manifest write failed"):
                await ChannelExportService(
                    client=second_client,
                    base_dir=Path(tmpdir),
                    manifest_writer=FailingManifestWriter(),
                ).export_channel(
                    ChannelExportOptions(
                        channel="@daily",
                        limit=None,
                        media_mode="metadata",
                        output_dir=Path(tmpdir),
                    )
                )

            state_after_failure = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(state_after_failure, initial_state)

    async def test_state_is_not_updated_when_channel_payload_write_fails(self):
        entity = FakeChannelEntity()

        with tempfile.TemporaryDirectory(
            prefix="tg_channel_service_payload_failure_"
        ) as tmpdir:
            await ChannelExportService(
                client=FakeChannelClient(entity, [make_message(1, text="First")]),
                base_dir=Path(tmpdir),
            ).export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                )
            )

            state_path = Path(tmpdir) / "@daily__123" / "channel_export_state.json"
            initial_state = state_path.read_text(encoding="utf-8")

            with self.assertRaisesRegex(
                RuntimeError,
                "channel payload write failed",
            ):
                await ChannelExportService(
                    client=FakeChannelClient(
                        entity,
                        [make_message(1, text="First"), make_message(2, text="Second")],
                    ),
                    base_dir=Path(tmpdir),
                    payload_writer=FailingChannelPayloadWriter(),
                ).export_channel(
                    ChannelExportOptions(
                        channel="@daily",
                        limit=None,
                        media_mode="metadata",
                        output_dir=Path(tmpdir),
                    )
                )

            self.assertEqual(state_path.read_text(encoding="utf-8"), initial_state)

    async def test_discussion_state_is_not_saved_when_manifest_write_fails(self):
        entity = FakeChannelEntity()

        with tempfile.TemporaryDirectory(
            prefix="tg_channel_service_discussion_manifest_failure_"
        ) as tmpdir:
            await ChannelExportService(
                client=FakeChannelClient(entity, [make_message(1, text="First")]),
                base_dir=Path(tmpdir),
                discussion_resolver=CountingDiscussionResolver(
                    resolved_discussion_source()
                ),
                discussion_exporter=ChannelDiscussionExporter(
                    fetcher=FakeDiscussionFetcher(
                        {1: ChannelDiscussionFetchResult(comments=(make_comment(101),))}
                    )
                ),
            ).export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                    discussion_mode="full",
                )
            )

            state_path = Path(tmpdir) / "@daily__123" / "channel_export_state.json"
            discussion_state_path = (
                Path(tmpdir) / "@daily__123" / "discussion_export_state.json"
            )
            initial_state = state_path.read_text(encoding="utf-8")
            initial_discussion_state = discussion_state_path.read_text(encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "manifest write failed"):
                await ChannelExportService(
                    client=FakeChannelClient(
                        entity,
                        [make_message(1, text="First"), make_message(2, text="Second")],
                    ),
                    base_dir=Path(tmpdir),
                    manifest_writer=FailingManifestWriter(),
                    discussion_resolver=CountingDiscussionResolver(
                        resolved_discussion_source()
                    ),
                    discussion_exporter=ChannelDiscussionExporter(
                        fetcher=FakeDiscussionFetcher(
                            {
                                2: ChannelDiscussionFetchResult(
                                    comments=(make_comment(201),)
                                )
                            }
                        )
                    ),
                ).export_channel(
                    ChannelExportOptions(
                        channel="@daily",
                        limit=None,
                        media_mode="metadata",
                        output_dir=Path(tmpdir),
                        discussion_mode="full",
                    )
                )

            self.assertEqual(state_path.read_text(encoding="utf-8"), initial_state)
            self.assertEqual(
                discussion_state_path.read_text(encoding="utf-8"),
                initial_discussion_state,
            )

    async def test_export_channel_emits_progress_and_completion_events(self):
        entity = FakeChannelEntity()
        client = FakeChannelClient(
            entity,
            [
                make_message(1, text="One"),
                make_message(2, text="Two"),
                make_message(3, text="Three"),
            ],
        )
        events = []

        with tempfile.TemporaryDirectory(prefix="tg_channel_service_events_") as tmpdir:
            service = ChannelExportService(
                client=client,
                base_dir=Path(tmpdir),
                event_sink=events.append,
                progress_interval=2,
            )
            await service.export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                )
            )

            event_names = [event.name for event in events]
            self.assertIn("channel_export.started", event_names)
            self.assertIn("channel_export.channel_resolved", event_names)
            self.assertIn("channel_export.state_loaded", event_names)
            self.assertIn("channel_export.progress", event_names)
            self.assertEqual(events[-1].name, "channel_export.completed")
            progress_payloads = [
                event.payload
                for event in events
                if event.name == "channel_export.progress"
            ]
            self.assertEqual(progress_payloads[-1]["processed_posts"], 3)

    async def test_full_media_mode_downloads_media_and_records_sha256(self):
        entity = FakeChannelEntity()
        client = FakeChannelClient(
            entity,
            [
                make_message(
                    1,
                    text="Photo",
                    media_type="Photo",
                    media_ref={
                        "mime_type": "image/jpeg",
                        "file_name": "a.jpg",
                        "content": "hello-media",
                    },
                )
            ],
        )

        with tempfile.TemporaryDirectory(prefix="tg_channel_service_full_") as tmpdir:
            service = ChannelExportService(client=client, base_dir=Path(tmpdir))
            result = await service.export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="full",
                    output_dir=Path(tmpdir),
                )
            )

            manifest_rows = [
                json.loads(line)
                for line in result.media_manifest_path.read_text(
                    encoding="utf-8"
                ).splitlines()
            ]
            self.assertEqual(client.download_media_calls, 1)
            self.assertEqual(result.downloaded_media_count_this_run, 1)
            self.assertEqual(manifest_rows[0]["download_status"], "downloaded")
            self.assertTrue(manifest_rows[0]["sha256"])
            self.assertIsNone(manifest_rows[0]["error"])
            self.assertNotEqual(manifest_rows[0]["download_status"], "pending")

    async def test_full_media_manifest_references_magic_resolved_final_mp4_path(self):
        content = b"\x00\x00\x00\x18ftypisom\x00\x00\x00\x00payload"
        entity = FakeChannelEntity()
        client = FakeChannelClient(
            entity,
            [
                make_message(
                    3,
                    text="Video document",
                    media_type="Document",
                    media_ref={
                        "mime_type": "application/octet-stream",
                        "content": content,
                        "binary": True,
                    },
                )
            ],
        )

        with tempfile.TemporaryDirectory(
            prefix="tg_channel_service_magic_mp4_"
        ) as tmpdir:
            result = await ChannelExportService(
                client=client, base_dir=Path(tmpdir)
            ).export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="full",
                    output_dir=Path(tmpdir),
                )
            )

            manifest_rows = [
                json.loads(line)
                for line in result.media_manifest_path.read_text(
                    encoding="utf-8"
                ).splitlines()
            ]
            final_path = "media/videos/0000000003_01.mp4"
            self.assertEqual(manifest_rows[0]["download_status"], "downloaded")
            self.assertEqual(manifest_rows[0]["local_path"], final_path)
            self.assertEqual(manifest_rows[0]["final_path"], final_path)
            self.assertEqual(manifest_rows[0]["detected_extension"], ".mp4")
            self.assertEqual(manifest_rows[0]["filename_strategy"], "magic_bytes")
            self.assertFalse(final_path.endswith(".bin"))
            self.assertTrue((result.manifest_path.parent / final_path).exists())
            self.assertFalse(
                (
                    result.manifest_path.parent / "media/documents/0000000003_01.bin"
                ).exists()
            )

    async def test_full_media_mode_skips_existing_file(self):
        entity = FakeChannelEntity()
        client = FakeChannelClient(
            entity,
            [
                make_message(
                    1,
                    text="Photo",
                    media_type="Photo",
                    media_ref={
                        "mime_type": "image/jpeg",
                        "file_name": "a.jpg",
                        "content": "first",
                    },
                )
            ],
        )

        with tempfile.TemporaryDirectory(
            prefix="tg_channel_service_existing_"
        ) as tmpdir:
            output_dir = Path(tmpdir)
            await ChannelExportService(
                client=client, base_dir=output_dir
            ).export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="full",
                    output_dir=output_dir,
                )
            )
            second_client = FakeChannelClient(entity, client.messages)
            result = await ChannelExportService(
                client=second_client,
                base_dir=output_dir,
            ).export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="full",
                    output_dir=output_dir,
                    force=True,
                )
            )

            rows = [
                json.loads(line)
                for line in result.media_manifest_path.read_text(
                    encoding="utf-8"
                ).splitlines()
            ]
            self.assertEqual(rows[0]["download_status"], "already_exists")
            self.assertEqual(result.already_existing_media_count_this_run, 1)

    async def test_full_media_mode_skips_by_size_and_type(self):
        entity = FakeChannelEntity()
        client = FakeChannelClient(
            entity,
            [
                make_message(
                    1,
                    text="Video",
                    media_type="Video",
                    media_ref={
                        "mime_type": "video/mp4",
                        "file_name": "clip.mp4",
                        "file_size": 10_000_000,
                        "content": "video",
                    },
                ),
                make_message(
                    2,
                    text="Doc",
                    media_type="Document",
                    media_ref={
                        "mime_type": "application/pdf",
                        "file_name": "report.pdf",
                        "file_size": 512,
                        "content": "pdf",
                    },
                ),
            ],
        )

        with tempfile.TemporaryDirectory(prefix="tg_channel_service_skip_") as tmpdir:
            result = await ChannelExportService(
                client=client, base_dir=Path(tmpdir)
            ).export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="full",
                    output_dir=Path(tmpdir),
                    max_media_size=1024,
                    media_types=("video",),
                )
            )

            rows = [
                json.loads(line)
                for line in result.media_manifest_path.read_text(
                    encoding="utf-8"
                ).splitlines()
            ]
            self.assertEqual(rows[0]["download_status"], "skipped_by_size")
            self.assertEqual(rows[1]["download_status"], "skipped_by_type")
            self.assertEqual(result.skipped_by_size_count_this_run, 1)
            self.assertEqual(result.skipped_by_type_count_this_run, 1)
            self.assertEqual(client.download_media_calls, 0)

    async def test_media_download_failure_is_recorded_without_failing_export(self):
        entity = FakeChannelEntity()
        client = FakeChannelClient(
            entity,
            [
                make_message(
                    1,
                    text="Broken",
                    media_type="Photo",
                    media_ref={
                        "mime_type": "image/jpeg",
                        "file_name": "bad.jpg",
                        "raise_error": "network down",
                    },
                )
            ],
        )

        with tempfile.TemporaryDirectory(
            prefix="tg_channel_service_failure_media_"
        ) as tmpdir:
            result = await ChannelExportService(
                client=client, base_dir=Path(tmpdir)
            ).export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="full",
                    output_dir=Path(tmpdir),
                )
            )

            rows = [
                json.loads(line)
                for line in result.media_manifest_path.read_text(
                    encoding="utf-8"
                ).splitlines()
            ]
            self.assertEqual(result.failed_media_count_this_run, 1)
            self.assertEqual(rows[0]["download_status"], "failed")
            self.assertEqual(rows[0]["error"], "network down")
            self.assertIsNone(rows[0]["sha256"])

    async def test_missing_media_ref_becomes_failed_without_pending_status(self):
        entity = FakeChannelEntity()
        client = FakeChannelClient(
            entity,
            [
                make_message(
                    1,
                    text="Missing ref",
                    media_type="Photo",
                    media_ref=None,
                )
            ],
        )

        with tempfile.TemporaryDirectory(
            prefix="tg_channel_service_missing_ref_"
        ) as tmpdir:
            result = await ChannelExportService(
                client=client, base_dir=Path(tmpdir)
            ).export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="full",
                    output_dir=Path(tmpdir),
                )
            )

            rows = [
                json.loads(line)
                for line in result.media_manifest_path.read_text(
                    encoding="utf-8"
                ).splitlines()
            ]
            self.assertEqual(result.failed_media_count_this_run, 1)
            self.assertEqual(rows[0]["download_status"], "failed")
            self.assertEqual(
                rows[0]["error"],
                "Media reference is unavailable for download",
            )
            self.assertIsNone(rows[0]["sha256"])

    async def test_full_media_emits_media_progress_and_failure_events(self):
        entity = FakeChannelEntity()
        client = FakeChannelClient(
            entity,
            [
                make_message(
                    1,
                    text="Photo",
                    media_type="Photo",
                    media_ref={
                        "mime_type": "image/jpeg",
                        "file_name": "a.jpg",
                        "content": "hello-media",
                    },
                ),
                make_message(
                    2,
                    text="Broken",
                    media_type="Photo",
                    media_ref={
                        "mime_type": "image/jpeg",
                        "file_name": "bad.jpg",
                        "raise_error": "network down",
                    },
                ),
            ],
        )
        events = []

        with tempfile.TemporaryDirectory(
            prefix="tg_channel_service_media_events_"
        ) as tmpdir:
            await ChannelExportService(
                client=client,
                base_dir=Path(tmpdir),
                event_sink=events.append,
            ).export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="full",
                    output_dir=Path(tmpdir),
                )
            )

            event_names = [event.name for event in events]
            self.assertIn("channel_export.media_progress", event_names)
            self.assertIn("channel_export.media_downloaded", event_names)
            self.assertIn("channel_export.media_failed", event_names)
            progress_payloads = [
                event.payload
                for event in events
                if event.name == "channel_export.media_progress"
            ]
            self.assertEqual(progress_payloads[-1]["processed_media"], 2)
            self.assertEqual(progress_payloads[-1]["downloaded"], 1)
            self.assertEqual(progress_payloads[-1]["failed"], 1)

    async def test_export_channel_does_not_download_media_in_metadata_mode(self):
        entity = FakeChannelEntity()
        client = FakeChannelClient(
            entity,
            [
                make_message(
                    1,
                    text="Photo",
                    media_type="Photo",
                    media_ref={"mime_type": "image/jpeg", "file_name": "a.jpg"},
                )
            ],
        )

        with tempfile.TemporaryDirectory(prefix="tg_channel_service_media_") as tmpdir:
            service = ChannelExportService(client=client, base_dir=Path(tmpdir))
            await service.export_channel(
                ChannelExportOptions(
                    channel="@daily",
                    limit=None,
                    media_mode="metadata",
                    output_dir=Path(tmpdir),
                )
            )

            self.assertEqual(client.download_media_calls, 0)


if __name__ == "__main__":
    unittest.main()
