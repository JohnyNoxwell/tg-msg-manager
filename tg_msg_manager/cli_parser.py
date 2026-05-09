import argparse

from .services.channel_export.discussions.options import (
    DEFAULT_MAX_COMMENTS_PER_POST,
    validate_discussion_mode,
    validate_max_comments_per_post,
)
from .services.channel_export.media_types import parse_media_types
from .services.channel_export.size_parser import parse_media_size


def _parse_media_size_argument(value: str) -> int:
    try:
        parsed = parse_media_size(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc
    assert parsed is not None
    return parsed


def _parse_media_types_argument(value: str):
    try:
        return parse_media_types(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def _parse_discussion_mode_argument(value: str) -> str:
    try:
        return validate_discussion_mode(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def _parse_max_comments_per_post_argument(value: str) -> int:
    try:
        return validate_max_comments_per_post(int(value))
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="TG_MSG_MNGR CLI")
    subparsers = parser.add_subparsers(dest="command")

    export_parser = subparsers.add_parser("export")
    export_parser.add_argument("--user-id", required=True)
    export_parser.add_argument("--chat-id", default=None)
    export_parser.add_argument("--deep", action="store_true", default=True)
    export_parser.add_argument("--flat", action="store_false", dest="deep")
    export_parser.add_argument("--force-resync", action="store_true")
    export_parser.add_argument("--context-window", type=int, default=3)
    export_parser.add_argument("--max-cluster", type=int, default=10)
    export_parser.add_argument("--depth", type=int, default=2)
    export_parser.add_argument("--limit", type=int, default=None)
    export_parser.add_argument("--json", action="store_true")

    subparsers.add_parser("update")
    retry_parser = subparsers.add_parser("retry")
    retry_parser.add_argument("--limit", type=int, default=10)
    retry_parser.add_argument("--list", action="store_true")
    retry_parser.add_argument("--cleanup", action="store_true")
    report_parser = subparsers.add_parser("report")
    report_parser.add_argument("--json", action="store_true")

    clean_parser = subparsers.add_parser("clean")
    clean_parser.add_argument("--dry-run", action="store_true", default=None)
    clean_parser.add_argument("--apply", action="store_true")
    clean_parser.add_argument("--yes", "-y", action="store_true")

    subparsers.add_parser("export-pm").add_argument("--user-id", required=True)
    subparsers.add_parser("delete").add_argument("--user-id", required=True)
    subparsers.add_parser("schedule")
    subparsers.add_parser("setup")

    db_parser = subparsers.add_parser("db-export")
    db_parser.add_argument("--user-id", required=True)
    db_parser.add_argument("--json", action="store_true", default=False)

    validate_dataset_parser = subparsers.add_parser("validate-dataset")
    validate_dataset_parser.add_argument("--path", required=True)
    validate_dataset_parser.add_argument("--json", action="store_true", default=False)

    inspect_dataset_parser = subparsers.add_parser("inspect-dataset")
    inspect_dataset_parser.add_argument("--path", required=True)
    inspect_dataset_parser.add_argument("--json", action="store_true", default=False)

    export_channel_parser = subparsers.add_parser("export-channel")
    export_channel_parser.add_argument("--channel", required=True)
    export_channel_parser.add_argument("--limit", type=int, default=None)
    export_channel_parser.add_argument(
        "--media",
        choices=("none", "metadata", "full"),
        default="metadata",
    )
    export_channel_parser.add_argument(
        "--max-media-size",
        type=_parse_media_size_argument,
        default=None,
        help="Maximum media file size for --media full, e.g. 50MB",
    )
    export_channel_parser.add_argument(
        "--media-types",
        type=_parse_media_types_argument,
        default=None,
        help="Comma-separated allowlist for --media full: photo,video,document,audio,voice,animation",
    )
    export_channel_parser.add_argument(
        "--discussion",
        choices=("none", "full"),
        type=_parse_discussion_mode_argument,
        default="none",
    )
    export_channel_parser.add_argument(
        "--max-comments-per-post",
        type=_parse_max_comments_per_post_argument,
        default=DEFAULT_MAX_COMMENTS_PER_POST,
        help="Maximum linked discussion comments to export per channel post",
    )
    export_channel_parser.add_argument("--output-dir", default=None)
    export_channel_parser.add_argument("--force", action="store_true", default=False)
    return parser
