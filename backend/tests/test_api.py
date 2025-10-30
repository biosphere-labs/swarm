"""
Tests for the FastAPI application endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from decomposition_pipeline.api.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


def test_root_endpoint(client):
    """Test the root endpoint returns API information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "status" in data
    assert data["status"] == "running"


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "version" in data


def test_api_status(client):
    """Test the API status endpoint returns configuration."""
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert "api_version" in data
    assert "llm_provider" in data
    assert "model" in data
    assert "approval_gates" in data
    assert "limits" in data

    # Check approval gates structure
    gates = data["approval_gates"]
    assert "paradigm" in gates
    assert "technique" in gates
    assert "decomposition" in gates
    assert "solution" in gates

    # Check limits structure
    limits = data["limits"]
    assert "max_concurrent_agents" in limits
    assert "recursion_limit" in limits
    assert "agent_timeout" in limits
