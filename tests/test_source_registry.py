"""Unit tests for the official source registry."""

import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from visa_assist.source_registry import (  # noqa: E402
    SourceRegistryError,
    load_source_registry,
)


def test_load_default_source_registry() -> None:
    """The checked-in registry contains the disabled UK placeholder."""
    registry = load_source_registry()

    assert len(registry.sources) == 1
    source = registry.sources[0]
    assert source.source_id == "uk_standard_visitor_overview"
    assert str(source.url) == "https://www.gov.uk/standard-visitor"
    assert source.destination_country == "GB"
    assert source.passport_country == "ALL"
    assert source.visa_type == "standard_visitor"
    assert source.content_type == "web_page"
    assert source.last_verified_at is None
    assert source.enabled is False


def test_load_source_registry_rejects_invalid_source(tmp_path: Path) -> None:
    """Invalid source fields produce a registry-specific error."""
    registry_path = tmp_path / "sources.yaml"
    registry_path.write_text(
        "sources:\n  - source_id: Invalid ID\n",
        encoding="utf-8",
    )

    with pytest.raises(SourceRegistryError, match="Invalid source registry"):
        load_source_registry(registry_path)


def test_load_source_registry_rejects_malformed_yaml(tmp_path: Path) -> None:
    """Malformed YAML produces a registry-specific error."""
    registry_path = tmp_path / "sources.yaml"
    registry_path.write_text("sources: [", encoding="utf-8")

    with pytest.raises(SourceRegistryError, match="Unable to read source registry"):
        load_source_registry(registry_path)
