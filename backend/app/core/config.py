"""Application settings, sourced from environment.

Uses pydantic-settings so every var is typed and validated at startup —
the app refuses to boot with a missing secret rather than crashing on first request.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Runtime
    env: Literal["dev", "staging", "prod"] = "dev"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    # Auth
    jwt_secret: str = Field(..., min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Database
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "careerforge"

    # CORS — store as plain string, parsed on access
    allowed_origins_str: str = Field("http://localhost:3000", alias="ALLOWED_ORIGINS")

    @property
    def allowed_origins(self) -> list[str]:
        v = self.allowed_origins_str.strip()
        # Handle JSON array format: ["http://localhost:3000","https://..."]
        if v.startswith("["):
            import json
            try:
                return [str(o).strip() for o in json.loads(v) if str(o).strip()]
            except json.JSONDecodeError:
                pass
        # Plain comma-separated: http://localhost:3000,https://...
        return [o.strip() for o in v.split(",") if o.strip()]

    # AI providers
    mistral_api_key: str | None = None
    groq_api_key: str | None = None
    sbert_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Uploads
    max_upload_mb: int = 5
    upload_dir: str = "./uploads"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
