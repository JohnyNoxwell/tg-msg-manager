import argparse
from pathlib import Path

from ...services.channel_export import ChannelExportError, ChannelExportOptions


async def _handle_export_channel_command(ctx, args: argparse.Namespace) -> None:
    output_dir = (
        Path(args.output_dir)
        if args.output_dir
        else Path(ctx.paths.channel_exports_dir)
    )
    options = ChannelExportOptions(
        channel=args.channel,
        limit=args.limit,
        media_mode=args.media,
        output_dir=output_dir,
        max_media_size=args.max_media_size,
        media_types=args.media_types,
        discussion_mode=args.discussion,
        max_comments_per_post=args.max_comments_per_post,
        force=args.force,
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
