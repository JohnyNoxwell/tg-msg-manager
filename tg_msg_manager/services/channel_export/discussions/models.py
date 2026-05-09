from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from .options import (
    DEFAULT_MAX_COMMENTS_PER_POST,
    DISCUSSION_MODE_NONE,
    validate_discussion_mode,
    validate_max_comments_per_post,
)

DISCUSSION_THREAD_STATUS_NOT_AVAILABLE = "not_available"
DISCUSSION_THREAD_STATUS_NOT_LINKED = "not_linked"
DISCUSSION_THREAD_STATUS_NO_COMMENTS = "no_comments"
DISCUSSION_THREAD_STATUS_EXPORTED = "exported"
DISCUSSION_THREAD_STATUS_PARTIAL = "partial"
DISCUSSION_THREAD_STATUS_FAILED = "failed"
ALLOWED_DISCUSSION_THREAD_STATUSES = frozenset(
    {
        DISCUSSION_THREAD_STATUS_NOT_AVAILABLE,
        DISCUSSION_THREAD_STATUS_NOT_LINKED,
        DISCUSSION_THREAD_STATUS_NO_COMMENTS,
        DISCUSSION_THREAD_STATUS_EXPORTED,
        DISCUSSION_THREAD_STATUS_PARTIAL,
        DISCUSSION_THREAD_STATUS_FAILED,
    }
)

DISCUSSION_SOURCE_STATUS_DISABLED = "disabled"
DISCUSSION_SOURCE_STATUS_NOT_AVAILABLE = "not_available"
DISCUSSION_SOURCE_STATUS_NOT_LINKED = "not_linked"
DISCUSSION_SOURCE_STATUS_RESOLVED = "resolved"
DISCUSSION_SOURCE_STATUS_FAILED = "failed"
ALLOWED_DISCUSSION_SOURCE_STATUSES = frozenset(
    {
        DISCUSSION_SOURCE_STATUS_DISABLED,
        DISCUSSION_SOURCE_STATUS_NOT_AVAILABLE,
        DISCUSSION_SOURCE_STATUS_NOT_LINKED,
        DISCUSSION_SOURCE_STATUS_RESOLVED,
        DISCUSSION_SOURCE_STATUS_FAILED,
    }
)


@dataclass(frozen=True)
class ChannelDiscussionOptions:
    mode: str = DISCUSSION_MODE_NONE
    max_comments_per_post: int = DEFAULT_MAX_COMMENTS_PER_POST

    def __post_init__(self) -> None:
        object.__setattr__(self, "mode", validate_discussion_mode(self.mode))
        object.__setattr__(
            self,
            "max_comments_per_post",
            validate_max_comments_per_post(self.max_comments_per_post),
        )


@dataclass(frozen=True)
class ChannelDiscussionSource:
    status: str
    discussion_chat_id: Optional[int]
    discussion_entity: Optional[Any]
    error: Optional[str] = None


@dataclass(frozen=True)
class ChannelDiscussionThreadRecord:
    channel_id: int
    channel_username: Optional[str]
    channel_message_id: int
    discussion_chat_id: Optional[int]
    discussion_root_message_id: Optional[int]
    comments_count: int
    exported_comments_count: int
    status: str
    error: Optional[str] = None


@dataclass(frozen=True)
class ChannelDiscussionMetadataRecord:
    channel_id: int
    channel_message_id: int
    has_comments: bool
    discussion_chat_id: Optional[int]
    replies_count: Optional[int]
    comments_exported: bool = False
    source: Optional[str] = None


@dataclass(frozen=True)
class ChannelDiscussionCommentRecord:
    message_id: int
    discussion_chat_id: int
    channel_id: int
    channel_message_id: int
    discussion_root_message_id: Optional[int]
    author_id: Optional[int]
    author_name: Optional[str]
    username: Optional[str]
    timestamp: datetime
    text: Optional[str]
    reply_to_id: Optional[int]
    media: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    reactions: Dict[str, Any] = field(default_factory=dict)
    raw_payload: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ChannelDiscussionExportState:
    schema_version: str
    channel_id: int
    discussion_chat_id: Optional[int]
    last_run_at: Optional[datetime]
    thread_count_total: int
    comment_count_total: int
    failed_thread_count_total: int
    last_run_status: str
    updated_at: datetime


@dataclass(frozen=True)
class ChannelDiscussionExportResult:
    mode: str
    discussion_chat_id: Optional[int]
    thread_count: int
    comment_count: int
    failed_thread_count: int
    comments_jsonl_path: Optional[Path]
    comments_txt_path: Optional[Path]
    threads_jsonl_path: Optional[Path]
    state_path: Optional[Path]
    metadata_count: int = 0
    metadata_jsonl_path: Optional[Path] = None
    state: Optional[ChannelDiscussionExportState] = None


@dataclass(frozen=True)
class ChannelDiscussionFetchResult:
    comments: Tuple[Any, ...]
    has_more: bool = False
    error: Optional[str] = None


@dataclass(frozen=True)
class ChannelDiscussionRunStats:
    mode: str
    thread_count: int = 0
    comment_count: int = 0
    failed_thread_count: int = 0
    partial_thread_count: int = 0
    not_linked_thread_count: int = 0
    not_available_thread_count: int = 0
    no_comments_thread_count: int = 0
