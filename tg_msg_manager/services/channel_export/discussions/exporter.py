from typing import Any, Iterable, Optional

from .fetcher import ChannelDiscussionFetcher
from .jsonl_renderer import ChannelDiscussionJsonlRenderer
from .mapper import ChannelDiscussionMapper
from .models import (
    DISCUSSION_SOURCE_STATUS_RESOLVED,
    DISCUSSION_THREAD_STATUS_EXPORTED,
    DISCUSSION_THREAD_STATUS_FAILED,
    DISCUSSION_THREAD_STATUS_NO_COMMENTS,
    DISCUSSION_THREAD_STATUS_NOT_AVAILABLE,
    DISCUSSION_THREAD_STATUS_NOT_LINKED,
    DISCUSSION_THREAD_STATUS_PARTIAL,
    ChannelDiscussionExportResult,
    ChannelDiscussionExportState,
    ChannelDiscussionMetadataRecord,
    ChannelDiscussionOptions,
    ChannelDiscussionSource,
    ChannelDiscussionThreadRecord,
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
                record = self._metadata_record(
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
                self._thread_record(
                    channel_identity=channel_identity,
                    post=post,
                    discussion_source=discussion_source,
                    status=DISCUSSION_THREAD_STATUS_NOT_LINKED,
                ),
                (),
            )
        if (
            discussion_source.status != DISCUSSION_SOURCE_STATUS_RESOLVED
            or discussion_source.discussion_entity is None
            or discussion_source.discussion_chat_id is None
        ):
            return (
                self._thread_record(
                    channel_identity=channel_identity,
                    post=post,
                    discussion_source=discussion_source,
                    status=DISCUSSION_THREAD_STATUS_NOT_AVAILABLE,
                    error=discussion_source.error,
                ),
                (),
            )
        if not self._post_has_discussion_comments(post):
            return (
                self._thread_record(
                    channel_identity=channel_identity,
                    post=post,
                    discussion_source=discussion_source,
                    status=DISCUSSION_THREAD_STATUS_NO_COMMENTS,
                    comments_count=0,
                    exported_comments_count=0,
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
                self._thread_record(
                    channel_identity=channel_identity,
                    post=post,
                    discussion_source=discussion_source,
                    status=DISCUSSION_THREAD_STATUS_FAILED,
                    error=fetch_result.error,
                ),
                (),
            )

        discussion_root_message_id = self._discussion_root_message_id(
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
        comments_count = self._comments_count(
            post=post,
            exported_count=len(comments),
            has_more=fetch_result.has_more,
        )
        if not comments:
            status = DISCUSSION_THREAD_STATUS_NO_COMMENTS
        elif fetch_result.has_more or comments_count > len(comments):
            status = DISCUSSION_THREAD_STATUS_PARTIAL
        else:
            status = DISCUSSION_THREAD_STATUS_EXPORTED
        return (
            self._thread_record(
                channel_identity=channel_identity,
                post=post,
                discussion_source=discussion_source,
                status=status,
                discussion_root_message_id=discussion_root_message_id,
                comments_count=comments_count,
                exported_comments_count=len(comments),
            ),
            comments,
        )

    @staticmethod
    def _thread_record(
        *,
        channel_identity: Any,
        post: Any,
        discussion_source: ChannelDiscussionSource,
        status: str,
        discussion_root_message_id: Optional[int] = None,
        comments_count: int = 0,
        exported_comments_count: int = 0,
        error: Optional[str] = None,
    ) -> ChannelDiscussionThreadRecord:
        return ChannelDiscussionThreadRecord(
            channel_id=channel_identity.channel_id,
            channel_username=channel_identity.username,
            channel_message_id=post.message_id,
            discussion_chat_id=discussion_source.discussion_chat_id,
            discussion_root_message_id=discussion_root_message_id,
            comments_count=comments_count,
            exported_comments_count=exported_comments_count,
            status=status,
            error=error,
        )

    @classmethod
    def _metadata_record(
        cls,
        *,
        channel_identity: Any,
        post: Any,
    ) -> ChannelDiscussionMetadataRecord:
        raw_payload = getattr(post, "raw_payload", None)
        replies = raw_payload.get("replies") if isinstance(raw_payload, dict) else None
        source = "raw_payload.replies" if isinstance(replies, dict) else None
        has_comments = (
            bool(replies.get("comments")) if isinstance(replies, dict) else False
        )
        discussion_chat_id = (
            cls._safe_optional_int(replies.get("channel_id"))
            if isinstance(replies, dict)
            else None
        )
        replies_count = cls._safe_optional_int(getattr(post, "replies_count", None))
        if replies_count is None and isinstance(replies, dict):
            replies_count = cls._safe_optional_int(replies.get("replies"))
        return ChannelDiscussionMetadataRecord(
            channel_id=channel_identity.channel_id,
            channel_message_id=post.message_id,
            has_comments=has_comments,
            discussion_chat_id=discussion_chat_id,
            replies_count=replies_count,
            comments_exported=False,
            source=source,
        )

    @staticmethod
    def _safe_optional_int(value: Any) -> Optional[int]:
        if value is None or isinstance(value, bool):
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @classmethod
    def _post_has_discussion_comments(cls, post: Any) -> bool:
        replies_count = cls._safe_optional_int(getattr(post, "replies_count", None))
        if replies_count is not None:
            return replies_count > 0
        raw_payload = getattr(post, "raw_payload", None)
        if not isinstance(raw_payload, dict) or "replies" not in raw_payload:
            return True
        replies = raw_payload.get("replies")
        if not isinstance(replies, dict) or replies.get("comments") is not True:
            return False
        nested_replies = cls._safe_optional_int(replies.get("replies"))
        return nested_replies is None or nested_replies > 0

    @staticmethod
    def _discussion_root_message_id(
        post: Any, comments: Iterable[Any]
    ) -> Optional[int]:
        raw_payload = getattr(post, "raw_payload", {}) or {}
        for key in ("discussion_root_message_id", "discussion_root_id"):
            value = raw_payload.get(key) if isinstance(raw_payload, dict) else None
            if value is not None:
                return int(value)
        for comment in comments:
            reply_to_id = getattr(comment, "reply_to_id", None)
            if reply_to_id is not None:
                return int(reply_to_id)
            reply_to = getattr(comment, "reply_to", None)
            value = getattr(reply_to, "reply_to_msg_id", None)
            if value is not None:
                return int(value)
        return None

    @staticmethod
    def _comments_count(*, post: Any, exported_count: int, has_more: bool) -> int:
        replies_count = getattr(post, "replies_count", None)
        if replies_count is not None:
            return int(replies_count)
        if has_more:
            return exported_count + 1
        return exported_count
