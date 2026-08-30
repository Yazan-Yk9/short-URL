import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_check():
    """
    Verify that the /health endpoint returns 200 OK 
    and the correct JSON structure.
    """
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    
    assert data["status"] == "healthy"
    assert data["service"] == "FastAPI Health Service"
    assert "message" in data


def test_root():
    """
    Verify that the root endpoint (/) returns 200 OK
    and contains the welcome message.
    """
    response = client.get("/")
    
    assert response.status_code == 200
    
    data = response.json()
    
    assert data["message"] == "Welcome to the Health Check Service!"
    assert data["health_check"] == "/health"
    assert data["documentation"] == "/docs"


def test_not_found():
    """
    Verify that accessing a non-existent route returns 404.
    """
    response = client.get("/non-existent-path")
    assert response.status_code == 404
