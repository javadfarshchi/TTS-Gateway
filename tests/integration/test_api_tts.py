"""API tests for the TTS service."""
import pytest
from fastapi.testclient import TestClient

from tts_gateway.app import create_app


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app with a fresh app instance."""
    test_app = create_app()
    return TestClient(test_app)


def test_health_check(test_client):
    """Test the health check endpoint."""
    response = test_client.get("/api/v1/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_tts_endpoint(test_client):
    """Test the TTS synthesis endpoint."""
    test_text = "This is a test of the TTS service."

    response = test_client.post(
        "/api/v1/tts?provider=mock",
        json={
            "text": test_text,
            "voice": "test-voice",
            "lang": "en",
            "speed": 1.0,
            "pitch": 0.0,
            "fmt": "wav",
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/wav"
    assert len(response.content) > 0


def test_tts_endpoint_validation(test_client):
    """Test request validation in the TTS endpoint."""
    # Test missing required field
    response = test_client.post("/api/v1/tts", json={"provider": "mock"})  # Missing 'text' field
    assert response.status_code == 422  # Validation error

    # Test invalid speed value
    response = test_client.post(
        "/api/v1/tts", json={"text": "Test", "speed": 3.0}  # Above maximum allowed value of 2.0
    )
    assert response.status_code == 422

    # Test invalid format
    response = test_client.post("/api/v1/tts", json={"text": "Test", "fmt": "invalid-format"})
    assert response.status_code == 422


def test_unknown_provider(test_client):
    """Test error handling for unknown TTS providers."""
    response = test_client.post("/api/v1/tts?provider=nonexistent-provider", json={"text": "Test"})

    assert response.status_code == 400
    assert "not found" in response.json()["detail"].lower()
