import pytest
import requests
import os

@pytest.fixture(scope="session")
def base_url():
    """Get base URL from environment"""
    url = os.environ.get('EXPO_PUBLIC_BACKEND_URL')
    if not url:
        pytest.fail("EXPO_PUBLIC_BACKEND_URL not set in environment")
    return url.rstrip('/')

@pytest.fixture(scope="session")
def api_client(base_url):
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session

@pytest.fixture(scope="session")
def admin_token(base_url, api_client):
    """Get admin auth token"""
    try:
        response = api_client.post(f"{base_url}/api/auth/login", json={
            "email": "admin@bibleapp.com",
            "password": "admin123"
        })
        if response.status_code == 200:
            data = response.json()
            return data.get("token")
        else:
            pytest.skip(f"Admin login failed: {response.status_code}")
    except Exception as e:
        pytest.skip(f"Cannot authenticate admin: {e}")

@pytest.fixture(scope="session")
def test_user_token(base_url, api_client):
    """Create and authenticate test user"""
    import uuid
    email = f"test_{uuid.uuid4().hex[:8]}@bibleapp.com"
    try:
        # Register
        response = api_client.post(f"{base_url}/api/auth/register", json={
            "name": "Test User",
            "email": email,
            "password": "test123456"
        })
        if response.status_code == 200:
            data = response.json()
            return data.get("token"), email
        else:
            pytest.skip(f"Test user registration failed: {response.status_code}")
    except Exception as e:
        pytest.skip(f"Cannot create test user: {e}")
