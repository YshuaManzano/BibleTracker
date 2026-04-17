import pytest
import requests
import os

@pytest.fixture(scope="session")
def base_url():
    """Get base URL from environment"""
    url = os.environ.get('EXPO_PUBLIC_BACKEND_URL', 'https://versetrack.preview.emergentagent.com')
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
            return data.get("token")
        else:
            pytest.skip(f"Test user registration failed: {response.status_code}")
    except Exception as e:
        pytest.skip(f"Cannot create test user: {e}")

@pytest.fixture(scope="session")
def test_user_id(base_url, api_client, test_user_token):
    """Get test user ID"""
    try:
        response = api_client.get(f"{base_url}/api/auth/me", headers={"Authorization": f"Bearer {test_user_token}"})
        if response.status_code == 200:
            return response.json()["id"]
        else:
            pytest.skip("Cannot get test user ID")
    except Exception as e:
        pytest.skip(f"Cannot get test user ID: {e}")
