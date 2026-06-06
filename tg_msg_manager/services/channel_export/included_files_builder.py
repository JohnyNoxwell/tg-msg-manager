from typing import Any

from tg_msg_manager.core.models.dataset_contracts import (
    MANIFEST_JSON,
    MEDIA_DIRECTORY_ENTRY,
    MEDIA_MANIFEST_JSONL,
    MESSAGES_JSONL,
    MESSAGES_TXT,
    RUN_CHANGELOG_JSONL,
)

from .discussions.manifest_summary import discussion_included_files
from .models import ChannelExportOptions


def build_included_files(
    options: ChannelExportOptions,
    discussion_result: Any = None,
) -> tuple[str, ...]:
    included = [MANIFEST_JSON, MEDIA_MANIFEST_JSONL, RUN_CHANGELOG_JSONL]
    if options.include_jsonl:
        included.append(MESSAGES_JSONL)
    if options.include_txt:
        included.append(MESSAGES_TXT)
    if options.media_mode == "full":
        included.append(MEDIA_DIRECTORY_ENTRY)
    included.extend(discussion_included_files(discussion_result))
    return tuple(included)
