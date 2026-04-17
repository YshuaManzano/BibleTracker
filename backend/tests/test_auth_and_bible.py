"""
Test auth endpoints and basic Bible data endpoints
"""
import pytest
import requests

class TestAuth:
    """Authentication endpoint tests"""

    def test_admin_login_success(self, base_url, api_client):
        """Test admin can login with correct credentials"""
        response = api_client.post(f"{base_url}/api/auth/login", json={
            "email": "admin@bibleapp.com",
            "password": "admin123"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "token" in data, "Response should contain token"
        assert "user" in data, "Response should contain user"
        assert data["user"]["email"] == "admin@bibleapp.com"
        print(f"✓ Admin login successful, token received")

    def test_login_wrong_password(self, base_url, api_client):
        """Test login fails with wrong password"""
        response = api_client.post(f"{base_url}/api/auth/login", json={
            "email": "admin@bibleapp.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"✓ Wrong password correctly rejected")

    def test_register_new_user(self, base_url, api_client):
        """Test user registration creates account and returns token"""
        import uuid
        email = f"TEST_newuser_{uuid.uuid4().hex[:8]}@bibleapp.com"
        
        response = api_client.post(f"{base_url}/api/auth/register", json={
            "name": "New Test User",
            "email": email,
            "password": "newpass123"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "token" in data, "Registration should return token"
        assert "user" in data, "Registration should return user"
        assert data["user"]["email"] == email.lower()
        print(f"✓ User registration successful for {email}")

    def test_register_duplicate_email(self, base_url, api_client):
        """Test registration fails for duplicate email"""
        response = api_client.post(f"{base_url}/api/auth/register", json={
            "name": "Duplicate",
            "email": "admin@bibleapp.com",
            "password": "test123"
        })
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print(f"✓ Duplicate email correctly rejected")

    def test_get_me_with_token(self, base_url, api_client, admin_token):
        """Test /auth/me returns user info with valid token"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = api_client.get(f"{base_url}/api/auth/me", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "email" in data
        assert data["email"] == "admin@bibleapp.com"
        print(f"✓ /auth/me returned user info")

    def test_get_me_without_token(self, base_url, api_client):
        """Test /auth/me fails without token"""
        response = api_client.get(f"{base_url}/api/auth/me")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"✓ /auth/me correctly requires authentication")


class TestBibleData:
    """Bible data endpoints (public)"""

    def test_get_daily_verse(self, base_url, api_client):
        """Test daily verse endpoint returns verse data"""
        response = api_client.get(f"{base_url}/api/bible/daily-verse")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "ref" in data, "Daily verse should have ref"
        assert "text" in data, "Daily verse should have text"
        assert len(data["text"]) > 0, "Verse text should not be empty"
        print(f"✓ Daily verse: {data['ref']}")

    def test_get_books_list(self, base_url, api_client):
        """Test books endpoint returns all 66 Bible books"""
        response = api_client.get(f"{base_url}/api/bible/books")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "books" in data
        assert len(data["books"]) == 66, f"Expected 66 books, got {len(data['books'])}"
        assert "categories" in data
        print(f"✓ Books list returned {len(data['books'])} books")

    def test_get_chapter_genesis_1(self, base_url, api_client):
        """Test fetching Genesis 1 chapter text"""
        response = api_client.get(f"{base_url}/api/bible/chapter/kjv/genesis/1")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["book"] == "Genesis"
        assert data["chapter"] == 1
        assert data["version"] == "kjv"
        assert "verses" in data or "text" in data
        if "verses" in data:
            assert len(data["verses"]) > 0, "Genesis 1 should have verses"
        print(f"✓ Genesis 1 fetched successfully")

    def test_get_chapter_invalid_book(self, base_url, api_client):
        """Test invalid book slug returns 404"""
        response = api_client.get(f"{base_url}/api/bible/chapter/kjv/invalidbook/1")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"✓ Invalid book correctly returns 404")

    def test_get_chapter_invalid_chapter_number(self, base_url, api_client):
        """Test invalid chapter number returns 400"""
        response = api_client.get(f"{base_url}/api/bible/chapter/kjv/genesis/999")
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print(f"✓ Invalid chapter number correctly returns 400")
