import argparse
import sys

from ...services.target_names import query_target_names
from ...services.target_names.renderers import (
    render_target_names_error,
    render_target_names_json,
    render_target_names_text,
)


async def _handle_target_command(ctx, args: argparse.Namespace) -> None:
    if args.target_command != "names":
        raise SystemExit(2)

    result = query_target_names(ctx.storage, args.target, field=args.field)
    if result.status != "found":
        code = (
            "ambiguous_target"
            if result.status == "ambiguous"
            else "target_not_found"
        )
        sys.stderr.write(
            render_target_names_error(
                code=code,
                target=result.target,
                json_output=args.format == "json",
            )
            + "\n"
        )
        raise SystemExit(1)

    output = (
        render_target_names_json(result, field=args.field)
        if args.format == "json"
        else render_target_names_text(result, field=args.field)
    )
    print(output)
