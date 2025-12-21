"""
Integration tests for API endpoints.

Example test file to demonstrate API testing.
"""

import pytest
from fastapi.testclient import TestClient
from src.presentation.api.app import app

client = TestClient(app)


def test_health_check() -> None:
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_process_chapter_validation() -> None:
    """Test chapter processing endpoint validation."""
    # Test with invalid request (missing required fields)
    response = client.post("/api/v1/processing/chapter", json={})
    assert response.status_code == 422  # Validation error


def test_process_chapter_missing_images() -> None:
    """Test chapter processing with missing image files."""
    response = client.post(
        "/api/v1/processing/chapter",
        json={
            "manga_name": "Test_Manga",
            "chapter_number": 1,
            "image_paths": ["/nonexistent/path.jpg"],
        },
    )
    # Should return validation error
    assert response.status_code in [400, 422]

