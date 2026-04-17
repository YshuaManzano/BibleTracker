"""
Test reading plans and progress tracking
"""
import pytest

class TestReadingPlans:
    """Reading plans endpoints"""

    def test_get_plans_list(self, base_url, api_client):
        """Test /plans returns 5 reading plans"""
        response = api_client.get(f"{base_url}/api/plans")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "plans" in data
        assert len(data["plans"]) == 5, f"Expected 5 plans, got {len(data['plans'])}"
        
        # Verify plan structure
        plan = data["plans"][0]
        assert "id" in plan
        assert "name" in plan
        assert "duration_days" in plan
        print(f"✓ Plans list returned {len(data['plans'])} plans")

    def test_activate_plan(self, base_url, api_client, test_user_token):
        """Test activating a reading plan"""
        token, email = test_user_token
        headers = {"Authorization": f"Bearer {token}"}
        
        # Activate NT 90 days plan
        response = api_client.post(f"{base_url}/api/plans/activate/nt-90-days", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["plan_id"] == "nt-90-days"
        assert data["status"] == "active"
        assert "daily_assignments" in data
        assert data["total_chapters"] > 0
        print(f"✓ Plan activated: {data['plan_name']}, {data['total_chapters']} chapters")

    def test_get_active_plans(self, base_url, api_client, test_user_token):
        """Test retrieving active plans for user"""
        token, email = test_user_token
        headers = {"Authorization": f"Bearer {token}"}
        
        response = api_client.get(f"{base_url}/api/plans/active", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "plans" in data
        assert len(data["plans"]) > 0, "Should have at least one active plan"
        print(f"✓ Active plans retrieved: {len(data['plans'])} plans")

    def test_activate_duplicate_plan(self, base_url, api_client, test_user_token):
        """Test activating same plan twice fails"""
        token, email = test_user_token
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to activate same plan again
        response = api_client.post(f"{base_url}/api/plans/activate/nt-90-days", headers=headers)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print(f"✓ Duplicate plan activation correctly rejected")


class TestProgress:
    """Progress tracking endpoints"""

    def test_mark_chapter_read(self, base_url, api_client, test_user_token):
        """Test marking a chapter as read"""
        token, email = test_user_token
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get active plan
        plans_resp = api_client.get(f"{base_url}/api/plans/active", headers=headers)
        plans = plans_resp.json()["plans"]
        if not plans:
            pytest.skip("No active plans to test with")
        
        plan_id = plans[0]["id"]
        
        # Mark Matthew 1 as read
        response = api_client.post(f"{base_url}/api/progress/mark-read", 
            headers=headers,
            json={"plan_id": plan_id, "book_slug": "matthew", "chapter": 1}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["status"] == "ok"
        assert "date" in data
        print(f"✓ Chapter marked as read: Matthew 1")

    def test_get_streak(self, base_url, api_client, test_user_token):
        """Test getting user's reading streak"""
        token, email = test_user_token
        headers = {"Authorization": f"Bearer {token}"}
        
        response = api_client.get(f"{base_url}/api/progress/streak", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "current_streak" in data
        assert "longest_streak" in data
        assert "grace_day_available" in data
        assert "total_days_read" in data
        assert isinstance(data["current_streak"], int)
        print(f"✓ Streak data: current={data['current_streak']}, longest={data['longest_streak']}")

    def test_get_heatmap(self, base_url, api_client, test_user_token):
        """Test getting reading heatmap"""
        token, email = test_user_token
        headers = {"Authorization": f"Bearer {token}"}
        
        response = api_client.get(f"{base_url}/api/progress/heatmap", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "heatmap" in data
        assert isinstance(data["heatmap"], dict)
        print(f"✓ Heatmap retrieved with {len(data['heatmap'])} days")

    def test_get_books_status(self, base_url, api_client, test_user_token):
        """Test getting completion status for all books"""
        token, email = test_user_token
        headers = {"Authorization": f"Bearer {token}"}
        
        response = api_client.get(f"{base_url}/api/progress/books-status", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "books" in data
        assert len(data["books"]) == 66
        
        # Check book structure
        book = data["books"][0]
        assert "slug" in book
        assert "name" in book
        assert "chapters" in book
        assert "read" in book
        assert "status" in book
        print(f"✓ Books status retrieved for 66 books")

    def test_dashboard_stats(self, base_url, api_client, test_user_token):
        """Test dashboard stats endpoint"""
        token, email = test_user_token
        headers = {"Authorization": f"Bearer {token}"}
        
        response = api_client.get(f"{base_url}/api/dashboard", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "active_plans" in data
        assert "total_chapters_read" in data
        assert "notes_count" in data
        assert "badges_earned" in data
        assert isinstance(data["active_plans"], int)
        print(f"✓ Dashboard stats: {data['active_plans']} plans, {data['total_chapters_read']} chapters read")
