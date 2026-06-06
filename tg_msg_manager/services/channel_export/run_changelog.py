import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from tg_msg_manager.core.models.dataset_contracts import RUN_CHANGELOG_JSONL

from .atomic_writer import AtomicTextFile


def run_changelog_path(output_dir: Path) -> Path:
    return Path(output_dir) / RUN_CHANGELOG_JSONL


class ChannelRunChangelogWriter:
    def append_entry(
        self,
        *,
        output_dir: Path,
        channel: Any,
        run_mode: str,
        previous_state: Any,
        new_state: Any,
        run_stats: Any,
        posts: tuple[Any, ...],
        artifact_paths: dict[str, str],
        summary: Any = None,
        warnings: tuple[str, ...] = (),
    ) -> Path:
        path = run_changelog_path(output_dir)
        now = datetime.now(timezone.utc).isoformat()
        entry = {
            "run_id": uuid.uuid4().hex,
            "export_target_type": "channel",
            "export_target_id": getattr(channel, "channel_id", None),
            "export_target_name": _target_name(channel),
            "run_mode": run_mode,
            "started_at": now,
            "finished_at": now,
            "previous_cursor": _state_cursor(previous_state),
            "new_cursor": _state_cursor(new_state),
            "new_message_count": getattr(run_stats, "posts_exported", 0),
            "new_message_ids": _message_ids(posts, summary),
            "first_new_message_id": _first_message_id(posts, summary),
            "last_new_message_id": _last_message_id(posts, summary),
            "first_new_message_date": _first_message_date(posts, summary),
            "last_new_message_date": _last_message_date(posts, summary),
            "artifact_paths": artifact_paths,
            "warnings": list(warnings),
        }
        writer = AtomicTextFile(path, mode="a", encoding="utf-8")
        try:
            handle = writer.open()
            handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
            writer.commit()
        except Exception:
            writer.rollback()
            raise
        return path


def _target_name(channel: Any) -> Optional[str]:
    username = getattr(channel, "username", None)
    if username:
        return username
    return getattr(channel, "title", None)


def _state_cursor(state: Any) -> Optional[int]:
    if state is None:
        return None
    return getattr(state, "last_exported_message_id", None)


def _first_post_attr(posts: tuple[Any, ...], attr: str) -> Any:
    if not posts:
        return None
    return getattr(posts[0], attr)


def _last_post_attr(posts: tuple[Any, ...], attr: str) -> Any:
    if not posts:
        return None
    return getattr(posts[-1], attr)


def _message_ids(posts: tuple[Any, ...], summary: Any) -> list[int]:
    if summary is not None:
        return list(summary.message_ids)
    return [post.message_id for post in posts]


def _first_message_id(posts: tuple[Any, ...], summary: Any) -> Any:
    if summary is not None:
        return summary.first_message_id
    return _first_post_attr(posts, "message_id")


def _last_message_id(posts: tuple[Any, ...], summary: Any) -> Any:
    if summary is not None:
        return summary.last_message_id
    return _last_post_attr(posts, "message_id")


def _first_post_date(posts: tuple[Any, ...]) -> Optional[str]:
    if not posts:
        return None
    return posts[0].timestamp.isoformat()


def _last_post_date(posts: tuple[Any, ...]) -> Optional[str]:
    if not posts:
        return None
    return posts[-1].timestamp.isoformat()


def _first_message_date(posts: tuple[Any, ...], summary: Any) -> Optional[str]:
    if summary is not None:
        if summary.first_message_timestamp is None:
            return None
        return summary.first_message_timestamp.isoformat()
    return _first_post_date(posts)


def _last_message_date(posts: tuple[Any, ...], summary: Any) -> Optional[str]:
    if summary is not None:
        if summary.last_message_timestamp is None:
            return None
        return summary.last_message_timestamp.isoformat()
    return _last_post_date(posts)
