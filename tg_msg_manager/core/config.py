import os
import logging
from typing import Set, Optional, Any
from pydantic import Field, AliasChoices, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """
    Application settings with Pydantic validation and ENV override support.
    """
    model_config = SettingsConfigDict(
        env_prefix="TG_", 
        env_file=".env",
        extra="ignore",
        populate_by_name=True
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
        validation_alias=AliasChoices("whitelist_chats", "exclude_chats")
    )

    # Optional list of chats to ONLY clean (if not empty)
    include_chats: Set[Any] = Field(default_factory=set)
    
    # Chats to search for user messages by default if --chat-id is missing
    chats_to_search_user_msgs: Set[Any] = Field(default_factory=set)
    
    # Throttling
    max_rps: float = 3.0
    
    # Observability
    log_level: str = "INFO"

    @field_validator("api_id", mode="before")
    @classmethod
    def validate_api_id(cls, v):
        if v is None:
            raise ValueError("api_id is required")
        return int(v)

    @field_validator("whitelist_chats", "chats_to_search_user_msgs", "include_chats", mode="before")
    @classmethod
    def normalize_ids(cls, v):
        if isinstance(v, str):
            v = {s.strip() for s in v.split(",") if s.strip()}
        
        if isinstance(v, (list, set)):
            normalized = set()
            for item in v:
                if item is None: continue
                try:
                    # Convert to int if it's a numeric string or integer
                    normalized.add(int(item))
                except (ValueError, TypeError):
                    # Keep as string if it's a username or similar
                    normalized.add(str(item))
            return normalized
        return v

def load_settings(config_path: Optional[str] = None) -> Settings:
    """
    Loads settings from config.json (if exists) and overrides with ENV.
    """
    # Pydantic Settings handles the loading logic
    # To support config.json explicitly if needed:
    try:
        if config_path and os.path.exists(config_path):
            import json
            config_data = json.loads(open(config_path, "r").read())
            synthetic_env: list[str] = []
            for key, value in config_data.items():
                env_key = f"TG_{key.upper()}"
                if env_key in os.environ:
                    continue
                if isinstance(value, (list, set, tuple, dict)):
                    import json
                    env_value = json.dumps(list(value) if isinstance(value, set) else value)
                else:
                    env_value = str(value)
                os.environ[env_key] = env_value
                synthetic_env.append(env_key)
            try:
                return Settings()
            finally:
                for key in synthetic_env:
                    os.environ.pop(key, None)
        return Settings()
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        raise

# Global settings instance
settings = load_settings("config.json")
