import json
from pathlib import Path
from typing import Any

from tg_msg_manager.core.models.dataset_contracts import (
    CHANNEL_STATE_JSON,
    DIRECT_CHANNEL_EXPORT_DATASET_TYPE,
    MANIFEST_JSON,
    MESSAGES_JSONL,
    MESSAGES_TXT,
)

from .discussions.options import (
    DEFAULT_MAX_COMMENTS_PER_POST,
    DISCUSSION_MODE_FULL,
    validate_discussion_mode,
    validate_max_comments_per_post,
)
from .media_policy import validate_media_mode
from .media_types import parse_media_types
from .models import ChannelExportOptions
from .state_manager import ChannelExportStateManager


class ChannelBatchOptionsBuilder:
    def __init__(self, state_manager: ChannelExportStateManager | None = None):
        self.state_manager = state_manager or ChannelExportStateManager()

    def build(self, dataset_dir: Path, *, root: Path) -> ChannelExportOptions:
        dataset_dir = Path(dataset_dir)
        state_path = dataset_dir / CHANNEL_STATE_JSON
        manifest_path = dataset_dir / MANIFEST_JSON
        if not state_path.is_file() or not manifest_path.is_file():
            raise ValueError(
                f"Dataset requires {CHANNEL_STATE_JSON} and {MANIFEST_JSON}"
            )

        state = self.state_manager.load(state_path)
        if state is None:
            raise ValueError(f"Channel export state is missing: {state_path}")
        manifest = self._load_manifest(manifest_path)
        source = self._mapping(manifest, "source")
        export = self._mapping(manifest, "export")
        discussion = self._mapping(manifest, "discussion")

        if manifest.get("dataset_type") != DIRECT_CHANNEL_EXPORT_DATASET_TYPE:
            raise ValueError("Manifest dataset_type is not direct_channel_export")
        if manifest.get("status") != "completed":
            raise ValueError("Manifest status is not completed")
        if (
            source.get("type") != "channel"
            or self._integer(source, "id") != state.channel_id
        ):
            raise ValueError("Manifest source does not match channel export state")
        if state.last_run_status != "completed":
            raise ValueError("Channel export state status is not completed")

        media_mode = validate_media_mode(self._text(export, "media_mode"))
        max_media_size = self._optional_non_negative_integer(export, "max_media_size")
        media_types = self._media_types(export.get("media_types"))
        discussion_mode = validate_discussion_mode(self._text(discussion, "mode"))
        max_comments = DEFAULT_MAX_COMMENTS_PER_POST
        if discussion_mode == DISCUSSION_MODE_FULL:
            max_comments = validate_max_comments_per_post(
                self._integer(discussion, "max_comments_per_post")
            )

        included_files = export.get("included_files")
        if not isinstance(included_files, list) or not all(
            isinstance(value, str) for value in included_files
        ):
            raise ValueError("Manifest export.included_files must be a string list")

        username = (state.channel_username or "").strip()
        channel = username if username.startswith("@") else f"@{username}"
        if not username:
            channel = str(state.channel_id)

        return ChannelExportOptions(
            channel=channel,
            limit=None,
            media_mode=media_mode,
            output_dir=Path(root),
            max_media_size=max_media_size,
            media_types=media_types,
            discussion_mode=discussion_mode,
            max_comments_per_post=max_comments,
            include_jsonl=MESSAGES_JSONL in included_files,
            include_txt=MESSAGES_TXT in included_files,
            force=False,
        )

    @staticmethod
    def _load_manifest(path: Path) -> dict[str, Any]:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Cannot read channel manifest: {path}") from exc
        if not isinstance(value, dict):
            raise ValueError("Channel manifest must be a JSON object")
        return value

    @staticmethod
    def _mapping(value: dict[str, Any], key: str) -> dict[str, Any]:
        nested = value.get(key)
        if not isinstance(nested, dict):
            raise ValueError(f"Manifest {key} must be a JSON object")
        return nested

    @staticmethod
    def _text(value: dict[str, Any], key: str) -> str:
        field = value.get(key)
        if not isinstance(field, str) or not field.strip():
            raise ValueError(f"Manifest field {key} must be non-empty text")
        return field

    @staticmethod
    def _integer(value: dict[str, Any], key: str) -> int:
        field = value.get(key)
        if isinstance(field, bool) or not isinstance(field, int):
            raise ValueError(f"Manifest field {key} must be an integer")
        return field

    @staticmethod
    def _optional_non_negative_integer(value: dict[str, Any], key: str) -> int | None:
        field = value.get(key)
        if field is None:
            return None
        if isinstance(field, bool) or not isinstance(field, int) or field < 0:
            raise ValueError(f"Manifest field {key} must be a non-negative integer")
        return field

    @staticmethod
    def _media_types(value: Any) -> tuple[str, ...] | None:
        if value is None:
            return None
        if not isinstance(value, list) or not all(
            isinstance(item, str) for item in value
        ):
            raise ValueError(
                "Manifest export.media_types must be a string list or null"
            )
        return parse_media_types(",".join(value))
