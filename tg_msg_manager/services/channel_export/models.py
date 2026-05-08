from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from .discussions.options import (
    DEFAULT_MAX_COMMENTS_PER_POST,
    DISCUSSION_MODE_NONE,
)

CHANNEL_EXPORT_RUN_MODE_FULL = "full"
CHANNEL_EXPORT_RUN_MODE_INCREMENTAL = "incremental"
CHANNEL_EXPORT_RUN_MODE_FORCE_FULL = "force_full"


@dataclass(frozen=True)
class ChannelIdentity:
    channel_id: int
    title: Optional[str]
    username: Optional[str]
    access_hash: Optional[int] = None


@dataclass(frozen=True)
class ChannelExportOptions:
    channel: str
    limit: Optional[int]
    media_mode: str
    output_dir: Path
    max_media_size: Optional[int] = None
    media_types: Optional[Tuple[str, ...]] = None
    discussion_mode: str = DISCUSSION_MODE_NONE
    max_comments_per_post: int = DEFAULT_MAX_COMMENTS_PER_POST
    include_jsonl: bool = True
    include_txt: bool = True
    force: bool = False


@dataclass(frozen=True)
class ChannelMediaRecord:
    media_id: str
    message_id: int
    media_index: int
    media_type: Optional[str]
    mime_type: Optional[str]
    file_name: Optional[str]
    file_size: Optional[int]
    width: Optional[int]
    height: Optional[int]
    duration: Optional[float]
    local_path: Optional[str]
    sha256: Optional[str]
    download_status: str
    error: Optional[str] = None
    original_filename: Optional[str] = None
    detected_extension: Optional[str] = None
    filename_strategy: Optional[str] = None
    final_filename: Optional[str] = None
    final_path: Optional[str] = None


@dataclass(frozen=True)
class ChannelPostRecord:
    message_id: int
    channel_id: int
    channel_title: Optional[str]
    channel_username: Optional[str]
    timestamp: datetime
    text: Optional[str]
    views: Optional[int]
    forwards: Optional[int]
    replies_count: Optional[int]
    reactions: Dict[str, Any]
    media: Tuple[ChannelMediaRecord, ...]
    raw_payload: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ChannelExportPlan:
    output_dir: Path
    manifest_path: Path
    messages_jsonl_path: Path
    messages_txt_path: Path
    media_manifest_path: Path
    state_path: Path
    media_dir: Path
    discussion_comments_jsonl_path: Path
    discussion_comments_txt_path: Path
    discussion_threads_jsonl_path: Path
    discussion_state_path: Path


@dataclass(frozen=True)
class ChannelExportState:
    schema_version: str
    channel_id: int
    channel_username: Optional[str]
    channel_title: Optional[str]
    last_exported_message_id: Optional[int]
    last_exported_at: Optional[datetime]
    message_count_total: int
    media_count_total: int
    downloaded_media_count_total: int
    already_existing_media_count_total: int
    skipped_media_count_total: int
    skipped_by_size_count_total: int
    skipped_by_type_count_total: int
    failed_media_count_total: int
    last_run_status: str
    updated_at: datetime
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    last_manifest_path: Optional[str] = None


@dataclass(frozen=True)
class ChannelExportRunStats:
    mode: str
    posts_exported: int
    media_records_added: int
    downloaded_media_count: int
    already_existing_media_count: int
    skipped_media_count: int
    skipped_by_size_count: int
    skipped_by_type_count: int
    failed_media_count: int
    date_from: Optional[datetime]
    date_to: Optional[datetime]
    last_exported_message_id: Optional[int]


@dataclass(frozen=True)
class ChannelExportResult:
    channel: ChannelIdentity
    run_mode: str
    media_mode: str
    max_media_size: Optional[int]
    media_types: Optional[Tuple[str, ...]]
    message_count: int
    media_count: int
    posts_exported_this_run: int
    media_records_added_this_run: int
    downloaded_media_count_this_run: int
    already_existing_media_count_this_run: int
    skipped_by_size_count_this_run: int
    skipped_by_type_count_this_run: int
    failed_media_count_this_run: int
    downloaded_media_count: int
    already_existing_media_count: int
    skipped_media_count: int
    skipped_by_size_count: int
    skipped_by_type_count: int
    failed_media_count: int
    manifest_path: Path
    messages_jsonl_path: Path
    messages_txt_path: Path
    media_manifest_path: Path
    state_path: Path
    discussion_mode: str = DISCUSSION_MODE_NONE
    discussion_chat_id: Optional[int] = None
    discussion_thread_count_this_run: int = 0
    discussion_comment_count_this_run: int = 0
    failed_discussion_thread_count_this_run: int = 0
    discussion_comments_jsonl_path: Optional[Path] = None
    discussion_comments_txt_path: Optional[Path] = None
    discussion_threads_jsonl_path: Optional[Path] = None
    discussion_state_path: Optional[Path] = None
