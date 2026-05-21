import argparse

from ...cli_io import print_update_summary
from ...cli_support import _sync_and_export_dirty_targets, resolve_id
from ...i18n import _
from ...utils.ui import UI


async def _handle_delete_command(ctx, args: argparse.Namespace) -> None:
    uid = resolve_id(args.user_id)
    await ctx.cleaner.purge_user_data(uid)


async def _handle_update_command(ctx, args: argparse.Namespace) -> None:
    del args
    stats = await _sync_and_export_dirty_targets(ctx, emit_telemetry_summary=True)
    print_update_summary(stats, title=_("label_update"))


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
