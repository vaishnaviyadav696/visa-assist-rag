"""Environment-backed application configuration."""

from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration loaded from environment variables and a local .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    llm_provider: str = "gemini"
    gemini_api_key: SecretStr | None = None
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    top_k: int = Field(default=5, ge=1)
    minimum_retrieval_score: float = Field(default=0.5, ge=0.0, le=1.0)
    source_data_dir: Path = Path("data/source")
    index_data_dir: Path = Path("data/index")
