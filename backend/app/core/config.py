"""
Application configuration.

Loads environment-based settings using pydantic-settings.
Secrets (Gemini API key, etc.) are declared here but must be supplied
via the `.env` file or real environment variables — never hardcoded.
"""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---------- Application ----------
    app_name: str = Field(default="Smart Recycling Assistant API")
    app_version: str = Field(default="0.1.0")
    app_env: str = Field(default="development")
    debug: bool = Field(default=True)
    api_v1_prefix: str = Field(default="/api/v1")

    # ---------- Server ----------
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8000)

    # ---------- CORS ----------
    cors_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
        ]
    )

    # ---------- Database (used from Stage 5) ----------
    database_url: str = Field(default="sqlite:///./smart_recycling.db")

    # ---------- Google Gemini (used from Stage 4) ----------
    gemini_api_key: str = Field(default="")
    gemini_model: str = Field(default="gemini-2.0-flash")

    # ---------- AI model (used from Stage 2) ----------
    classification_model_path: str = Field(default="")
    classification_model_enabled: bool = Field(default=False)

    # ---------- Uploads (used from Stage 3) ----------
    max_upload_size_mb: int = Field(default=8)
    allowed_image_types: List[str] = Field(
        default_factory=lambda: ["image/jpeg", "image/png", "image/webp"]
    )

    # ---------- Validators ----------
    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors_origins(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("allowed_image_types", mode="before")
    @classmethod
    def _split_allowed_types(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (import-safe, test-friendly)."""
    return Settings()