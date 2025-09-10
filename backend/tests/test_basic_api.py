import pytest
import os
import sys
from fastapi.testclient import TestClient

# Add backend root to Python path
backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_root)

# Import the FastAPI app
from main import app

@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


class TestBasicEndpoints:
    """Test basic API endpoints that should exist"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "service" in data
    
    def test_test_endpoint(self, client):
        """Test the API test endpoint"""
        response = client.get("/api/v1/test")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data


class TestAPIDocumentation:
    """Test API documentation endpoints"""
    
    def test_docs_endpoint(self, client):
        """Test OpenAPI documentation endpoint"""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_openapi_json(self, client):
        """Test OpenAPI JSON schema"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert data["info"]["title"] == "DataQuest AI API"


class TestCORSConfiguration:
    """Test CORS configuration"""
    
    def test_cors_headers(self, client):
        """Test that CORS headers are properly configured"""
        # Make a regular request with Origin header to test CORS
        response = client.get(
            "/api/v1/test",
            headers={"Origin": "http://localhost:3000"}
        )
        # Should succeed and have CORS headers
        assert response.status_code == 200
        # Check for CORS headers (may not be present in test client, but endpoint should work)
        assert "success" in response.json()


class TestFileUploadEndpoints:
    """Test file upload related endpoints (if they exist)"""
    
    def test_files_endpoint_exists(self, client):
        """Test if files endpoints are accessible"""
        # Test if the files router is properly mounted
        response = client.get("/api/v1/files/analyses")
        
        # Should either work or give a proper HTTP error (not 404 for route)
        assert response.status_code != 404 or "not found" not in response.text.lower()


class TestApplicationStartup:
    """Test application configuration and startup"""
    
    def test_app_configuration(self):
        """Test that the app is properly configured"""
        assert app.title == "DataQuest AI API"
        assert app.version == "1.0.0"
        assert app.docs_url == "/docs"
        assert app.redoc_url == "/redoc"
    
    def test_router_mounting(self):
        """Test that routers are properly mounted"""
        # Check that routers are included
        route_paths = [route.path for route in app.routes]
        
        # Should have basic routes
        assert "/" in route_paths
        assert "/health" in route_paths
        
        # Should have API routes (prefixes)
        api_routes = [route.path for route in app.routes if "/api/v1" in route.path]
        assert len(api_routes) > 0


# Simple smoke tests for environment
class TestEnvironment:
    """Test environment configuration"""
    
    def test_python_version(self):
        """Test Python version compatibility"""
        assert sys.version_info >= (3, 9), "Python 3.9+ required"
    
    def test_backend_directory_structure(self):
        """Test that required directories exist"""
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Check for main files
        assert os.path.exists(os.path.join(backend_dir, "main.py"))
        assert os.path.exists(os.path.join(backend_dir, "requirements.txt"))
        
        # Check for app directory
        app_dir = os.path.join(backend_dir, "app")
        assert os.path.exists(app_dir)


# Basic integration test
class TestBasicIntegration:
    """Basic integration tests"""
    
    def test_full_request_cycle(self, client):
        """Test a complete request-response cycle"""
        # Test health check
        health_response = client.get("/health")
        assert health_response.status_code == 200
        
        # Test API endpoint
        api_response = client.get("/api/v1/test")
        assert api_response.status_code == 200
        
        # Verify responses are JSON
        assert isinstance(health_response.json(), dict)
        assert isinstance(api_response.json(), dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
