"""Smoke test for the minimal application scaffold."""

from app import main
from visa_assist import config, schemas


def test_project_scaffold_loads() -> None:
    """Verify that the entry point and placeholder modules load."""
    assert main() == "visa-assist is ready"
    assert config.__name__ == "visa_assist.config"
    assert schemas.__name__ == "visa_assist.schemas"
