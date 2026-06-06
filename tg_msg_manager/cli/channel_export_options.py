from argparse import Namespace
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

from ..services.channel_export import ChannelExportOptions


@dataclass(frozen=True)
class ChannelExportCommandOptions:
    channel: str
    limit: Optional[int]
    media: str
    max_media_size: Optional[int]
    media_types: Optional[tuple[str, ...]]
    discussion: str
    max_comments_per_post: int
    output_dir: Optional[str]
    force: bool


def build_channel_export_command_options(
    *,
    channel: str,
    limit: Optional[int],
    media: str,
    max_media_size: Optional[int],
    media_types: Optional[tuple[str, ...]],
    discussion: str,
    max_comments_per_post: int,
    output_dir: Optional[str],
    force: bool,
) -> ChannelExportCommandOptions:
    return ChannelExportCommandOptions(
        channel=channel,
        limit=limit,
        media=media,
        max_media_size=max_media_size,
        media_types=media_types,
        discussion=discussion,
        max_comments_per_post=max_comments_per_post,
        output_dir=output_dir,
        force=force,
    )


def channel_export_options_from_namespace(
    args: Namespace,
) -> ChannelExportCommandOptions:
    return build_channel_export_command_options(
        channel=args.channel,
        limit=args.limit,
        media=args.media,
        max_media_size=args.max_media_size,
        media_types=args.media_types,
        discussion=args.discussion,
        max_comments_per_post=args.max_comments_per_post,
        output_dir=args.output_dir,
        force=args.force,
    )


def coerce_channel_export_command_options(
    args: Union[Namespace, ChannelExportCommandOptions],
) -> ChannelExportCommandOptions:
    if isinstance(args, ChannelExportCommandOptions):
        return args
    return channel_export_options_from_namespace(args)


def build_channel_export_service_options(
    options: ChannelExportCommandOptions,
    *,
    default_output_dir: str,
) -> ChannelExportOptions:
    output_dir = (
        Path(options.output_dir) if options.output_dir else Path(default_output_dir)
    )
    return ChannelExportOptions(
        channel=options.channel,
        limit=options.limit,
        media_mode=options.media,
        output_dir=output_dir,
        max_media_size=options.max_media_size,
        media_types=options.media_types,
        discussion_mode=options.discussion,
        max_comments_per_post=options.max_comments_per_post,
        force=options.force,
    )
