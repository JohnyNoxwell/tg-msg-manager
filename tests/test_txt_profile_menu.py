import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from tg_msg_manager.cli_menu import _handle_menu_export


def test_menu_empty_txt_profile_defaults_to_context_readable():
    ctx = MagicMock()
    ctx.pm.should_stop.return_value = False

    with (
        patch(
            "tg_msg_manager.cli_menu.TerminalInput.prompt_with_esc",
            side_effect=["123", "", "n", "2", ""],
        ),
        patch(
            "tg_msg_manager.cli_menu.get_safe_user_and_chat",
            new=AsyncMock(return_value=(None, None)),
        ),
        patch(
            "tg_msg_manager.cli_menu._run_export_sync", new=AsyncMock(return_value=1)
        ),
        patch("tg_msg_manager.cli_menu._emit_export_summary", new=AsyncMock()) as emit,
        patch("tg_msg_manager.cli_menu.pause_for_enter"),
    ):
        asyncio.run(_handle_menu_export(ctx))

    assert emit.await_args.kwargs["as_json"] is False
    assert emit.await_args.kwargs["txt_profile"] == "context-readable"


def test_menu_legacy_txt_profile_passes_legacy():
    ctx = MagicMock()
    ctx.pm.should_stop.return_value = False

    with (
        patch(
            "tg_msg_manager.cli_menu.TerminalInput.prompt_with_esc",
            side_effect=["123", "", "n", "2", "legacy"],
        ),
        patch(
            "tg_msg_manager.cli_menu.get_safe_user_and_chat",
            new=AsyncMock(return_value=(None, None)),
        ),
        patch(
            "tg_msg_manager.cli_menu._run_export_sync", new=AsyncMock(return_value=1)
        ),
        patch("tg_msg_manager.cli_menu._emit_export_summary", new=AsyncMock()) as emit,
        patch("tg_msg_manager.cli_menu.pause_for_enter"),
    ):
        asyncio.run(_handle_menu_export(ctx))

    assert emit.await_args.kwargs["txt_profile"] == "legacy"


def test_menu_invalid_txt_profile_rejects_without_export():
    ctx = MagicMock()
    ctx.pm.should_stop.return_value = False

    with (
        patch(
            "tg_msg_manager.cli_menu.TerminalInput.prompt_with_esc",
            side_effect=["123", "", "n", "2", "bad"],
        ),
        patch("tg_msg_manager.cli_menu._run_export_sync", new=AsyncMock()) as sync,
        patch("tg_msg_manager.cli_menu._emit_export_summary", new=AsyncMock()) as emit,
        patch("tg_msg_manager.cli_menu.pause_for_enter"),
    ):
        asyncio.run(_handle_menu_export(ctx))

    sync.assert_not_awaited()
    emit.assert_not_awaited()
