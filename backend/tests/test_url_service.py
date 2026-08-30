import pytest
from fastapi.testclient import TestClient
from app.main import app

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
    assert data["service"] == "Short Link Service is running smoothly."
    assert data["storage"] == "in-memory (volatile)"


def test_root():
    """
    Verify that the root endpoint (/) returns 200 OK
    and contains the welcome message.
    """
    response = client.get("/")
    
    assert response.status_code == 200
    
    data = response.json()
    
    assert data["message"] == "Welcome to the Short Link Service!"
    assert data["health_check"] == "/health"
    assert data["docs"] == "/docs"


def test_not_found():
    """
    Verify that accessing a non-existent route returns 404.
    """
    response = client.get("/non-existent-path")
    assert response.status_code == 404
