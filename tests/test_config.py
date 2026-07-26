"""Tests for environment-backed application configuration."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from visa_assist.config import Settings

SETTING_NAMES = (
    "ENVIRONMENT",
    "DATABASE_URL",
    "LLM_PROVIDER",
    "GEMINI_API_KEY",
    "GEMINI_MODEL",
    "EMBEDDING_MODEL",
    "VECTOR_INDEX_DIR",
    "VECTOR_MANIFEST_PATH",
    "RETRIEVAL_TOP_K",
    "RETRIEVAL_THRESHOLD",
    "SYNTHETIC_DATA_SEED",
    "LOGGING_LEVEL",
)


@pytest.fixture(autouse=True)
def clear_settings_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep configuration tests independent from the host environment."""
    for name in SETTING_NAMES:
        monkeypatch.delenv(name, raising=False)


def test_settings_defaults() -> None:
    """Settings provide deterministic local-development defaults."""
    settings = Settings(_env_file=None)

    assert settings.environment == "development"
    assert settings.database_url == "sqlite:///data/synthetic/visa_assist.db"
    assert settings.llm_provider == "gemini"
    assert settings.gemini_api_key is None
    assert settings.gemini_model == "gemini-2.5-flash"
    assert settings.embedding_model == "sentence-transformers/all-MiniLM-L6-v2"
    assert settings.vector_index_dir == Path("data/index")
    assert settings.vector_manifest_path == Path("data/index/manifest.json")
    assert settings.retrieval_top_k == 5
    assert settings.retrieval_threshold == 0.5
    assert settings.synthetic_data_seed == 42
    assert settings.logging_level == "INFO"


def test_settings_load_dotenv(tmp_path: Path) -> None:
    """Values from a dotenv file are parsed into their declared types."""
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            (
                "ENVIRONMENT=test",
                "DATABASE_URL=sqlite:///test.db",
                "LLM_PROVIDER=gemini",
                "GEMINI_API_KEY=demo-key",
                "GEMINI_MODEL=demo-model",
                "EMBEDDING_MODEL=demo-embedding",
                "VECTOR_INDEX_DIR=tmp/index",
                "VECTOR_MANIFEST_PATH=tmp/index/manifest.json",
                "RETRIEVAL_TOP_K=8",
                "RETRIEVAL_THRESHOLD=0.7",
                "SYNTHETIC_DATA_SEED=99",
                "LOGGING_LEVEL=debug",
            )
        ),
        encoding="utf-8",
    )

    settings = Settings(_env_file=env_file)

    assert settings.environment == "test"
    assert settings.database_url == "sqlite:///test.db"
    assert settings.gemini_api_key is not None
    assert settings.gemini_api_key.get_secret_value() == "demo-key"
    assert settings.vector_index_dir == Path("tmp/index")
    assert settings.retrieval_top_k == 8
    assert settings.retrieval_threshold == 0.7
    assert settings.synthetic_data_seed == 99
    assert settings.logging_level == "DEBUG"


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("retrieval_top_k", 0),
        ("retrieval_threshold", -0.1),
        ("retrieval_threshold", 1.1),
        ("synthetic_data_seed", -1),
        ("logging_level", "TRACE"),
    ),
)
def test_settings_reject_invalid_values(field: str, value: object) -> None:
    """Bounded numeric values and logging levels fail validation."""
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **{field: value})
