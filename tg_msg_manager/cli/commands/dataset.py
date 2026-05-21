import argparse
from pathlib import Path

from ...services.dataset_validation import (
    DatasetInspectionOptions,
    DatasetValidationOptions,
    inspect_dataset,
    render_inspection_report_json,
    render_inspection_report_markdown,
    render_validation_report_json,
    render_validation_report_markdown,
    validate_dataset,
)


async def _handle_validate_dataset_command(ctx, args: argparse.Namespace) -> None:
    del ctx
    report = validate_dataset(
        DatasetValidationOptions(dataset_path=Path(args.path).expanduser())
    )
    output = (
        render_validation_report_json(report)
        if args.json
        else render_validation_report_markdown(report)
    )
    print(output)
    if report.status == "errors":
        raise SystemExit(1)


async def _handle_inspect_dataset_command(ctx, args: argparse.Namespace) -> None:
    del ctx
    report = inspect_dataset(
        DatasetInspectionOptions(dataset_path=Path(args.path).expanduser())
    )
    output = (
        render_inspection_report_json(report)
        if args.json
        else render_inspection_report_markdown(report)
    )
    print(output)
