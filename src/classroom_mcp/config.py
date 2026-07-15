"""Settings — pydantic-settings with .env support."""

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
    learnbot_url: str = Field(default="http://127.0.0.1:11104", alias="LEARNBOT_URL")


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
