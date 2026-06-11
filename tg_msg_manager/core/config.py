import json
import os
import logging
from typing import Set, Optional, Any
from pydantic import Field, AliasChoices, field_validator
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    PydanticBaseSettingsSource,
)

logger = logging.getLogger(__name__)
SUPPORTED_LANGS = {"ru", "en"}
DEFAULT_CONFIG = {
    "api_id": 0,
    "api_hash": "",
    "session_name": "tg_msg_manager",
    "db_path": "messages.db",
    "account_name": "Default Account",
    "whitelist_chats": [],
    "include_chats": [],
    "chats_to_search_user_msgs": [],
    "max_rps": 3.0,
    "log_level": "INFO",
    "lang": "ru",
}


class ConfigurationSetupRequired(ValueError):
    pass


class Settings(BaseSettings):
    """
    Application settings with Pydantic validation and ENV override support.
    """

    model_config = SettingsConfigDict(
        env_prefix="TG_", env_file=".env", extra="ignore", populate_by_name=True
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        from pydantic_settings import JsonConfigSettingsSource

        return (
            init_settings,
            env_settings,
            JsonConfigSettingsSource(settings_cls),
            dotenv_settings,
            file_secret_settings,
        )

    api_id: int
    api_hash: str
    session_name: str = "tg_msg_manager"

    # Storage
    db_path: str = "messages.db"

    account_name: str = "Default Account"

    # Whitelist of chat IDs or usernames that should NEVER be cleaned
    # Supports 'exclude_chats' from legacy config
    whitelist_chats: Set[Any] = Field(
        default_factory=set,
        validation_alias=AliasChoices("whitelist_chats", "exclude_chats"),
    )

    # Optional list of chats to ONLY clean (if not empty)
    include_chats: Set[Any] = Field(default_factory=set)

    # Chats to search for user messages by default if --chat-id is missing
    chats_to_search_user_msgs: Set[Any] = Field(default_factory=set)

    # Throttling
    max_rps: float = 3.0

    # Observability
    log_level: str = "INFO"

    # UI / localization
    lang: str = Field(
        default="ru",
        validation_alias=AliasChoices("lang", "language", "ui_language"),
    )

    @field_validator("api_id", mode="before")
    @classmethod
    def validate_api_id(cls, v):
        if v is None:
            raise ValueError("api_id is required")
        return int(v)

    @field_validator(
        "whitelist_chats", "chats_to_search_user_msgs", "include_chats", mode="before"
    )
    @classmethod
    def normalize_ids(cls, v):
        if isinstance(v, str):
            v = {s.strip() for s in v.split(",") if s.strip()}

        if isinstance(v, (list, set)):
            normalized = set()
            for item in v:
                if item is None:
                    continue
                try:
                    # Convert to int if it's a numeric string or integer
                    normalized.add(int(item))
                except (ValueError, TypeError):
                    # Keep as string if it's a username or similar
                    normalized.add(str(item))
            return normalized
        return v

    @field_validator("lang", mode="before")
    @classmethod
    def normalize_lang(cls, v):
        if v is None:
            return "ru"
        lang = str(v).strip().lower()
        if lang in SUPPORTED_LANGS:
            return lang
        return "ru"


def _resolve_config_value(field_name: str, config_data: dict[str, Any]) -> Any:
    if field_name in config_data:
        return config_data[field_name]

    field_info = Settings.model_fields.get(field_name)
    if field_info is None:
        return None

    validation_alias = field_info.validation_alias
    if isinstance(validation_alias, AliasChoices):
        for choice in validation_alias.choices:
            if isinstance(choice, str) and choice in config_data:
                return config_data[choice]
    elif isinstance(validation_alias, str) and validation_alias in config_data:
        return config_data[validation_alias]

    return None


def _normalized_config_data(config_data: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for field_name in Settings.model_fields:
        value = _resolve_config_value(field_name, config_data)
        if value is not None:
            normalized[field_name] = value
    return normalized


def _config_settings_kwargs(config_data: dict[str, Any]) -> dict[str, Any]:
    settings_kwargs: dict[str, Any] = {}
    for key, value in config_data.items():
        env_key = f"TG_{key.upper()}"
        if env_key not in os.environ:
            settings_kwargs[key] = value
    return settings_kwargs


def ensure_default_config(config_path: str) -> bool:
    """Create a safe first-run config without overwriting an existing file."""
    os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)
    try:
        with open(config_path, "x", encoding="utf-8") as config_file:
            json.dump(DEFAULT_CONFIG, config_file, ensure_ascii=False, indent=2)
            config_file.write("\n")
        return True
    except FileExistsError:
        return False


def _require_configured_api_credentials(
    settings: Settings,
    config_path: Optional[str],
) -> None:
    if settings.api_id > 0 and settings.api_hash.strip() not in ("", "YOUR_API_HASH"):
        return
    location = config_path or "config.json"
    raise ConfigurationSetupRequired(
        f"Telegram API credentials are not configured. Edit {location} "
        "and set api_id and api_hash."
    )


def load_settings(
    config_path: Optional[str] = None,
    *,
    require_api_credentials: bool = True,
) -> Settings:
    """
    Loads settings from config.json (if exists) and overrides with ENV.
    """
    # Pydantic Settings handles the loading logic
    # To support config.json explicitly if needed:
    try:
        if config_path and os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = _normalized_config_data(json.load(f))
            settings_kwargs = _config_settings_kwargs(config_data)
            if not require_api_credentials:
                if "api_id" not in config_data and "TG_API_ID" not in os.environ:
                    settings_kwargs["api_id"] = 0
                if "api_hash" not in config_data and "TG_API_HASH" not in os.environ:
                    settings_kwargs["api_hash"] = ""
            settings = Settings(**settings_kwargs)
            if require_api_credentials:
                _require_configured_api_credentials(settings, config_path)
            return settings
        if not require_api_credentials:
            settings_kwargs = {}
            if "TG_API_ID" not in os.environ:
                settings_kwargs["api_id"] = 0
            if "TG_API_HASH" not in os.environ:
                settings_kwargs["api_hash"] = ""
            return Settings(**settings_kwargs)
        settings = Settings()
        _require_configured_api_credentials(settings, config_path)
        return settings
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        raise
