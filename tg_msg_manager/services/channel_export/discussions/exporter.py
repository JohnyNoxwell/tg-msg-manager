from typing import Any, Iterable, Optional

from .artifact_builder import ChannelDiscussionArtifactBuilder
from .fetcher import ChannelDiscussionFetcher
from .jsonl_renderer import ChannelDiscussionJsonlRenderer
from .mapper import ChannelDiscussionMapper
from .models import (
    DISCUSSION_SOURCE_STATUS_RESOLVED,
    ChannelDiscussionExportResult,
    ChannelDiscussionExportState,
    ChannelDiscussionOptions,
    ChannelDiscussionSource,
)
from .options import DISCUSSION_MODE_METADATA, DISCUSSION_MODE_NONE
from .payload_writer import (
    WRITE_MODE_APPEND,
    WRITE_MODE_OVERWRITE,
    ChannelDiscussionMetadataPayloadWriter,
    ChannelDiscussionPayloadWriter,
)
from ..state_consistency import (
    validate_discussion_state_for_incremental,
    validate_discussion_state_matches_channel,
    validate_discussion_state_matches_source,
)
from .state_manager import ChannelDiscussionStateManager
from .txt_renderer import ChannelDiscussionTxtRenderer


class ChannelDiscussionExporter:
    def __init__(
        self,
        *,
        fetcher: ChannelDiscussionFetcher,
        mapper: Optional[ChannelDiscussionMapper] = None,
        jsonl_renderer: Optional[ChannelDiscussionJsonlRenderer] = None,
        txt_renderer: Optional[ChannelDiscussionTxtRenderer] = None,
        payload_writer: Optional[ChannelDiscussionPayloadWriter] = None,
        metadata_payload_writer: Optional[
            ChannelDiscussionMetadataPayloadWriter
        ] = None,
        state_manager: Optional[ChannelDiscussionStateManager] = None,
        artifact_builder: Optional[ChannelDiscussionArtifactBuilder] = None,
    ):
        self.fetcher = fetcher
        self.mapper = mapper or ChannelDiscussionMapper()
        self.jsonl_renderer = jsonl_renderer or ChannelDiscussionJsonlRenderer()
        self.txt_renderer = txt_renderer or ChannelDiscussionTxtRenderer()
        self.payload_writer = payload_writer or ChannelDiscussionPayloadWriter()
        self.metadata_payload_writer = (
            metadata_payload_writer or ChannelDiscussionMetadataPayloadWriter()
        )
        self.state_manager = state_manager or ChannelDiscussionStateManager()
        self.artifact_builder = artifact_builder or ChannelDiscussionArtifactBuilder()

    async def export_for_posts(
        self,
        *,
        channel_entity: Any,
        channel_identity: Any,
        discussion_source: ChannelDiscussionSource,
        posts: Iterable[Any],
        plan: Any,
        discussion_options: ChannelDiscussionOptions,
        run_mode: str,
        previous_state: Optional[ChannelDiscussionExportState] = None,
        save_state: bool = True,
    ) -> ChannelDiscussionExportResult:
        if discussion_options.mode == DISCUSSION_MODE_NONE:
            return ChannelDiscussionExportResult(
                mode=discussion_options.mode,
                discussion_chat_id=None,
                thread_count=0,
                comment_count=0,
                failed_thread_count=0,
                comments_jsonl_path=None,
                comments_txt_path=None,
                threads_jsonl_path=None,
                state_path=None,
                state=None,
            )

        write_mode = (
            WRITE_MODE_APPEND if run_mode == "incremental" else WRITE_MODE_OVERWRITE
        )
        if discussion_options.mode == DISCUSSION_MODE_METADATA:
            return self._export_metadata_for_posts(
                channel_identity=channel_identity,
                posts=posts,
                plan=plan,
                discussion_options=discussion_options,
                run_mode=run_mode,
                write_mode=write_mode,
            )
        if previous_state is not None:
            validate_discussion_state_matches_channel(
                channel_identity,
                previous_state,
            )
            validate_discussion_state_matches_source(
                previous_state,
                discussion_source.discussion_chat_id,
            )
        session = self.payload_writer.open_session(
            comments_jsonl_path=plan.discussion_comments_jsonl_path,
            comments_txt_path=plan.discussion_comments_txt_path,
            threads_jsonl_path=plan.discussion_threads_jsonl_path,
            jsonl_renderer=self.jsonl_renderer,
            txt_renderer=self.txt_renderer,
            run_mode=run_mode,
            write_mode=write_mode,
        )

        with session:
            for post in posts:
                thread, comments = await self._build_thread_payload(
                    channel_identity=channel_identity,
                    channel_entity=channel_entity,
                    discussion_source=discussion_source,
                    post=post,
                    max_comments_per_post=discussion_options.max_comments_per_post,
                )
                session.write_thread(thread)
                for comment in comments:
                    session.write_comment(comment)
            stats = session.finish()

        state = self.state_manager.build_completed_state(
            channel=channel_identity,
            discussion_chat_id=discussion_source.discussion_chat_id,
            stats=stats,
            previous_state=previous_state,
        )
        if previous_state is not None and run_mode == "incremental":
            validate_discussion_state_for_incremental(previous_state, state)
        if save_state:
            self.state_manager.save(plan.discussion_state_path, state)
        return ChannelDiscussionExportResult(
            mode=discussion_options.mode,
            discussion_chat_id=discussion_source.discussion_chat_id,
            thread_count=stats.thread_count,
            comment_count=stats.comment_count,
            failed_thread_count=stats.failed_thread_count,
            comments_jsonl_path=plan.discussion_comments_jsonl_path,
            comments_txt_path=plan.discussion_comments_txt_path,
            threads_jsonl_path=plan.discussion_threads_jsonl_path,
            state_path=plan.discussion_state_path,
            state=state,
        )

    def _export_metadata_for_posts(
        self,
        *,
        channel_identity: Any,
        posts: Iterable[Any],
        plan: Any,
        discussion_options: ChannelDiscussionOptions,
        run_mode: str,
        write_mode: str,
    ) -> ChannelDiscussionExportResult:
        session = self.metadata_payload_writer.open_session(
            metadata_jsonl_path=plan.discussion_metadata_jsonl_path,
            jsonl_renderer=self.jsonl_renderer,
            run_mode=run_mode,
            write_mode=write_mode,
        )
        discussion_chat_id = None
        with session:
            for post in posts:
                record = self.artifact_builder.build_metadata_record(
                    channel_identity=channel_identity,
                    post=post,
                )
                if discussion_chat_id is None and record.discussion_chat_id is not None:
                    discussion_chat_id = record.discussion_chat_id
                session.write_metadata(record)
            stats = session.finish()
        return ChannelDiscussionExportResult(
            mode=discussion_options.mode,
            discussion_chat_id=discussion_chat_id,
            thread_count=0,
            comment_count=0,
            failed_thread_count=0,
            comments_jsonl_path=None,
            comments_txt_path=None,
            threads_jsonl_path=None,
            state_path=None,
            metadata_count=stats.thread_count,
            metadata_jsonl_path=plan.discussion_metadata_jsonl_path,
            state=None,
        )

    def load_state(self, path: Any) -> Optional[ChannelDiscussionExportState]:
        return self.state_manager.load(path)

    def save_result_state(self, result: ChannelDiscussionExportResult) -> None:
        if result.state_path is None or result.state is None:
            return
        self.state_manager.save(result.state_path, result.state)

    async def _build_thread_payload(
        self,
        *,
        channel_identity: Any,
        channel_entity: Any,
        discussion_source: ChannelDiscussionSource,
        post: Any,
        max_comments_per_post: int,
    ):
        if discussion_source.status == "not_linked":
            return (
                self.artifact_builder.build_not_linked_thread(
                    channel_identity=channel_identity,
                    post=post,
                    discussion_source=discussion_source,
                ),
                (),
            )
        if (
            discussion_source.status != DISCUSSION_SOURCE_STATUS_RESOLVED
            or discussion_source.discussion_entity is None
            or discussion_source.discussion_chat_id is None
        ):
            return (
                self.artifact_builder.build_not_available_thread(
                    channel_identity=channel_identity,
                    post=post,
                    discussion_source=discussion_source,
                ),
                (),
            )
        if not self.artifact_builder.post_has_discussion_comments(post):
            return (
                self.artifact_builder.build_no_comments_thread(
                    channel_identity=channel_identity,
                    post=post,
                    discussion_source=discussion_source,
                ),
                (),
            )

        fetch_result = await self.fetcher.fetch_comments_for_post(
            channel_entity=channel_entity,
            discussion_entity=discussion_source.discussion_entity,
            channel_post_record=post,
            max_comments_per_post=max_comments_per_post,
        )
        if fetch_result.error is not None:
            return (
                self.artifact_builder.build_failed_thread(
                    channel_identity=channel_identity,
                    post=post,
                    discussion_source=discussion_source,
                    error=fetch_result.error,
                ),
                (),
            )

        discussion_root_message_id = self.artifact_builder.discussion_root_message_id(
            post,
            fetch_result.comments,
        )
        comments = tuple(
            self.mapper.map_comment(
                comment,
                channel_post_record=post,
                discussion_chat_id=discussion_source.discussion_chat_id,
                discussion_root_message_id=discussion_root_message_id,
            )
            for comment in fetch_result.comments
        )
        return (
            self.artifact_builder.build_fetched_thread(
                channel_identity=channel_identity,
                post=post,
                discussion_source=discussion_source,
                discussion_root_message_id=discussion_root_message_id,
                exported_comments_count=len(comments),
                has_more=fetch_result.has_more,
            ),
            comments,
        )
