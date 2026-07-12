import argparse
from pathlib import Path
from typing import Union

from ..channel_export_options import (
    ChannelExportCommandOptions,
    build_channel_export_service_options,
    coerce_channel_export_command_options,
)
from ...services.channel_export import ChannelExportError
from ...services.channel_export.batch_models import BATCH_STATUS_FAILED


async def _handle_export_channel_command(
    ctx,
    args: Union[argparse.Namespace, ChannelExportCommandOptions],
) -> None:
    command_options = coerce_channel_export_command_options(args)
    options = build_channel_export_service_options(
        command_options,
        default_output_dir=ctx.paths.channel_exports_dir,
    )
    try:
        result = await ctx.channel_exporter.export_channel(options)
    except ChannelExportError as exc:
        raise SystemExit(str(exc)) from exc
    except Exception as exc:
        raise SystemExit(f"Channel export failed: {exc}") from exc
    print("Channel export completed")
    print(f"Mode: {result.run_mode}")
    print(f"Posts exported this run: {result.posts_exported_this_run}")
    print(f"Total known exported posts: {result.message_count}")
    print(f"Media records added this run: {result.media_records_added_this_run}")
    print(f"Total known media records: {result.media_count}")
    print(f"Downloaded media this run: {result.downloaded_media_count_this_run}")
    print(
        f"Already existing media this run: {result.already_existing_media_count_this_run}"
    )
    print(f"Skipped by size this run: {result.skipped_by_size_count_this_run}")
    print(f"Skipped by type this run: {result.skipped_by_type_count_this_run}")
    print(f"Failed media this run: {result.failed_media_count_this_run}")
    print(f"Manifest: {result.manifest_path}")
    print(f"JSONL: {result.messages_jsonl_path}")
    print(f"TXT: {result.messages_txt_path}")
    print(f"Media manifest: {result.media_manifest_path}")
    print(f"State: {result.state_path}")
    if result.discussion_mode == "metadata":
        print("Discussion mode: metadata")
        print(
            f"Discussion metadata records this run: {result.discussion_metadata_count_this_run}"
        )
        print(f"Discussion metadata: {result.discussion_metadata_jsonl_path}")
    elif result.discussion_mode == "full":
        print("Discussion mode: full")
        print(f"Discussion threads this run: {result.discussion_thread_count_this_run}")
        print(
            f"Discussion comments this run: {result.discussion_comment_count_this_run}"
        )
        print(
            "Failed discussion threads this run: "
            f"{result.failed_discussion_thread_count_this_run}"
        )
        print(f"Discussion comments: {result.discussion_comments_jsonl_path}")
        print(f"Discussion threads: {result.discussion_threads_jsonl_path}")
        print(f"Discussion state: {result.discussion_state_path}")


async def _handle_update_channels_command(ctx, args: argparse.Namespace) -> None:
    root = (
        Path(args.output_dir)
        if args.output_dir
        else Path(ctx.paths.channel_exports_dir)
    )
    try:
        result = await ctx.channel_batch_updater.update_all(root)
    except Exception as exc:
        raise SystemExit(f"Channel batch update failed: {exc}") from exc

    for item in result.items:
        line = f"{item.status}: {item.channel}"
        if item.status == BATCH_STATUS_FAILED:
            line = f"{line}: {item.error}"
        else:
            line = f"{line}: posts={item.posts_exported}"
        print(line)
    print(
        "Channel batch update summary: "
        f"updated={result.updated_count} "
        f"no_new_posts={result.no_new_posts_count} "
        f"failed={result.failed_count}"
    )
    if result.failed_count:
        raise SystemExit(1)
