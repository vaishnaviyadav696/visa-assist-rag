"""Unit tests for application configuration."""

import sys
from pathlib import Path

import pytest
from pydantic import ValidationError


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from visa_assist.config import Settings  # noqa: E402


def test_settings_defaults() -> None:
    """Settings provide safe local defaults when no .env file exists."""
    settings = Settings(_env_file=None)

    assert settings.llm_provider == "gemini"
    assert settings.gemini_api_key is None
    assert settings.embedding_model == "sentence-transformers/all-MiniLM-L6-v2"
    assert settings.top_k == 5
    assert settings.minimum_retrieval_score == 0.5
    assert settings.source_data_dir == Path("data/source")
    assert settings.index_data_dir == Path("data/index")


def test_settings_load_dotenv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Settings load and convert values from a local .env file."""
    (tmp_path / ".env").write_text(
        "\n".join(
            (
                "LLM_PROVIDER=ollama",
                "GEMINI_API_KEY=test-key",
                "EMBEDDING_MODEL=example/model",
                "TOP_K=8",
                "MINIMUM_RETRIEVAL_SCORE=0.7",
                "SOURCE_DATA_DIR=fixtures/source",
                "INDEX_DATA_DIR=fixtures/index",
            )
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    settings = Settings()

    assert settings.llm_provider == "ollama"
    assert settings.gemini_api_key is not None
    assert settings.gemini_api_key.get_secret_value() == "test-key"
    assert settings.embedding_model == "example/model"
    assert settings.top_k == 8
    assert settings.minimum_retrieval_score == 0.7
    assert settings.source_data_dir == Path("fixtures/source")
    assert settings.index_data_dir == Path("fixtures/index")


@pytest.mark.parametrize(
    ("name", "value"),
    (("TOP_K", "0"), ("MINIMUM_RETRIEVAL_SCORE", "1.1")),
)
def test_settings_reject_invalid_retrieval_values(
    monkeypatch: pytest.MonkeyPatch,
    name: str,
    value: str,
) -> None:
    """Retrieval settings reject values outside their supported ranges."""
    monkeypatch.setenv(name, value)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)
