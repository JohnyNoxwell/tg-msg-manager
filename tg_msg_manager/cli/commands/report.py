import argparse

from ...services.reporting import (
    ReportCollector,
    render_report_json,
    render_report_markdown,
)


async def _handle_report_command(ctx, args: argparse.Namespace) -> None:
    collector = ReportCollector(
        storage=ctx.storage,
        exports_dir=ctx.paths.db_exports_dir,
    )
    report = collector.collect()
    output = render_report_json(report) if args.json else render_report_markdown(report)
    print(output)
