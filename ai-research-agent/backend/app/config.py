"""Typed application configuration loaded from environment / .env."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str = ""
    brave_api_key: str = ""
    database_url: str = "postgresql+asyncpg://user:pass@localhost/research"
    langsmith_api_key: str = ""
    langsmith_tracing: bool = True
    model_name: str = "claude-sonnet-4-20250514"
    allowed_origins: str = "http://localhost:5173"


@lru_cache
def get_settings() -> Settings:
    return Settings()
