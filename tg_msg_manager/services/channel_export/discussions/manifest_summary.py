from typing import Any

from .options import DISCUSSION_MODE_FULL

DISCUSSION_DATASET_FILES = (
    "discussion_comments.jsonl",
    "discussion_comments.txt",
    "discussion_threads.jsonl",
    "discussion_export_state.json",
)


def discussion_included_files(discussion_result: Any = None) -> tuple[str, ...]:
    if discussion_result is None:
        return ()
    return DISCUSSION_DATASET_FILES


def build_discussion_manifest(
    *,
    discussion_mode: str,
    max_comments_per_post: int,
    discussion_result: Any = None,
) -> dict[str, Any]:
    if discussion_mode != DISCUSSION_MODE_FULL:
        return {"mode": discussion_mode}
    if discussion_result is None:
        return {
            "mode": discussion_mode,
            "discussion_chat_id": None,
            "thread_count": 0,
            "comment_count": 0,
            "failed_thread_count": 0,
            "max_comments_per_post": max_comments_per_post,
            "included_files": [],
        }
    return {
        "mode": discussion_mode,
        "discussion_chat_id": discussion_result.discussion_chat_id,
        "thread_count": discussion_result.thread_count,
        "comment_count": discussion_result.comment_count,
        "failed_thread_count": discussion_result.failed_thread_count,
        "max_comments_per_post": max_comments_per_post,
        "included_files": list(DISCUSSION_DATASET_FILES),
    }
