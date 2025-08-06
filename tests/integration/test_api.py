"""
Integration tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
import io
import os

from app.main import app


# Test client
client = TestClient(app)


def test_health_endpoint():
    """Test health endpoint returns 200 and correct structure"""
    # Act
    response = client.get("/health")
    
    # Assert
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "version" in response.json()
    assert "timestamp" in response.json()


def test_extract_endpoint_invalid_file():
    """Test extract endpoint with invalid file type"""
    # Arrange
    test_file = io.BytesIO(b"This is not a PDF file")
    test_file.name = "test.txt"
    
    # Act
    response = client.post(
        "/api/extract",
        files={"file": ("test.txt", test_file, "text/plain")},
        headers={"Authorization": f"Bearer {os.environ.get('API_KEY', 'test_api_key')}"}
    )
    
    # Assert
    assert response.status_code == 400
    assert "Only PDF files are supported" in response.json()["detail"]


def test_extract_endpoint_missing_auth():
    """Test extract endpoint with missing authentication"""
    # Arrange
    test_file = io.BytesIO(b"%PDF-1.7\nThis is a fake PDF\n%%EOF")
    
    # Act
    response = client.post(
        "/api/extract",
        files={"file": ("test.pdf", test_file, "application/pdf")}
    )
    
    # Assert
    assert response.status_code == 401


def test_extract_endpoint_invalid_auth():
    """Test extract endpoint with invalid authentication"""
    # Arrange
    test_file = io.BytesIO(b"%PDF-1.7\nThis is a fake PDF\n%%EOF")
    
    # Act
    response = client.post(
        "/api/extract",
        files={"file": ("test.pdf", test_file, "application/pdf")},
        headers={"Authorization": "Bearer invalid_key"}
    )
    
    # Assert
    assert response.status_code == 401 