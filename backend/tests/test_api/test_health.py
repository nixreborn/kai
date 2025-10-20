"""Tests for Health Check API endpoint."""

import pytest
from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


class TestHealthAPI:
    """Test suite for Health Check API."""

    def test_health_check_returns_200(self) -> None:
        """Test that health check endpoint returns 200."""
        response = client.get("/health")

        assert response.status_code == 200

    def test_health_check_returns_correct_structure(self) -> None:
        """Test that health check returns expected JSON structure."""
        response = client.get("/health")

        data = response.json()
        assert "status" in data
        assert "version" in data

    def test_health_check_status_is_healthy(self) -> None:
        """Test that health check reports healthy status."""
        response = client.get("/health")

        data = response.json()
        assert data["status"] == "healthy"

    def test_health_check_version_format(self) -> None:
        """Test that version is in expected format."""
        response = client.get("/health")

        data = response.json()
        assert data["version"] == "0.1.0"

    def test_health_check_response_time(self) -> None:
        """Test that health check responds quickly."""
        import time

        start = time.time()
        response = client.get("/health")
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 0.1  # Should respond in less than 100ms

    def test_root_endpoint(self) -> None:
        """Test root endpoint returns API information."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data

    def test_root_endpoint_includes_docs_link(self) -> None:
        """Test that root endpoint includes link to docs."""
        response = client.get("/")

        data = response.json()
        assert data["docs"] == "/docs"

    def test_docs_endpoint_accessible(self) -> None:
        """Test that API documentation is accessible."""
        response = client.get("/docs")

        assert response.status_code == 200

    def test_openapi_json_accessible(self) -> None:
        """Test that OpenAPI spec is accessible."""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
