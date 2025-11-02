# finance_ai/core/settings.py
from __future__ import annotations

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # App
    APP_NAME: str = "Finance AI"
    ENV: str = "dev"
    DATABASE_URL: str = "sqlite:///./app.db"

    # Secrets
    # If JWT_SECRET_KEY is not set, fallback to SECRET_KEY.
    SECRET_KEY: str = Field(default="change-me-please", validation_alias=AliasChoices("SECRET_KEY"))
    JWT_SECRET_KEY: str = Field(
        default="change-me-please",
        validation_alias=AliasChoices("JWT_SECRET_KEY", "SECRET_KEY"),
    )

    # JWT config
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # CORS
    CORS_ORIGINS: str = ""


settings = Settings()