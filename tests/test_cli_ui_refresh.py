from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from tg_msg_manager.cli_io import print_update_summary, render_main_menu
from tg_msg_manager.i18n import use_lang
from tg_msg_manager.utils.ui import UI


def test_prompt_text_uses_plain_suffix_without_tty():
    with patch.object(UI, "is_tty", return_value=False):
        assert UI.prompt_text("Введите ID") == "Введите ID: "
        assert UI.prompt_text("Уверены?", suffix="", hint="(y/n)") == "Уверены? (y/n)"


def test_menu_row_uses_compact_alignment_without_tty():
    with patch.object(UI, "is_tty", return_value=False):
        assert UI.menu_row("01", "Экспорт", "История сообщений") == " 01 ▸ Экспорт  История сообщений"


def test_render_main_menu_uses_compact_menu_rows_without_tty():
    output = StringIO()
    with use_lang("ru"), patch.object(UI, "clear_screen"), patch.object(
        UI, "print_gradient_banner"
    ), patch.object(UI, "is_tty", return_value=False), redirect_stdout(output):
        render_main_menu(123)

    text = output.getvalue()
    assert "[01]" not in text
    assert "01 ▸ Экспорт" in text
    assert "12 ▸ Audit Report" in text


def test_print_update_summary_renders_divided_lines_without_tty():
    output = StringIO()
    stats = {
        42: {"name": "Target", "count": 3, "dirty": True, "own_messages": 2, "with_context": 1}
    }
    with use_lang("ru"), patch.object(UI, "is_tty", return_value=False), redirect_stdout(
        output
    ):
        print_update_summary(stats, title="Update")

    text = output.getvalue()
    assert "обновление завершено" not in text
    assert "обработано" not in text
    assert "без контекста" in text
    assert "с контекстом" in text
    assert "· 2" in text
    assert "· 1" in text


def test_print_update_summary_empty_state_is_neutral_without_tty():
    output = StringIO()
    with use_lang("ru"), patch.object(UI, "is_tty", return_value=False), redirect_stdout(
        output
    ):
        print_update_summary({}, title="Update")

    text = output.getvalue()
    assert "Update" in text
    assert "·" in text
    assert "Всего новых сообщений: 0" in text


def test_final_summary_uses_divider_between_label_and_value_without_tty():
    output = StringIO()
    with use_lang("ru"), patch.object(UI, "is_tty", return_value=False), redirect_stdout(
        output
    ):
        UI.print_final_summary(
            "sync_summary_title",
            [{"title": "Target", "lines": [("processed", 3)]}],
        )

    text = output.getvalue()
    assert "обработано" in text
    assert "· 3" in text
