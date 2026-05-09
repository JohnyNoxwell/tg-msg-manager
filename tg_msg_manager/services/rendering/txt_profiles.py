TXT_PROFILE_CONTEXT_READABLE = "context-readable"
TXT_PROFILE_LEGACY = "legacy"
DEFAULT_TXT_PROFILE = TXT_PROFILE_CONTEXT_READABLE

ALLOWED_TXT_PROFILES = frozenset(
    {
        TXT_PROFILE_CONTEXT_READABLE,
        TXT_PROFILE_LEGACY,
    }
)


def validate_txt_profile(value: str | None) -> str:
    if value is None:
        return DEFAULT_TXT_PROFILE

    normalized = str(value).strip()
    if not normalized:
        return DEFAULT_TXT_PROFILE
    if normalized not in ALLOWED_TXT_PROFILES:
        allowed = ", ".join(sorted(ALLOWED_TXT_PROFILES))
        raise ValueError(f"Unknown TXT profile: {value!r}. Allowed values: {allowed}")
    return normalized
