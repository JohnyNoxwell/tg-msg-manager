import logging
from typing import Any, Optional

from .core.models.retry import RetryRunStats
from .core.models.setup import SchedulerSetupRequest, SchedulerSetupResult
from .core.models.sync_report import TrackedSyncRunReport
from .core.telemetry import telemetry
from .i18n import _
from .services.rendering import DEFAULT_TXT_PROFILE
from .utils.ui import UI


logger = logging.getLogger(__name__)


def resolve_id(id_str: str) -> Any:
    try:
        return int(id_str)
    except (ValueError, TypeError):
        return id_str


async def get_safe_user_and_chat(
    client: Any,
    user_id_str: str,
    chat_id_str: Optional[str] = None,
):
    user_id = resolve_id(user_id_str)
    chat_id = resolve_id(chat_id_str) if chat_id_str else None

    chat_entity = None
    if chat_id:
        try:
            chat_entity = await client.get_entity(chat_id)
        except Exception as e:
            logger.warning(f"Could not resolve chat {chat_id}: {e}")

    user_entity = None
    try:
        user_entity = await client.get_entity(user_id)
    except Exception as e:
        logger.warning(f"Could not resolve user {user_id} directly: {e}")

    return user_entity, chat_entity


def get_dirty_target_ids(stats: Any) -> list:
    try:
        report = TrackedSyncRunReport.coerce(stats)
    except TypeError:
        return []
    return report.dirty_user_ids()


def _store_resolved_user(ctx: Any, user_ent: Any) -> None:
    if not user_ent:
        return
    ctx.active_uid = user_ent.id
    ctx.storage.upsert_user(
        user_id=user_ent.id,
        first_name=getattr(user_ent, "first_name", None),
        last_name=getattr(user_ent, "last_name", None),
        username=getattr(user_ent, "username", None),
        author_name=UI.format_name(user_ent),
    )


async def _run_export_sync(
    ctx: Any,
    *,
    final_uid: Any,
    user_ent: Any,
    chat_ent: Any,
    deep_mode: bool,
    recursive_depth: int,
    force_resync: bool = False,
    context_window: int = 3,
    max_cluster: int = 10,
    limit: Optional[int] = None,
) -> int:
    if chat_ent:
        return await ctx.exporter.sync_chat(
            chat_ent,
            from_user_id=final_uid,
            deep_mode=deep_mode,
            force_resync=force_resync,
            context_window=context_window,
            max_cluster=max_cluster,
            recursive_depth=recursive_depth,
            limit=limit,
        )
    if user_ent or isinstance(final_uid, int):
        return await ctx.exporter.sync_all_dialogs_for_user(
            final_uid,
            target_chat_ids=ctx.settings.chats_to_search_user_msgs,
            deep_mode=deep_mode,
            force_resync=force_resync,
            context_window=context_window,
            max_cluster=max_cluster,
            recursive_depth=recursive_depth,
            limit=limit,
        )
    print(
        f"{UI.paint(UI.ICON_ERROR, UI.CLR_ERROR, bold=True)} {UI.paint(_('text_could_not_resolve_target', target=final_uid), UI.CLR_ERROR)}"
    )
    return 0


async def _emit_export_summary(
    ctx: Any,
    *,
    final_uid: Any,
    processed: int,
    as_json: bool,
    txt_profile: str = DEFAULT_TXT_PROFILE,
    show_finalize_section: bool = True,
    show_saved_path: bool = True,
) -> None:
    if show_finalize_section:
        print(f"\n{UI.section(_('section_finalizing_export'), icon=UI.ICON_SECTION)}")

    path = await ctx.db_exporter.export_user_messages(
        final_uid, as_json=as_json, include_date=False, txt_profile=txt_profile
    )
    if show_saved_path and path:
        print(
            f"{UI.paint(UI.ICON_SUCCESS, UI.CLR_SUCCESS, bold=True)} {UI.paint(_('text_export_saved'), UI.CLR_SUCCESS)}  {UI.muted(path)}"
        )

    telemetry.log_summary("Export telemetry summary")
    user_info = ctx.storage.get_user(final_uid)
    target_name = UI.format_name(user_info) if user_info else f"ID:{final_uid}"
    UI.print_final_summary(
        "sync_summary_title",
        [
            {
                "title": f"{_('label_export')}: {target_name}",
                "lines": [("processed", processed)],
            }
        ],
    )


async def _sync_and_export_dirty_targets(
    ctx: Any, *, emit_telemetry_summary: bool
) -> TrackedSyncRunReport:
    stats = await ctx.exporter.sync_all_tracked()
    for uid in get_dirty_target_ids(stats):
        await ctx.db_exporter.update_user_messages(
            uid, as_json=True, include_date=False
        )
    if emit_telemetry_summary:
        telemetry.log_summary("Update telemetry summary")
    return stats


def _print_alias_install_result(ctx: Any, *, paint_errors: bool) -> None:
    res = ctx.alias_manager.install()
    if res.success:
        if res.rc_path:
            print(_("setup_success_unix", path=res.rc_path))
            print(_("setup_activate", path=res.rc_path))
        elif res.bin_dir:
            print(_("setup_success_win", dir=res.bin_dir))
        print("\n" + _("alias_header"))
        for spec in ctx.alias_manager.get_alias_specs():
            print(f"  {spec.alias:<4} -> {_(spec.label_key)}")
        return

    if res.error_kind == "unsupported_platform":
        error_message = _("setup_platform_error", plt=res.platform)
    else:
        error_message = res.error_detail or (
            "Error during setup." if paint_errors else "Error during setup"
        )
    if paint_errors:
        print(UI.paint(error_message, UI.CLR_ERROR))
    else:
        print(error_message)


def _prompt_scheduler_setup_request() -> SchedulerSetupRequest:
    default_request = SchedulerSetupRequest()
    try:
        time_input = input(_("sched_time_prompt")).strip()
    except EOFError:
        return default_request

    if not time_input:
        return default_request

    try:
        hour_str, minute_str = time_input.split(":", 1)
        return SchedulerSetupRequest(hour=int(hour_str), minute=int(minute_str))
    except (ValueError, TypeError):
        print(UI.paint(_("sched_invalid_time"), UI.CLR_WARN))
        return default_request


def _print_scheduler_setup_result(
    result: SchedulerSetupResult, *, paint_errors: bool
) -> None:
    if result.success:
        mode = _("sched_daily_at", time=f"{result.hour:02d}:{result.minute:02d}")
        print(_("sched_success_macos", mode=mode))
        print(_("sched_logs_path", path=result.logs_dir))
        print(_("sched_complete"))
        return

    if result.error_kind == "launchctl_load_failed":
        error_message = _("sched_register_error", error=result.error_detail or "")
    else:
        error_message = _("sched_unexpected_error", error=result.error_detail or "")

    if paint_errors:
        print(UI.paint(error_message, UI.CLR_ERROR))
    else:
        print(error_message)


def _print_retry_tasks(tasks: list[Any]) -> None:
    if not tasks:
        print("Retry queue is empty.")
        return
    for task in tasks:
        print(
            f"{task.task_id} | {task.task_type} | status={task.status} | "
            f"chat={task.chat_id} | target={task.target_user_id} | "
            f"retry_count={task.retry_count} | due={task.next_retry_timestamp}"
        )


def _print_retry_summary(stats: RetryRunStats) -> None:
    print(
        "Retry run summary: "
        f"scanned={stats.scanned}, "
        f"succeeded={stats.succeeded}, "
        f"rescheduled={stats.rescheduled}, "
        f"failed={stats.failed}, "
        f"cleaned={stats.cleaned}"
    )
