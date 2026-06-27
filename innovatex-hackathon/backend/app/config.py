from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),  # try backend/.env first, then repo-root/.env
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    APP_NAME: str = "Diagnóstico Ley 1581 de 2012"
    API_V1_PREFIX: str = "/api"
    APP_VERSION: str = "0.1.0"

    # Database — Supabase managed PostgreSQL (Path B)
    # Direct connection (for Alembic DDL / migrations):
    DATABASE_URL: str = ""
    # Pooler connection (for FastAPI runtime — PgBouncer, many short-lived connections):
    DATABASE_URL_POOLER: str = ""

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_JWKS_URL: str = ""
    SUPABASE_JWT_SECRET: str = ""  # used only if HS256; ignored for ES256 (JWKS)
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost"]

    # Frontend
    FRONTEND_URL: str = "http://localhost:5173"

    # AI (placeholder)
    AI_PROVIDER: str = "mock"
    OPENAI_API_KEY: SecretStr = SecretStr("")
    ANTHROPIC_API_KEY: SecretStr = SecretStr("")
    GEMINI_API_KEY: SecretStr = SecretStr("")

    # AI (Phase 5) — extended
    AI_FALLBACK_PROVIDERS: list[str] = []
    AI_TIMEOUT_SECONDS: int = 5
    AI_MOCK_ENABLED: bool = True


settings = Settings()
