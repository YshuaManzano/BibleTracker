"""
Test AI features, notes, badges, and mood suggestions
"""
import pytest

class TestAIFeatures:
    """AI-powered features"""

    def test_get_mood_suggestions(self, base_url, api_client):
        """Test mood suggestions endpoint returns 6 moods"""
        response = api_client.get(f"{base_url}/api/ai/mood-suggestions")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "moods" in data
        moods = data["moods"]
        assert len(moods) == 6, f"Expected 6 moods, got {len(moods)}"
        
        # Check mood structure
        assert "anxious" in moods
        assert "joyful" in moods
        assert "grieving" in moods
        assert "grateful" in moods
        assert "seeking" in moods
        assert "lonely" in moods
        
        # Verify passages
        anxious_mood = moods["anxious"]
        assert "passages" in anxious_mood
        assert len(anxious_mood["passages"]) > 0
        print(f"✓ Mood suggestions returned {len(moods)} moods")

    def test_get_ai_summary(self, base_url, api_client, test_user_token):
        """Test AI chapter summary generation"""
        token, email = test_user_token
        headers = {"Authorization": f"Bearer {token}"}
        
        # Request summary for John 3
        response = api_client.get(f"{base_url}/api/ai/summary/john/3", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "summary" in data
        assert len(data["summary"]) > 0, "Summary should not be empty"
        print(f"✓ AI summary generated for John 3: {data['summary'][:100]}...")


class TestNotes:
    """Notes CRUD operations"""

    def test_create_note(self, base_url, api_client, test_user_token):
        """Test creating a note on a chapter"""
        token, email = test_user_token
        headers = {"Authorization": f"Bearer {token}"}
        
        response = api_client.post(f"{base_url}/api/notes",
            headers=headers,
            json={"book_slug": "psalms", "chapter": 23, "text": "TEST_The Lord is my shepherd note"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "id" in data
        assert data["book_slug"] == "psalms"
        assert data["chapter"] == 23
        assert data["text"] == "TEST_The Lord is my shepherd note"
        print(f"✓ Note created: {data['id']}")
        return data["id"]

    def test_get_notes_for_chapter(self, base_url, api_client, test_user_token):
        """Test retrieving notes for specific chapter"""
        token, email = test_user_token
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create a note first
        api_client.post(f"{base_url}/api/notes",
            headers=headers,
            json={"book_slug": "john", "chapter": 3, "text": "TEST_Note for John 3"}
        )
        
        # Get notes
        response = api_client.get(f"{base_url}/api/notes?book_slug=john&chapter=3", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "notes" in data
        assert len(data["notes"]) > 0
        print(f"✓ Notes retrieved: {len(data['notes'])} notes for John 3")

    def test_update_note(self, base_url, api_client, test_user_token):
        """Test updating a note"""
        token, email = test_user_token
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create note
        create_resp = api_client.post(f"{base_url}/api/notes",
            headers=headers,
            json={"book_slug": "romans", "chapter": 8, "text": "TEST_Original note"}
        )
        note_id = create_resp.json()["id"]
        
        # Update note
        response = api_client.put(f"{base_url}/api/notes/{note_id}",
            headers=headers,
            json={"text": "TEST_Updated note text"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Verify update
        get_resp = api_client.get(f"{base_url}/api/notes?book_slug=romans&chapter=8", headers=headers)
        notes = get_resp.json()["notes"]
        updated_note = next((n for n in notes if n["id"] == note_id), None)
        assert updated_note is not None
        assert updated_note["text"] == "TEST_Updated note text"
        print(f"✓ Note updated successfully")

    def test_delete_note(self, base_url, api_client, test_user_token):
        """Test deleting a note"""
        token, email = test_user_token
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create note
        create_resp = api_client.post(f"{base_url}/api/notes",
            headers=headers,
            json={"book_slug": "genesis", "chapter": 1, "text": "TEST_Note to delete"}
        )
        note_id = create_resp.json()["id"]
        
        # Delete note
        response = api_client.delete(f"{base_url}/api/notes/{note_id}", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Verify deletion
        get_resp = api_client.get(f"{base_url}/api/notes", headers=headers)
        notes = get_resp.json()["notes"]
        deleted_note = next((n for n in notes if n["id"] == note_id), None)
        assert deleted_note is None, "Note should be deleted"
        print(f"✓ Note deleted successfully")


class TestBadges:
    """Badges and achievements"""

    def test_get_badges(self, base_url, api_client, test_user_token):
        """Test getting user badges"""
        token, email = test_user_token
        headers = {"Authorization": f"Bearer {token}"}
        
        response = api_client.get(f"{base_url}/api/badges", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "badges" in data
        assert len(data["badges"]) > 0
        
        # Check badge structure
        badge = data["badges"][0]
        assert "id" in badge
        assert "name" in badge
        assert "description" in badge
        assert "earned" in badge
        assert isinstance(badge["earned"], bool)
        print(f"✓ Badges retrieved: {len(data['badges'])} total badges")


class TestSettings:
    """User settings"""

    def test_get_settings(self, base_url, api_client, test_user_token):
        """Test getting user settings"""
        token, email = test_user_token
        headers = {"Authorization": f"Bearer {token}"}
        
        response = api_client.get(f"{base_url}/api/settings", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "theme" in data
        assert data["theme"] in ["auto", "light", "dark"]
        print(f"✓ Settings retrieved: theme={data['theme']}")

    def test_update_theme(self, base_url, api_client, test_user_token):
        """Test updating theme setting"""
        token, email = test_user_token
        headers = {"Authorization": f"Bearer {token}"}
        
        response = api_client.put(f"{base_url}/api/settings/theme",
            headers=headers,
            json={"theme": "dark"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["theme"] == "dark"
        
        # Verify persistence
        get_resp = api_client.get(f"{base_url}/api/settings", headers=headers)
        assert get_resp.json()["theme"] == "dark"
        print(f"✓ Theme updated to dark")
