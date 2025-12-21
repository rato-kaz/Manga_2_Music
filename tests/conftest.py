"""
Pytest configuration and fixtures.

This file provides shared fixtures for all tests.
"""

import pytest
from pathlib import Path
from src.infrastructure.logging_config import setup_logging


@pytest.fixture(scope="session", autouse=True)
def setup_test_logging() -> None:
    """Setup logging for tests."""
    setup_logging(log_level="WARNING")  # Reduce noise in tests


@pytest.fixture
def sample_image_path(tmp_path: Path) -> Path:
    """Create a sample image file for testing."""
    # In real tests, you would create an actual image file
    # For now, return a path (tests would need to create actual file)
    return tmp_path / "test_image.jpg"


@pytest.fixture
def test_output_dir(tmp_path: Path) -> Path:
    """Create a test output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True)
    return output_dir

