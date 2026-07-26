"""Validated environment-backed application configuration."""

from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings loaded from environment variables and a local `.env` file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    environment: Literal["development", "test", "production"] = "development"
    database_url: str = Field(
        default="sqlite:///data/synthetic/visa_assist.db",
        min_length=1,
    )
    llm_provider: str = Field(default="gemini", min_length=1)
    gemini_api_key: SecretStr | None = None
    gemini_model: str = Field(default="gemini-2.5-flash", min_length=1)
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        min_length=1,
    )
    vector_index_dir: Path = Path("data/index")
    vector_manifest_path: Path = Path("data/index/manifest.json")
    retrieval_top_k: int = Field(default=5, ge=1)
    retrieval_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    synthetic_data_seed: int = Field(default=42, ge=0)
    logging_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    @field_validator("logging_level", mode="before")
    @classmethod
    def normalize_logging_level(cls, value: object) -> object:
        """Accept conventional case-insensitive logging level values."""
        return value.upper() if isinstance(value, str) else value
