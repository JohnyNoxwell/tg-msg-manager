import argparse
import logging

from ...cli_support import (
    _emit_export_summary,
    _run_export_sync,
    _store_resolved_user,
    get_safe_user_and_chat,
    resolve_id,
)
from ...services.retry_worker import enqueue_archive_pm_retry_task


logger = logging.getLogger(__name__)


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
            txt_profile=args.txt_profile,
            show_finalize_section=True,
            show_saved_path=True,
        )
    except Exception as e:
        if not ctx.pm.should_stop():
            logger.error(f"Error during export: {e}")


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
