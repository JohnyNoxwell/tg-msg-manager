import argparse

from ...cli_support import (
    _print_alias_install_result,
    _print_scheduler_setup_result,
    _prompt_scheduler_setup_request,
)
from ...services.scheduler import setup_scheduler


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
