"""
Tests for core system endpoints
Health checks and root endpoint
"""

from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Tests for health check endpoints."""
    
    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint returns API info."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert data["name"] == "AutoML Platform"
    
    def test_health_check(self, client: TestClient):
        """Test basic health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["service"] == "AutoML Platform"
    
    def test_database_health_check(self, client: TestClient):
        """Test database connectivity health check."""
        response = client.get("/health/db")
        
        assert response.status_code == 200
        data = response.json()
        # Note: With SQLite test DB, this should pass
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
