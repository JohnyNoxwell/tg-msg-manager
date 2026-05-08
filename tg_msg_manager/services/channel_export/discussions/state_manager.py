import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from ..atomic_writer import atomic_write_text
from .errors import ChannelDiscussionStateError
from .models import ChannelDiscussionExportState, ChannelDiscussionRunStats
from ..state_consistency import validate_discussion_state_integrity


def _parse_iso_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ChannelDiscussionStateError(
            f"Invalid datetime in discussion export state: {value!r}"
        ) from exc
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _isoformat_or_none(value: Optional[datetime]) -> Optional[str]:
    return value.isoformat() if value is not None else None


class ChannelDiscussionStateManager:
    schema_version = "1.0"

    def load(self, path: Path) -> Optional[ChannelDiscussionExportState]:
        target_path = Path(path)
        if not target_path.exists():
            return None
        try:
            payload = json.loads(target_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ChannelDiscussionStateError(
                f"Discussion export state is corrupted: {target_path}"
            ) from exc
        if not isinstance(payload, dict):
            raise ChannelDiscussionStateError(
                f"Discussion export state must be a JSON object: {target_path}"
            )
        try:
            state = ChannelDiscussionExportState(
                schema_version=str(
                    payload.get("schema_version") or self.schema_version
                ),
                channel_id=int(payload["channel_id"]),
                discussion_chat_id=(
                    int(payload["discussion_chat_id"])
                    if payload.get("discussion_chat_id") is not None
                    else None
                ),
                last_run_at=_parse_iso_datetime(payload.get("last_run_at")),
                thread_count_total=int(payload.get("thread_count_total", 0) or 0),
                comment_count_total=int(payload.get("comment_count_total", 0) or 0),
                failed_thread_count_total=int(
                    payload.get("failed_thread_count_total", 0) or 0
                ),
                last_run_status=str(payload.get("last_run_status") or "completed"),
                updated_at=_parse_iso_datetime(payload.get("updated_at"))
                or datetime.now(timezone.utc),
            )
        except KeyError as exc:
            raise ChannelDiscussionStateError(
                f"Discussion export state is missing required field {exc.args[0]!r}: {target_path}"
            ) from exc
        except (TypeError, ValueError) as exc:
            raise ChannelDiscussionStateError(
                f"Discussion export state has invalid values: {target_path}"
            ) from exc
        validate_discussion_state_integrity(state)
        return state

    def save(self, path: Path, state: ChannelDiscussionExportState) -> None:
        validate_discussion_state_integrity(state)
        target_path = Path(path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        content = json.dumps(self.to_dict(state), ensure_ascii=False, indent=2) + "\n"
        atomic_write_text(target_path, content, encoding="utf-8")

    def to_dict(self, state: ChannelDiscussionExportState) -> Dict[str, Any]:
        return {
            "schema_version": state.schema_version,
            "channel_id": state.channel_id,
            "discussion_chat_id": state.discussion_chat_id,
            "last_run_at": _isoformat_or_none(state.last_run_at),
            "thread_count_total": state.thread_count_total,
            "comment_count_total": state.comment_count_total,
            "failed_thread_count_total": state.failed_thread_count_total,
            "last_run_status": state.last_run_status,
            "updated_at": _isoformat_or_none(state.updated_at),
        }

    def build_completed_state(
        self,
        *,
        channel: Any,
        discussion_chat_id: Optional[int],
        stats: ChannelDiscussionRunStats,
        previous_state: Optional[ChannelDiscussionExportState] = None,
    ) -> ChannelDiscussionExportState:
        now = datetime.now(timezone.utc)
        if stats.mode == "incremental" and previous_state is not None:
            thread_count_total = previous_state.thread_count_total + stats.thread_count
            comment_count_total = (
                previous_state.comment_count_total + stats.comment_count
            )
            failed_thread_count_total = (
                previous_state.failed_thread_count_total + stats.failed_thread_count
            )
        else:
            thread_count_total = stats.thread_count
            comment_count_total = stats.comment_count
            failed_thread_count_total = stats.failed_thread_count

        return ChannelDiscussionExportState(
            schema_version=self.schema_version,
            channel_id=channel.channel_id,
            discussion_chat_id=discussion_chat_id,
            last_run_at=now,
            thread_count_total=thread_count_total,
            comment_count_total=comment_count_total,
            failed_thread_count_total=failed_thread_count_total,
            last_run_status="completed",
            updated_at=now,
        )
