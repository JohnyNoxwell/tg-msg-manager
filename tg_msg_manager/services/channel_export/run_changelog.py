import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .atomic_writer import AtomicTextFile

RUN_CHANGELOG_JSONL = "run_changelog.jsonl"


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
            "new_message_ids": [post.message_id for post in posts],
            "first_new_message_id": _first_post_attr(posts, "message_id"),
            "last_new_message_id": _last_post_attr(posts, "message_id"),
            "first_new_message_date": _first_post_date(posts),
            "last_new_message_date": _last_post_date(posts),
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


def _first_post_date(posts: tuple[Any, ...]) -> Optional[str]:
    if not posts:
        return None
    return posts[0].timestamp.isoformat()


def _last_post_date(posts: tuple[Any, ...]) -> Optional[str]:
    if not posts:
        return None
    return posts[-1].timestamp.isoformat()
