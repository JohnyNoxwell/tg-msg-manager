from .cli_io import (
    TerminalInput,
    pause_for_enter,
    print_target_list,
    print_update_summary,
)
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
from .i18n import _, get_lang, set_lang
from .infrastructure.storage.records import PrimaryTarget
from .services.reporting import (
    ReportCollector,
    render_report_json,
    render_report_markdown,
)
from .services.scheduler import setup_scheduler
from .utils.ui import UI


async def _handle_menu_export(ctx) -> None:
    UI.print_header(_("menu_1"), _("menu_1_desc"))
    target_str = TerminalInput.prompt_with_esc(_("prompt_target") + ": ")
    if target_str is None or target_str.strip() == "0":
        return

    chat_str = TerminalInput.prompt_with_esc(_("prompt_chat") + ": ")
    if chat_str is None:
        return

    deep_choice = TerminalInput.prompt_with_esc(
        _("prompt_deep").replace("[y/N]", "[y]").replace("[Y/n]", "[y]") + ": "
    )
    if deep_choice is None:
        return
    active_deep = deep_choice.lower() != "n"

    active_depth = 2
    if active_deep:
        depth_str = TerminalInput.prompt_with_esc(f"{_('depth_label')} (1-5) [2]: ")
        if depth_str and depth_str.isdigit():
            active_depth = int(depth_str)

    user_ent, chat_ent = await get_safe_user_and_chat(
        ctx.client,
        target_str.strip(),
        chat_str.strip() if chat_str else None,
    )
    _store_resolved_user(ctx, user_ent)

    final_uid = user_ent.id if user_ent else resolve_id(target_str)
    ctx.active_uid = final_uid
    processed = 0
    try:
        processed = await _run_export_sync(
            ctx,
            final_uid=final_uid,
            user_ent=user_ent,
            chat_ent=chat_ent,
            deep_mode=active_deep,
            recursive_depth=active_depth,
        )
    finally:
        if ctx.pm.should_stop():
            print(
                f"\n{UI.paint('▲', UI.CLR_WARN, bold=True)} {UI.paint(_('text_interrupted_exporting_partial'), UI.CLR_WARN)}"
            )
        if final_uid:
            await _emit_export_summary(
                ctx,
                final_uid=final_uid,
                processed=processed,
                as_json=True,
                show_finalize_section=False,
                show_saved_path=False,
            )
    pause_for_enter()


async def _handle_menu_update(ctx) -> None:
    UI.print_header(_("menu_2"), _("menu_2_desc"))
    updated_stats = await _sync_and_export_dirty_targets(
        ctx, emit_telemetry_summary=False
    )
    if updated_stats:
        print_update_summary(updated_stats, title="Update")
    pause_for_enter()


async def _handle_menu_clean(ctx) -> None:
    UI.print_header(_("menu_3"), _("sub_clean_info"))
    pm_choice = TerminalInput.prompt_with_esc(_("prompt_clean_pms") + ": ")
    if pm_choice is None:
        return
    confirm = TerminalInput.prompt_with_esc(_("clean_confirm") + " (y/n): ")
    if confirm and confirm.lower() == "y":
        deleted = await ctx.cleaner.global_self_cleanup(
            dry_run=False, include_pms=(pm_choice.lower() == "y")
        )
        print(
            f"\n{UI.section(_('summary_header'), icon='◆')}\n{_('total_deleted_msgs', count=deleted)}"
        )
    pause_for_enter()


async def _handle_menu_export_pm(ctx) -> None:
    UI.print_header(_("menu_4"), _("menu_4_desc"))
    target_str = TerminalInput.prompt_with_esc(_("prompt_pm_target") + ": ")
    if target_str:
        user_ent, _unused = await get_safe_user_and_chat(ctx.client, target_str.strip())
        if user_ent:
            await ctx.private_archive.archive_pm(user_ent)
    pause_for_enter()


async def _handle_menu_delete_data(ctx) -> None:
    UI.print_header(_("menu_5"), _("menu_5_desc"))
    users = ctx.storage.get_primary_targets()
    if users:
        print_target_list(users)
        idx = TerminalInput.prompt_with_esc("\nChoice: ")
        if idx and idx.isdigit() and 1 <= int(idx) <= len(users):
            target = PrimaryTarget.coerce(users[int(idx) - 1])
            await ctx.cleaner.purge_user_data(target.user_id)
        else:
            print(UI.paint(_("text_invalid_selection"), UI.CLR_WARN))
    else:
        print(UI.paint(_("no_targets"), UI.CLR_WARN))
    pause_for_enter()


async def _handle_menu_schedule(ctx) -> None:
    UI.print_header(_("menu_6"), _("help_desc_6"))
    request = _prompt_scheduler_setup_request()
    result = await setup_scheduler(
        request,
        project_root=ctx.paths.project_root,
        python_path=ctx.runtime.python_executable,
    )
    _print_scheduler_setup_result(result, paint_errors=True)
    pause_for_enter()


async def _handle_menu_setup(ctx) -> None:
    UI.print_header(_("menu_7"), _("sub_setup_info"))
    _print_alias_install_result(ctx, paint_errors=True)
    pause_for_enter()


async def _handle_menu_about(ctx) -> None:
    UI.print_header(_("menu_8"), _("about_text"))
    pause_for_enter()


async def _handle_menu_db_export(ctx) -> None:
    UI.print_header(_("menu_9"), _("sub_db_export_info"))
    users = ctx.storage.get_primary_targets()
    if users:
        print_target_list(users)
        idx_str = TerminalInput.prompt_with_esc("\n" + _("choice_prompt") + ": ")
        if idx_str and idx_str.isdigit() and 1 <= int(idx_str) <= len(users):
            target = PrimaryTarget.coerce(users[int(idx_str) - 1])
            fmt = TerminalInput.prompt_with_esc(_("label_format_prompt"))
            if fmt == "1":
                await ctx.db_exporter.export_user_messages(target.user_id, as_json=True)
            elif fmt == "2":
                await ctx.db_exporter.export_user_messages(
                    target.user_id, as_json=False
                )
    else:
        print(UI.paint(_("no_targets"), UI.CLR_WARN))
    pause_for_enter()


async def _handle_menu_retry(ctx) -> None:
    UI.print_header(_("menu_retry"), _("sub_retry_info"))
    print(f"  [1] {_('retry_action_run')}")
    print(f"  [2] {_('retry_action_list')}")
    print(f"  [3] {_('retry_action_cleanup')}")
    choice = TerminalInput.prompt_with_esc("\n" + _("retry_action_prompt") + ": ")
    if choice is None:
        return

    normalized = choice.strip()
    if normalized == "2":
        _print_retry_tasks(ctx.storage.list_retry_tasks(limit=10))
    elif normalized == "3":
        cleaned = ctx.storage.cleanup_retry_tasks()
        _print_retry_summary(RetryRunStats(cleaned=cleaned))
    else:
        stats = await ctx.retry_worker.run_due_tasks(limit=10)
        _print_retry_summary(stats)
    pause_for_enter()


async def _handle_menu_report(ctx) -> None:
    UI.print_header(_("menu_report"), _("sub_report_info"))
    print(f"  [1] {_('report_format_markdown')}")
    print(f"  [2] {_('report_format_json')}")
    choice = TerminalInput.prompt_with_esc("\n" + _("report_format_prompt") + ": ")
    if choice is None:
        return

    collector = ReportCollector(
        storage=ctx.storage,
        exports_dir=ctx.paths.db_exports_dir,
    )
    report = collector.collect()
    normalized = choice.strip()
    output = (
        render_report_json(report)
        if normalized == "2"
        else render_report_markdown(report)
    )
    print(output)
    pause_for_enter()


async def _dispatch_main_menu_choice(ctx, choice: str) -> bool:
    if choice == "L":
        set_lang("en" if get_lang() == "ru" else "ru")
        return True
    if choice == "0":
        return False
    if choice == "R":
        await _handle_menu_retry(ctx)
        return True
    if choice == "P":
        await _handle_menu_report(ctx)
        return True

    handlers = {
        "1": _handle_menu_export,
        "2": _handle_menu_update,
        "3": _handle_menu_clean,
        "4": _handle_menu_export_pm,
        "5": _handle_menu_delete_data,
        "6": _handle_menu_schedule,
        "7": _handle_menu_setup,
        "8": _handle_menu_about,
        "9": _handle_menu_db_export,
    }
    handler = handlers.get(choice)
    if handler is not None:
        await handler(ctx)
    return True
