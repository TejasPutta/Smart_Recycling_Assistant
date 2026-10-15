"""
Application configuration.

Loads environment-based settings using pydantic-settings.
Secrets (Gemini API key, etc.) are declared here but must be supplied
via the `.env` file or real environment variables — never hardcoded.
"""

from functools import lru_cache
from typing import List

from pydantic import Field
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
    # Stored as a comma-separated string; access via `.cors_origins` property.
    cors_origins_raw: str = Field(
        default=(
            "http://localhost:5173,http://localhost:3000,"
            "http://127.0.0.1:5173,http://127.0.0.1:3000"
        ),
        alias="CORS_ORIGINS",
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
    allowed_image_types_raw: str = Field(
        default="image/jpeg,image/png,image/webp",
        alias="ALLOWED_IMAGE_TYPES",
    )

    # ---------- Convenience properties ----------
    @property
    def cors_origins(self) -> List[str]:
        """Return CORS origins as a clean list of strings."""
        return [item.strip() for item in self.cors_origins_raw.split(",") if item.strip()]

    @property
    def allowed_image_types(self) -> List[str]:
        """Return allowed MIME types as a clean list of strings."""
        return [
            item.strip()
            for item in self.allowed_image_types_raw.split(",")
            if item.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (import-safe, test-friendly)."""
    return Settings()