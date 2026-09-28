"""Settings - pydantic-settings with .env support."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    server_name: str = "classroom-mcp"
    backend_port: int = Field(default=11105, alias="BACKEND_PORT")
    frontend_port: int = Field(default=11106, alias="FRONTEND_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    db_path: str = Field(default="data/classroom.db", alias="DB_PATH")
    api_key: str = Field(default="", alias="CLASSROOM_API_KEY")
    learnbot_url: str = Field(default="http://127.0.0.1:11101", alias="LEARNBOT_URL")


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def clear_settings_cache() -> None:
    """Force the next get_settings() call to re-read env vars.

    The `from classroom_mcp.config import _settings; _settings = None` pattern
    does NOT do this - that rebinds a local name, not this module's global.
    Tests must call this function instead.
    """
    global _settings
    _settings = None
