from typing import Iterable

from .context_readable_txt_renderer import ContextReadableTxtRenderer
from .legacy_txt_renderer import LegacyTxtRenderer
from .models import TxtRenderOptions
from .txt_profiles import (
    TXT_PROFILE_CONTEXT_READABLE,
    TXT_PROFILE_LEGACY,
    validate_txt_profile,
)


def render_txt_records(records: Iterable[object], options: TxtRenderOptions) -> str:
    profile = validate_txt_profile(options.profile)
    normalized_options = TxtRenderOptions(
        profile=profile,
        target_user_id=options.target_user_id,
        target_author_name=options.target_author_name,
        chat_id=options.chat_id,
        chat_title=options.chat_title,
        include_ids=options.include_ids,
        max_reply_excerpt_chars=options.max_reply_excerpt_chars,
    )
    if profile == TXT_PROFILE_LEGACY:
        return LegacyTxtRenderer().render(records, normalized_options)
    if profile == TXT_PROFILE_CONTEXT_READABLE:
        return ContextReadableTxtRenderer().render(records, normalized_options)
    raise ValueError(f"Unknown TXT profile: {profile!r}")


def render_txt(records: Iterable[object], options: TxtRenderOptions) -> str:
    return render_txt_records(records, options)
