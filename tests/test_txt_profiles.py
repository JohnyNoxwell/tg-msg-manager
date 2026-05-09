import pytest

from tg_msg_manager.services.rendering import (
    DEFAULT_TXT_PROFILE,
    TXT_PROFILE_CONTEXT_READABLE,
    TXT_PROFILE_LEGACY,
    validate_txt_profile,
)


def test_default_txt_profile_is_context_readable():
    assert DEFAULT_TXT_PROFILE == TXT_PROFILE_CONTEXT_READABLE


def test_validate_txt_profile_accepts_known_profiles():
    assert validate_txt_profile("context-readable") == TXT_PROFILE_CONTEXT_READABLE
    assert validate_txt_profile("legacy") == TXT_PROFILE_LEGACY


def test_validate_txt_profile_uses_default_for_empty_values():
    assert validate_txt_profile(None) == TXT_PROFILE_CONTEXT_READABLE
    assert validate_txt_profile("") == TXT_PROFILE_CONTEXT_READABLE


def test_validate_txt_profile_rejects_unknown_values():
    with pytest.raises(ValueError):
        validate_txt_profile("compact")
