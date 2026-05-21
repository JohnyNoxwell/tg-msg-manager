import argparse

from ...cli_support import resolve_id


async def _handle_db_export_command(ctx, args: argparse.Namespace) -> None:
    uid = resolve_id(args.user_id)
    await ctx.db_exporter.export_user_messages(
        uid,
        as_json=args.json,
        txt_profile=args.txt_profile,
    )
