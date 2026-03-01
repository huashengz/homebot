import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_detailed_health_check():
    """Test detailed health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "components" in response.json()


def test_list_models():
    """Test list models endpoint"""
    response = client.get("/models")
    assert response.status_code == 200
    assert "available_models" in response.json()
    assert isinstance(response.json()["available_models"], list)


def test_chat_endpoint():
    """Test chat endpoint"""
    response = client.post("/api/v1/chat/", json={"content": "Hello"})
    assert response.status_code == 200
    assert "response" in response.json()
    assert "session_id" in response.json()


def test_chat_history_endpoint():
    """Test chat history endpoint"""
    session_id = "test-session"
    response = client.get(f"/api/v1/chat/history/{session_id}")
    assert response.status_code == 200
    assert response.json()["session_id"] == session_id
    assert "messages" in response.json()


def test_voice_engines_endpoint():
    """Test voice engines endpoint"""
    response = client.get("/api/v1/voice/engines")
    assert response.status_code == 200
    assert "engines" in response.json()
    assert isinstance(response.json()["engines"], list)


def test_tts_info_endpoint():
    """Test TTS info endpoint"""
    response = client.get("/api/v1/voice/tts/info")
    assert response.status_code == 200
    assert "voices" in response.json()
    assert isinstance(response.json()["voices"], list)
