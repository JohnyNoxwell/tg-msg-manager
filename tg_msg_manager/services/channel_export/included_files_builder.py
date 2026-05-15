from typing import Any

from .discussions.manifest_summary import discussion_included_files
from .models import ChannelExportOptions


def build_included_files(
    options: ChannelExportOptions,
    discussion_result: Any = None,
) -> tuple[str, ...]:
    included = ["manifest.json", "media_manifest.jsonl", "run_changelog.jsonl"]
    if options.include_jsonl:
        included.append("messages.jsonl")
    if options.include_txt:
        included.append("messages.txt")
    if options.media_mode == "full":
        included.append("media/")
    included.extend(discussion_included_files(discussion_result))
    return tuple(included)
