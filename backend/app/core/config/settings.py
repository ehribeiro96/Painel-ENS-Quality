from __future__ import annotations

import os
from functools import lru_cache
from typing import Annotated, Literal

from pydantic import AliasChoices, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


def _is_weak_jwt_secret(secret: str) -> bool:
    normalized = secret.strip()
    if not normalized:
        return True
    lowered = normalized.lower()
    if lowered == "change-me" or "change-me" in lowered:
        return True
    if "placeholder" in lowered:
        return True
    if normalized.startswith("<") and normalized.endswith(">"):
        return True
    return len(normalized) < 32


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", populate_by_name=True)

    app_name: str = "ENS ITAM Platform"
    environment: Literal["local", "staging", "production"] = "local"
    api_prefix: str = "/api/v1"
    database_url: str = "postgresql+asyncpg://itam:itam@localhost:5432/itam"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret_key: str = Field(min_length=32, default="change-me-with-at-least-32-characters")
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 15
    refresh_token_days: int = 7
    refresh_cookie_name: str = "ens_itam_refresh"
    refresh_cookie_secure: bool = False
    refresh_cookie_samesite: Literal["lax", "strict", "none"] = "lax"
    allowed_origins: Annotated[list[str], NoDecode] = []
    upload_max_mb: int = 25
    import_max_rows: int = 10000
    app_startup_checks: bool = True
    app_auto_migrate: bool = False
    app_startup_step_timeout_seconds: float = 15.0
    dependency_retry_attempts: int = 30
    dependency_retry_delay_seconds: float = 2.0
    admin_email: str | None = None
    admin_password: str | None = None
    admin_name: str = "ITAM Admin"
    rate_limit_per_minute: int = 240
    auth_rate_limit_per_minute: int = 20
    session_timeout_minutes: int = 8 * 60
    frontend_static: str | None = None
    frontend_dist: str | None = None
    enable_ai_chat: bool = False
    ai_provider: Literal["mock", "gemini", "openai", "ollama", "ollama-lan", "hermes"] = Field(
        default="mock",
        validation_alias=AliasChoices("ai_provider", "AI_CHAT_PROVIDER", "AI_PROVIDER"),
    )
    ai_chat_default_provider: Literal["mock", "ollama", "hermes"] = Field(
        default="mock",
        validation_alias=AliasChoices("ai_chat_default_provider", "AI_CHAT_DEFAULT_PROVIDER"),
    )
    ai_model: str = ""
    ai_gemini_api_key: str = ""
    ai_openai_api_key: str = ""
    ai_timeout_seconds: int = 30
    ai_max_input_chars: int = 12000
    ai_max_output_tokens: int = 1000
    ai_chat_rate_limit_per_minute: int = 20
    metrics_token: str = Field(default="", validation_alias=AliasChoices("METRICS_TOKEN"))
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen3:1.7b-64k"
    ollama_timeout_seconds: int = 120
    ollama_allowed_hosts: Annotated[list[str], NoDecode] = ["localhost", "127.0.0.1", "::1"]
    hermes_base_url: str = ""
    hermes_model: str = "hermes-agent"

    @property
    def openai_api_key(self) -> str:
        """Backward-compatible runtime accessor for the Painel OpenAI key.

        Contract: the Painel reads AI_OPENAI_API_KEY. OPENAI_API_KEY may be
        present for Hermes/Codex/external SDKs only and is bridged in memory by
        validate_ai_openai_key_bridge when AI_OPENAI_API_KEY is absent.
        """

        return self.ai_openai_api_key

    @field_validator("allowed_origins", "ollama_allowed_hosts", mode="before")
    @classmethod
    def parse_csv_list(cls, value: str | list[str] | None) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_ai_chat_provider_alias(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        legacy_provider = (os.environ.get("AI_CHAT_PROVIDER") or "").strip().lower()
        if legacy_provider and legacy_provider in {"mock", "ollama", "ollama-lan", "hermes"}:
            current = str(data.get("ai_provider") or "").strip().lower()
            if not current or current == "mock":
                normalized = dict(data)
                normalized["ai_provider"] = legacy_provider
                return normalized
        return data

    @model_validator(mode="after")
    def validate_production_security(self) -> Settings:
        if not self.ai_openai_api_key.strip():
            # Temporary process-memory bridge only. This does not write .env,
            # docker-compose or logs, and intentionally does not expose values.
            external_openai_key = os.environ.get("OPENAI_API_KEY", "")
            if external_openai_key.strip():
                self.ai_openai_api_key = external_openai_key
        if self.environment == "local":
            # Local developer instances should expose AI Chat unless it is explicitly disabled
            # by a runtime configuration override.
            if "enable_ai_chat" not in self.model_fields_set:
                self.enable_ai_chat = True
            self.app_auto_migrate = True
        elif _is_weak_jwt_secret(self.jwt_secret_key):
            raise ValueError("JWT_SECRET_KEY must be changed outside local")
        if self.environment == "production" and self.admin_password == "<DEFINIR_LOCALMENTE_NO_ENV>":
            raise ValueError("ADMIN_PASSWORD must be changed in production")
        if self.refresh_cookie_samesite == "none" and not self.refresh_cookie_secure:
            raise ValueError("REFRESH_COOKIE_SECURE=true is required when REFRESH_COOKIE_SAMESITE=none")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
