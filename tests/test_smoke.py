"""Smoke tests for the initial project scaffold."""

import importlib.util
from pathlib import Path
from types import ModuleType


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path) -> ModuleType:
    """Load a module directly from a project file."""
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_project_modules_load() -> None:
    """Verify that the initial modules import and the entry point responds."""
    app = load_module("app", PROJECT_ROOT / "app.py")
    config = load_module("config", PROJECT_ROOT / "src/visa_assist/config.py")
    schemas = load_module("schemas", PROJECT_ROOT / "src/visa_assist/schemas.py")

    assert app.main() == "visa-assist is ready"
    assert config.__name__ == "config"
    assert schemas.__name__ == "schemas"
