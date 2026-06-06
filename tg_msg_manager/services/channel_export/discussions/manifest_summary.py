from typing import Any

from tg_msg_manager.core.models.dataset_contracts import (
    DISCUSSION_FULL_DATASET_FILES,
    DISCUSSION_METADATA_DATASET_FILES,
)

from .options import DISCUSSION_MODE_FULL, DISCUSSION_MODE_METADATA

DISCUSSION_DATASET_FILES = DISCUSSION_FULL_DATASET_FILES


def discussion_included_files(discussion_result: Any = None) -> tuple[str, ...]:
    if discussion_result is None:
        return ()
    if getattr(discussion_result, "mode", None) == DISCUSSION_MODE_METADATA:
        return DISCUSSION_METADATA_DATASET_FILES
    return DISCUSSION_DATASET_FILES


def build_discussion_manifest(
    *,
    discussion_mode: str,
    max_comments_per_post: int,
    discussion_result: Any = None,
) -> dict[str, Any]:
    if discussion_mode == DISCUSSION_MODE_METADATA:
        if discussion_result is None:
            return {
                "mode": discussion_mode,
                "metadata_count": 0,
                "comment_count": 0,
                "comments_exported": False,
                "included_files": [],
            }
        return {
            "mode": discussion_mode,
            "discussion_chat_id": discussion_result.discussion_chat_id,
            "metadata_count": discussion_result.metadata_count,
            "comment_count": 0,
            "comments_exported": False,
            "included_files": list(DISCUSSION_METADATA_DATASET_FILES),
        }
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
