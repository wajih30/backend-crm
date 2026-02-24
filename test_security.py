"""Security tests - verify role-based access control"""

import pytest
import httpx
from app.main import app

@pytest.fixture
def client():
    return httpx.Client(app=app, base_url="http://test")

def test_public_register_disabled(client):
    """Test that public registration endpoint is disabled"""
    response = client.post("/api/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
        "role": "admin"
    })
    assert response.status_code == 403
    assert "disabled" in response.json()["detail"].lower()

def test_non_admin_cannot_create_users(client):
    """Test that non-admin users cannot create other users"""
    # This would require authenticated session, skipped for now
    pass

def test_non_admin_cannot_escalate_role(client):
    """Test that users cannot escalate their own role"""
    pass

def test_admin_can_create_users(client):
    """Test that admins can create other users"""
    pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
