from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


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
    media_dir: Path


@dataclass(frozen=True)
class ChannelExportResult:
    channel: ChannelIdentity
    message_count: int
    media_count: int
    downloaded_media_count: int
    skipped_media_count: int
    manifest_path: Path
    messages_jsonl_path: Path
    messages_txt_path: Path
    media_manifest_path: Path
