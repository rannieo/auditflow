"""Application settings loaded from environment / .env."""

import logging
from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

log = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Typed settings — instances are created via get_settings()."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_env: str = Field(default="development")
    database_url: str = Field(default="sqlite:///./auditflow.db")
    # NoDecode tells DotEnvSettingsSource not to JSON-decode the raw string;
    # _split_cors_origins below turns "a,b,c" into ["a", "b", "c"].
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:5173"]
    )

    # AI provider selection — "mock" | "ollama"
    ai_provider: str = Field(default="mock")
    openai_api_key: str = Field(default="")
    anthropic_api_key: str = Field(default="")

    # Ollama Cloud — see docs.ollama.com/cloud. The :120b-cloud tag is what
    # this project uses; the official docs note that tag is also for local
    # Ollama clients offloading to cloud, but the cloud /api/chat endpoint
    # accepts it directly.
    ollama_api_key: str = Field(default="")
    ollama_base_url: str = Field(default="https://ollama.com")
    ollama_model: str = Field(default="gpt-oss:120b-cloud")
    ollama_timeout_seconds: float = Field(default=30.0)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @model_validator(mode="after")
    def _downgrade_ollama_without_key(self) -> "Settings":
        """If ollama is requested but no key is set, silently fall back to mock."""
        if self.ai_provider == "ollama" and not self.ollama_api_key:
            log.warning(
                "ai_provider=ollama but OLLAMA_API_KEY is empty; "
                "downgrading to mock provider."
            )
            object.__setattr__(self, "ai_provider", "mock")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
