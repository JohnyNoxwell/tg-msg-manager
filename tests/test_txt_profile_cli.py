import pytest

from tg_msg_manager.cli_parser import build_cli_parser
from tg_msg_manager.services.rendering import DEFAULT_TXT_PROFILE


def test_export_parser_accepts_txt_profiles():
    parser = build_cli_parser()

    args = parser.parse_args(
        ["export", "--user-id", "123", "--chat-id", "456", "--txt-profile", "legacy"]
    )
    assert args.txt_profile == "legacy"

    args = parser.parse_args(
        [
            "export",
            "--user-id",
            "123",
            "--chat-id",
            "456",
            "--txt-profile",
            "context-readable",
        ]
    )
    assert args.txt_profile == "context-readable"


def test_export_parser_rejects_unknown_txt_profile():
    parser = build_cli_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(["export", "--user-id", "123", "--txt-profile", "compact"])


def test_export_parser_default_txt_profile_is_context_readable():
    parser = build_cli_parser()

    args = parser.parse_args(["export", "--user-id", "123"])

    assert args.txt_profile == DEFAULT_TXT_PROFILE


def test_export_parser_json_flag_still_sets_json_without_changing_profile_default():
    parser = build_cli_parser()

    args = parser.parse_args(["export", "--user-id", "123", "--json"])

    assert args.json is True
    assert args.txt_profile == DEFAULT_TXT_PROFILE
