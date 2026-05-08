import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from .atomic_writer import atomic_write_text
from .errors import ChannelExportStateError
from .models import (
    CHANNEL_EXPORT_RUN_MODE_FORCE_FULL,
    CHANNEL_EXPORT_RUN_MODE_FULL,
    CHANNEL_EXPORT_RUN_MODE_INCREMENTAL,
    ChannelExportRunStats,
    ChannelExportState,
    ChannelIdentity,
)
from .state_consistency import validate_channel_state_integrity


def _parse_iso_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ChannelExportStateError(
            f"Invalid datetime in channel export state: {value!r}"
        ) from exc
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _isoformat_or_none(value: Optional[datetime]) -> Optional[str]:
    return value.isoformat() if value is not None else None


class ChannelExportStateManager:
    schema_version = "1.0"

    def state_exists(self, path: Path) -> bool:
        return Path(path).exists()

    def load(self, path: Path) -> Optional[ChannelExportState]:
        target_path = Path(path)
        if not target_path.exists():
            return None

        try:
            payload = json.loads(target_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ChannelExportStateError(
                f"Channel export state is corrupted: {target_path}"
            ) from exc

        if not isinstance(payload, dict):
            raise ChannelExportStateError(
                f"Channel export state must be a JSON object: {target_path}"
            )

        try:
            state = ChannelExportState(
                schema_version=str(
                    payload.get("schema_version") or self.schema_version
                ),
                channel_id=int(payload["channel_id"]),
                channel_username=payload.get("channel_username"),
                channel_title=payload.get("channel_title"),
                last_exported_message_id=(
                    int(payload["last_exported_message_id"])
                    if payload.get("last_exported_message_id") is not None
                    else None
                ),
                last_exported_at=_parse_iso_datetime(payload.get("last_exported_at")),
                message_count_total=int(payload.get("message_count_total", 0) or 0),
                media_count_total=int(payload.get("media_count_total", 0) or 0),
                downloaded_media_count_total=int(
                    payload.get("downloaded_media_count_total", 0) or 0
                ),
                already_existing_media_count_total=int(
                    payload.get("already_existing_media_count_total", 0) or 0
                ),
                skipped_media_count_total=int(
                    payload.get("skipped_media_count_total", 0) or 0
                ),
                skipped_by_size_count_total=int(
                    payload.get("skipped_by_size_count_total", 0) or 0
                ),
                skipped_by_type_count_total=int(
                    payload.get("skipped_by_type_count_total", 0) or 0
                ),
                failed_media_count_total=int(
                    payload.get("failed_media_count_total", 0) or 0
                ),
                last_run_status=str(payload.get("last_run_status") or "completed"),
                updated_at=_parse_iso_datetime(payload.get("updated_at"))
                or datetime.now(timezone.utc),
                date_from=_parse_iso_datetime(payload.get("date_from")),
                date_to=_parse_iso_datetime(payload.get("date_to")),
                last_manifest_path=payload.get("last_manifest_path"),
            )
        except KeyError as exc:
            raise ChannelExportStateError(
                f"Channel export state is missing required field {exc.args[0]!r}: {target_path}"
            ) from exc
        except (TypeError, ValueError) as exc:
            raise ChannelExportStateError(
                f"Channel export state has invalid values: {target_path}"
            ) from exc
        validate_channel_state_integrity(state)
        return state

    def save(self, path: Path, state: ChannelExportState) -> None:
        validate_channel_state_integrity(state)
        target_path = Path(path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        content = json.dumps(self.to_dict(state), ensure_ascii=False, indent=2) + "\n"
        atomic_write_text(target_path, content, encoding="utf-8")

    def to_dict(self, state: ChannelExportState) -> Dict[str, Any]:
        return {
            "schema_version": state.schema_version,
            "channel_id": state.channel_id,
            "channel_username": state.channel_username,
            "channel_title": state.channel_title,
            "last_exported_message_id": state.last_exported_message_id,
            "last_exported_at": _isoformat_or_none(state.last_exported_at),
            "message_count_total": state.message_count_total,
            "media_count_total": state.media_count_total,
            "downloaded_media_count_total": state.downloaded_media_count_total,
            "already_existing_media_count_total": state.already_existing_media_count_total,
            "skipped_media_count_total": state.skipped_media_count_total,
            "skipped_by_size_count_total": state.skipped_by_size_count_total,
            "skipped_by_type_count_total": state.skipped_by_type_count_total,
            "failed_media_count_total": state.failed_media_count_total,
            "last_run_status": state.last_run_status,
            "updated_at": _isoformat_or_none(state.updated_at),
            "date_from": _isoformat_or_none(state.date_from),
            "date_to": _isoformat_or_none(state.date_to),
            "last_manifest_path": state.last_manifest_path,
        }

    def determine_run_mode(
        self, state: Optional[ChannelExportState], *, force: bool
    ) -> str:
        if force:
            return CHANNEL_EXPORT_RUN_MODE_FORCE_FULL
        if state is None or state.last_exported_message_id is None:
            return CHANNEL_EXPORT_RUN_MODE_FULL
        return CHANNEL_EXPORT_RUN_MODE_INCREMENTAL

    def validate_state_for_channel(
        self, state: ChannelExportState, channel: ChannelIdentity
    ) -> None:
        if state.channel_id != channel.channel_id:
            raise ChannelExportStateError(
                "Channel export state belongs to a different channel: "
                f"expected {channel.channel_id}, got {state.channel_id}"
            )

    def build_completed_state(
        self,
        *,
        channel: ChannelIdentity,
        stats: ChannelExportRunStats,
        manifest_path: Path,
        previous_state: Optional[ChannelExportState] = None,
    ) -> ChannelExportState:
        now = datetime.now(timezone.utc)

        if (
            stats.mode == CHANNEL_EXPORT_RUN_MODE_INCREMENTAL
            and previous_state is not None
        ):
            message_count_total = (
                previous_state.message_count_total + stats.posts_exported
            )
            media_count_total = (
                previous_state.media_count_total + stats.media_records_added
            )
            downloaded_media_count_total = (
                previous_state.downloaded_media_count_total
                + stats.downloaded_media_count
            )
            already_existing_media_count_total = (
                previous_state.already_existing_media_count_total
                + stats.already_existing_media_count
            )
            skipped_media_count_total = (
                previous_state.skipped_media_count_total + stats.skipped_media_count
            )
            skipped_by_size_count_total = (
                previous_state.skipped_by_size_count_total + stats.skipped_by_size_count
            )
            skipped_by_type_count_total = (
                previous_state.skipped_by_type_count_total + stats.skipped_by_type_count
            )
            failed_media_count_total = (
                previous_state.failed_media_count_total + stats.failed_media_count
            )
            date_from = self._merge_date_from(previous_state.date_from, stats.date_from)
            date_to = self._merge_date_to(previous_state.date_to, stats.date_to)
            last_exported_message_id = (
                stats.last_exported_message_id
                if stats.last_exported_message_id is not None
                else previous_state.last_exported_message_id
            )
        else:
            message_count_total = stats.posts_exported
            media_count_total = stats.media_records_added
            downloaded_media_count_total = stats.downloaded_media_count
            already_existing_media_count_total = stats.already_existing_media_count
            skipped_media_count_total = stats.skipped_media_count
            skipped_by_size_count_total = stats.skipped_by_size_count
            skipped_by_type_count_total = stats.skipped_by_type_count
            failed_media_count_total = stats.failed_media_count
            date_from = stats.date_from
            date_to = stats.date_to
            last_exported_message_id = stats.last_exported_message_id

        return ChannelExportState(
            schema_version=self.schema_version,
            channel_id=channel.channel_id,
            channel_username=channel.username,
            channel_title=channel.title,
            last_exported_message_id=last_exported_message_id,
            last_exported_at=now,
            message_count_total=message_count_total,
            media_count_total=media_count_total,
            downloaded_media_count_total=downloaded_media_count_total,
            already_existing_media_count_total=already_existing_media_count_total,
            skipped_media_count_total=skipped_media_count_total,
            skipped_by_size_count_total=skipped_by_size_count_total,
            skipped_by_type_count_total=skipped_by_type_count_total,
            failed_media_count_total=failed_media_count_total,
            last_run_status="completed",
            updated_at=now,
            date_from=date_from,
            date_to=date_to,
            last_manifest_path=Path(manifest_path).name,
        )

    @staticmethod
    def _merge_date_from(
        left: Optional[datetime], right: Optional[datetime]
    ) -> Optional[datetime]:
        if left is None:
            return right
        if right is None:
            return left
        return left if left <= right else right

    @staticmethod
    def _merge_date_to(
        left: Optional[datetime], right: Optional[datetime]
    ) -> Optional[datetime]:
        if left is None:
            return right
        if right is None:
            return left
        return left if left >= right else right
