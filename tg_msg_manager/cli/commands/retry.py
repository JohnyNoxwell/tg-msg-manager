import argparse

from ...cli_support import _print_retry_summary, _print_retry_tasks
from ...core.models.retry import RetryRunStats


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
