import argparse
import logging
from pathlib import Path

from .cli_io import print_update_summary
from .cli_support import (
    _emit_export_summary,
    _print_alias_install_result,
    _print_retry_summary,
    _print_retry_tasks,
    _print_scheduler_setup_result,
    _prompt_scheduler_setup_request,
    _run_export_sync,
    _store_resolved_user,
    _sync_and_export_dirty_targets,
    get_safe_user_and_chat,
    resolve_id,
)
from .core.models.retry import RetryRunStats
from .i18n import _
from .services.channel_export import ChannelExportError, ChannelExportOptions
from .services.reporting import (
    ReportCollector,
    render_report_json,
    render_report_markdown,
)
from .services.retry_worker import enqueue_archive_pm_retry_task
from .services.scheduler import setup_scheduler
from .utils.ui import UI


logger = logging.getLogger(__name__)


async def _handle_setup_command(ctx, args: argparse.Namespace) -> None:
    del args
    _print_alias_install_result(ctx, paint_errors=False)


async def _handle_schedule_command(ctx, args: argparse.Namespace) -> None:
    del args
    request = _prompt_scheduler_setup_request()
    result = await setup_scheduler(
        request,
        project_root=ctx.paths.project_root,
        python_path=ctx.runtime.python_executable,
    )
    _print_scheduler_setup_result(result, paint_errors=False)


async def _handle_delete_command(ctx, args: argparse.Namespace) -> None:
    uid = resolve_id(args.user_id)
    await ctx.cleaner.purge_user_data(uid)


async def _handle_db_export_command(ctx, args: argparse.Namespace) -> None:
    uid = resolve_id(args.user_id)
    await ctx.db_exporter.export_user_messages(uid, as_json=args.json)


async def _handle_export_command(ctx, args: argparse.Namespace) -> None:
    ctx.active_uid = resolve_id(args.user_id)
    user_ent, chat_ent = await get_safe_user_and_chat(
        ctx.client, args.user_id, args.chat_id
    )
    _store_resolved_user(ctx, user_ent)

    processed = 0
    try:
        processed = await _run_export_sync(
            ctx,
            final_uid=ctx.active_uid,
            user_ent=user_ent,
            chat_ent=chat_ent,
            deep_mode=args.deep,
            recursive_depth=args.depth,
            force_resync=args.force_resync,
            context_window=args.context_window,
            max_cluster=args.max_cluster,
            limit=args.limit,
        )
        await _emit_export_summary(
            ctx,
            final_uid=ctx.active_uid,
            processed=processed,
            as_json=args.json,
            show_finalize_section=True,
            show_saved_path=True,
        )
    except Exception as e:
        if not ctx.pm.should_stop():
            logger.error(f"Error during export: {e}")


async def _handle_update_command(ctx, args: argparse.Namespace) -> None:
    del args
    stats = await _sync_and_export_dirty_targets(ctx, emit_telemetry_summary=True)
    print_update_summary(stats, title=_("label_update"))


async def _handle_retry_command(ctx, args: argparse.Namespace) -> None:
    if args.list:
        _print_retry_tasks(ctx.storage.list_retry_tasks(limit=args.limit))
        return
    if args.cleanup:
        cleaned = ctx.storage.cleanup_retry_tasks()
        _print_retry_summary(RetryRunStats(cleaned=cleaned))
        return

    stats = await ctx.retry_worker.run_due_tasks(limit=args.limit)
    _print_retry_summary(stats)


async def _handle_report_command(ctx, args: argparse.Namespace) -> None:
    collector = ReportCollector(
        storage=ctx.storage,
        exports_dir=ctx.paths.db_exports_dir,
    )
    report = collector.collect()
    output = render_report_json(report) if args.json else render_report_markdown(report)
    print(output)


async def _handle_clean_command(ctx, args: argparse.Namespace) -> None:
    is_dry = True
    if args.apply or args.yes:
        is_dry = False
    if args.dry_run is True:
        is_dry = True
    deleted = await ctx.cleaner.global_self_cleanup(dry_run=is_dry)
    print(
        f"\n{UI.section(_('summary_header'), icon='◆')}\n{_('total_deleted_msgs', count=deleted)}"
    )
    if is_dry:
        print(UI.paint(_("dry_run_info"), UI.CLR_WARN))


async def _handle_export_pm_command(ctx, args: argparse.Namespace) -> None:
    user_ent, _unused = await get_safe_user_and_chat(ctx.client, args.user_id)
    if user_ent:
        try:
            await ctx.private_archive.archive_pm(user_ent)
        except Exception as exc:
            enqueue_archive_pm_retry_task(
                ctx.storage,
                user_id=user_ent.id,
                error=exc,
            )
            logger.error(f"Error during PM archive: {exc}")


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
