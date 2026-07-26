"""Load the official source registry from local YAML."""

from pathlib import Path

import yaml
from pydantic import ValidationError

from visa_assist.schemas import SourceRegistry


DEFAULT_SOURCE_REGISTRY_PATH = (
    Path(__file__).resolve().parents[2] / "config" / "sources.yaml"
)


class SourceRegistryError(ValueError):
    """Raised when a source registry cannot be parsed or validated."""


def load_source_registry(
    path: Path | str = DEFAULT_SOURCE_REGISTRY_PATH,
) -> SourceRegistry:
    """Read and validate a source registry from a local YAML file."""
    registry_path = Path(path)

    try:
        raw_registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise SourceRegistryError(
            f"Unable to read source registry: {registry_path}"
        ) from exc

    try:
        return SourceRegistry.model_validate(raw_registry)
    except ValidationError as exc:
        raise SourceRegistryError(
            f"Invalid source registry: {registry_path}"
        ) from exc
