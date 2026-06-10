from typing import Any, Iterable, Optional

from .models import (
    DISCUSSION_THREAD_STATUS_EXPORTED,
    DISCUSSION_THREAD_STATUS_FAILED,
    DISCUSSION_THREAD_STATUS_NO_COMMENTS,
    DISCUSSION_THREAD_STATUS_NOT_AVAILABLE,
    DISCUSSION_THREAD_STATUS_NOT_LINKED,
    DISCUSSION_THREAD_STATUS_PARTIAL,
    ChannelDiscussionMetadataRecord,
    ChannelDiscussionSource,
    ChannelDiscussionThreadRecord,
)


class ChannelDiscussionArtifactBuilder:
    def build_not_linked_thread(
        self,
        *,
        channel_identity: Any,
        post: Any,
        discussion_source: ChannelDiscussionSource,
    ) -> ChannelDiscussionThreadRecord:
        return self.build_thread_record(
            channel_identity=channel_identity,
            post=post,
            discussion_source=discussion_source,
            status=DISCUSSION_THREAD_STATUS_NOT_LINKED,
        )

    def build_not_available_thread(
        self,
        *,
        channel_identity: Any,
        post: Any,
        discussion_source: ChannelDiscussionSource,
    ) -> ChannelDiscussionThreadRecord:
        return self.build_thread_record(
            channel_identity=channel_identity,
            post=post,
            discussion_source=discussion_source,
            status=DISCUSSION_THREAD_STATUS_NOT_AVAILABLE,
            error=discussion_source.error,
        )

    def build_no_comments_thread(
        self,
        *,
        channel_identity: Any,
        post: Any,
        discussion_source: ChannelDiscussionSource,
        comments_count: int = 0,
    ) -> ChannelDiscussionThreadRecord:
        return self.build_thread_record(
            channel_identity=channel_identity,
            post=post,
            discussion_source=discussion_source,
            status=DISCUSSION_THREAD_STATUS_NO_COMMENTS,
            comments_count=comments_count,
            exported_comments_count=0,
        )

    def build_failed_thread(
        self,
        *,
        channel_identity: Any,
        post: Any,
        discussion_source: ChannelDiscussionSource,
        error: str,
    ) -> ChannelDiscussionThreadRecord:
        return self.build_thread_record(
            channel_identity=channel_identity,
            post=post,
            discussion_source=discussion_source,
            status=DISCUSSION_THREAD_STATUS_FAILED,
            error=error,
        )

    def build_fetched_thread(
        self,
        *,
        channel_identity: Any,
        post: Any,
        discussion_source: ChannelDiscussionSource,
        discussion_root_message_id: Optional[int],
        exported_comments_count: int,
        has_more: bool,
    ) -> ChannelDiscussionThreadRecord:
        comments_count = self.comments_count(
            post=post,
            exported_count=exported_comments_count,
            has_more=has_more,
        )
        return self.build_thread_record(
            channel_identity=channel_identity,
            post=post,
            discussion_source=discussion_source,
            status=self.thread_status(
                comments_count=comments_count,
                exported_comments_count=exported_comments_count,
                has_more=has_more,
            ),
            discussion_root_message_id=discussion_root_message_id,
            comments_count=comments_count,
            exported_comments_count=exported_comments_count,
        )

    @staticmethod
    def build_thread_record(
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
    def build_metadata_record(
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
            cls.safe_optional_int(replies.get("channel_id"))
            if isinstance(replies, dict)
            else None
        )
        replies_count = cls.safe_optional_int(getattr(post, "replies_count", None))
        if replies_count is None and isinstance(replies, dict):
            replies_count = cls.safe_optional_int(replies.get("replies"))
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
    def safe_optional_int(value: Any) -> Optional[int]:
        if value is None or isinstance(value, bool):
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @classmethod
    def post_has_discussion_comments(cls, post: Any) -> bool:
        replies_count = cls.safe_optional_int(getattr(post, "replies_count", None))
        if replies_count is not None:
            return replies_count > 0
        raw_payload = getattr(post, "raw_payload", None)
        if not isinstance(raw_payload, dict) or "replies" not in raw_payload:
            return True
        replies = raw_payload.get("replies")
        if not isinstance(replies, dict) or replies.get("comments") is not True:
            return False
        nested_replies = cls.safe_optional_int(replies.get("replies"))
        return nested_replies is None or nested_replies > 0

    @staticmethod
    def discussion_root_message_id(post: Any, comments: Iterable[Any]) -> Optional[int]:
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
    def comments_count(*, post: Any, exported_count: int, has_more: bool) -> int:
        replies_count = getattr(post, "replies_count", None)
        if replies_count is not None:
            return int(replies_count)
        if has_more:
            return exported_count + 1
        return exported_count

    @staticmethod
    def thread_status(
        *,
        comments_count: int,
        exported_comments_count: int,
        has_more: bool,
    ) -> str:
        if exported_comments_count == 0:
            return DISCUSSION_THREAD_STATUS_NO_COMMENTS
        if has_more or comments_count > exported_comments_count:
            return DISCUSSION_THREAD_STATUS_PARTIAL
        return DISCUSSION_THREAD_STATUS_EXPORTED
