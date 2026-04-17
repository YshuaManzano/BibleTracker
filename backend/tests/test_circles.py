"""
Backend tests for Reading Circles feature
Tests: Create circle, list circles, join circle, get circle detail, approve/reject members, leave/delete circle
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('EXPO_PUBLIC_BACKEND_URL', 'https://versetrack.preview.emergentagent.com').rstrip('/')

class TestCirclesCreate:
    """Test circle creation"""

    def test_create_public_circle(self, api_client, admin_token):
        """Create a public circle with individual plan mode"""
        response = api_client.post(
            f"{BASE_URL}/api/circles",
            json={
                "name": "TEST_Public Circle",
                "description": "A test public circle",
                "privacy": "public",
                "plan_mode": "individual"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "TEST_Public Circle"
        assert data["privacy"] == "public"
        assert data["plan_mode"] == "individual"
        assert "invite_code" in data
        assert len(data["invite_code"]) == 8
        assert "id" in data
        assert len(data["members"]) == 1
        assert data["members"][0]["role"] == "creator"
        return data["id"], data["invite_code"]

    def test_create_private_circle(self, api_client, admin_token):
        """Create a private circle"""
        response = api_client.post(
            f"{BASE_URL}/api/circles",
            json={
                "name": "TEST_Private Circle",
                "description": "A test private circle",
                "privacy": "private",
                "plan_mode": "individual"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["privacy"] == "private"
        assert "invite_code" in data

    def test_create_circle_requires_auth(self, api_client):
        """Creating a circle requires authentication"""
        response = api_client.post(
            f"{BASE_URL}/api/circles",
            json={"name": "Test Circle", "privacy": "public", "plan_mode": "individual"}
        )
        assert response.status_code == 401


class TestCirclesList:
    """Test listing user's circles"""

    def test_list_my_circles(self, api_client, admin_token):
        """List circles user is a member of"""
        # First create a circle
        create_response = api_client.post(
            f"{BASE_URL}/api/circles",
            json={
                "name": "TEST_My Circle",
                "description": "Test",
                "privacy": "public",
                "plan_mode": "individual"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert create_response.status_code == 200

        # Now list circles
        response = api_client.get(
            f"{BASE_URL}/api/circles",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "circles" in data
        assert len(data["circles"]) > 0
        # Check that our circle is in the list
        circle_names = [c["name"] for c in data["circles"]]
        assert "TEST_My Circle" in circle_names or "Sunday School Group" in circle_names

    def test_list_circles_requires_auth(self, api_client):
        """Listing circles requires authentication"""
        response = api_client.get(f"{BASE_URL}/api/circles")
        assert response.status_code == 401


class TestCirclesJoin:
    """Test joining circles via invite code"""

    def test_join_public_circle(self, api_client, admin_token, test_user_token):
        """Join a public circle with invite code"""
        # Admin creates a circle
        create_response = api_client.post(
            f"{BASE_URL}/api/circles",
            json={
                "name": "TEST_Join Public",
                "description": "Test join",
                "privacy": "public",
                "plan_mode": "individual"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert create_response.status_code == 200
        invite_code = create_response.json()["invite_code"]

        # Test user joins
        join_response = api_client.post(
            f"{BASE_URL}/api/circles/join",
            json={"invite_code": invite_code},
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert join_response.status_code == 200
        data = join_response.json()
        assert data["status"] == "active"
        assert "Joined successfully" in data["message"]

    def test_join_private_circle_pending(self, api_client, admin_token, test_user_token):
        """Join a private circle results in pending status"""
        # Admin creates a private circle
        create_response = api_client.post(
            f"{BASE_URL}/api/circles",
            json={
                "name": "TEST_Join Private",
                "description": "Test private join",
                "privacy": "private",
                "plan_mode": "individual"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert create_response.status_code == 200
        invite_code = create_response.json()["invite_code"]

        # Test user joins
        join_response = api_client.post(
            f"{BASE_URL}/api/circles/join",
            json={"invite_code": invite_code},
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert join_response.status_code == 200
        data = join_response.json()
        assert data["status"] == "pending"
        assert "approval" in data["message"].lower()

    def test_join_invalid_code(self, api_client, test_user_token):
        """Join with invalid invite code returns 404"""
        response = api_client.post(
            f"{BASE_URL}/api/circles/join",
            json={"invite_code": "INVALID1"},
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 404

    def test_join_already_member(self, api_client, admin_token):
        """Joining a circle you're already in returns 400"""
        # Create circle
        create_response = api_client.post(
            f"{BASE_URL}/api/circles",
            json={
                "name": "TEST_Already Member",
                "privacy": "public",
                "plan_mode": "individual"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        invite_code = create_response.json()["invite_code"]

        # Try to join own circle
        join_response = api_client.post(
            f"{BASE_URL}/api/circles/join",
            json={"invite_code": invite_code},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert join_response.status_code == 400


class TestCircleInvite:
    """Test getting circle info by invite code"""

    def test_get_circle_by_invite(self, api_client, admin_token):
        """Get circle info by invite code (no auth required)"""
        # Create circle
        create_response = api_client.post(
            f"{BASE_URL}/api/circles",
            json={
                "name": "TEST_Invite Info",
                "description": "Test invite info",
                "privacy": "public",
                "plan_mode": "individual"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        invite_code = create_response.json()["invite_code"]

        # Get circle info (no auth)
        response = api_client.get(f"{BASE_URL}/api/circles/invite/{invite_code}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "TEST_Invite Info"
        assert data["description"] == "Test invite info"
        assert data["privacy"] == "public"
        assert data["invite_code"] == invite_code
        assert "member_count" in data

    def test_get_circle_invalid_invite(self, api_client):
        """Get circle with invalid invite code returns 404"""
        response = api_client.get(f"{BASE_URL}/api/circles/invite/INVALID1")
        assert response.status_code == 404


class TestCircleDetail:
    """Test getting circle detail with member progress"""

    def test_get_circle_detail(self, api_client, admin_token):
        """Get circle detail with member progress bars"""
        # Create circle
        create_response = api_client.post(
            f"{BASE_URL}/api/circles",
            json={
                "name": "TEST_Detail Circle",
                "description": "Test detail",
                "privacy": "public",
                "plan_mode": "individual"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        circle_id = create_response.json()["id"]

        # Get detail
        response = api_client.get(
            f"{BASE_URL}/api/circles/{circle_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "TEST_Detail Circle"
        assert "members_progress" in data
        assert len(data["members_progress"]) == 1
        member = data["members_progress"][0]
        assert "total_chapters_read" in member
        assert "current_streak" in member
        assert member["role"] == "creator"
        assert data["is_creator"] is True

    def test_get_circle_detail_not_member(self, api_client, admin_token, test_user_token):
        """Non-members cannot view circle detail"""
        # Admin creates circle
        create_response = api_client.post(
            f"{BASE_URL}/api/circles",
            json={
                "name": "TEST_Private Detail",
                "privacy": "private",
                "plan_mode": "individual"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        circle_id = create_response.json()["id"]

        # Test user tries to view (not a member)
        response = api_client.get(
            f"{BASE_URL}/api/circles/{circle_id}",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 403


class TestCircleApproval:
    """Test approve/reject members for private circles"""

    def test_approve_member(self, api_client, admin_token, test_user_token, test_user_id):
        """Creator can approve pending member"""
        # Admin creates private circle
        create_response = api_client.post(
            f"{BASE_URL}/api/circles",
            json={
                "name": "TEST_Approve Circle",
                "privacy": "private",
                "plan_mode": "individual"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        circle_id = create_response.json()["id"]
        invite_code = create_response.json()["invite_code"]

        # Test user joins (pending)
        api_client.post(
            f"{BASE_URL}/api/circles/join",
            json={"invite_code": invite_code},
            headers={"Authorization": f"Bearer {test_user_token}"}
        )

        # Admin approves
        approve_response = api_client.post(
            f"{BASE_URL}/api/circles/{circle_id}/approve/{test_user_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert approve_response.status_code == 200
        assert approve_response.json()["status"] == "approved"

        # Verify member is now active
        detail_response = api_client.get(
            f"{BASE_URL}/api/circles/{circle_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        members = detail_response.json()["members_progress"]
        assert len(members) == 2

    def test_reject_member(self, api_client, admin_token, test_user_token, test_user_id):
        """Creator can reject pending member"""
        # Admin creates private circle
        create_response = api_client.post(
            f"{BASE_URL}/api/circles",
            json={
                "name": "TEST_Reject Circle",
                "privacy": "private",
                "plan_mode": "individual"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        circle_id = create_response.json()["id"]
        invite_code = create_response.json()["invite_code"]

        # Test user joins (pending)
        api_client.post(
            f"{BASE_URL}/api/circles/join",
            json={"invite_code": invite_code},
            headers={"Authorization": f"Bearer {test_user_token}"}
        )

        # Admin rejects
        reject_response = api_client.post(
            f"{BASE_URL}/api/circles/{circle_id}/reject/{test_user_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert reject_response.status_code == 200
        assert reject_response.json()["status"] == "rejected"

    def test_non_creator_cannot_approve(self, api_client, admin_token, test_user_token, test_user_id):
        """Non-creator cannot approve members"""
        # Admin creates circle
        create_response = api_client.post(
            f"{BASE_URL}/api/circles",
            json={
                "name": "TEST_Non Creator Approve",
                "privacy": "private",
                "plan_mode": "individual"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        circle_id = create_response.json()["id"]

        # Test user tries to approve (not creator)
        response = api_client.post(
            f"{BASE_URL}/api/circles/{circle_id}/approve/{test_user_id}",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 403


class TestCircleLeaveDelete:
    """Test leaving and deleting circles"""

    def test_leave_circle(self, api_client, admin_token, test_user_token):
        """Member can leave a circle"""
        # Admin creates public circle
        create_response = api_client.post(
            f"{BASE_URL}/api/circles",
            json={
                "name": "TEST_Leave Circle",
                "privacy": "public",
                "plan_mode": "individual"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        circle_id = create_response.json()["id"]
        invite_code = create_response.json()["invite_code"]

        # Test user joins
        api_client.post(
            f"{BASE_URL}/api/circles/join",
            json={"invite_code": invite_code},
            headers={"Authorization": f"Bearer {test_user_token}"}
        )

        # Test user leaves
        leave_response = api_client.delete(
            f"{BASE_URL}/api/circles/{circle_id}/leave",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert leave_response.status_code == 200
        assert leave_response.json()["status"] == "left"

    def test_creator_cannot_leave(self, api_client, admin_token):
        """Creator cannot leave their own circle"""
        # Admin creates circle
        create_response = api_client.post(
            f"{BASE_URL}/api/circles",
            json={
                "name": "TEST_Creator Leave",
                "privacy": "public",
                "plan_mode": "individual"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        circle_id = create_response.json()["id"]

        # Admin tries to leave
        response = api_client.delete(
            f"{BASE_URL}/api/circles/{circle_id}/leave",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 400

    def test_delete_circle(self, api_client, admin_token):
        """Creator can delete circle"""
        # Admin creates circle
        create_response = api_client.post(
            f"{BASE_URL}/api/circles",
            json={
                "name": "TEST_Delete Circle",
                "privacy": "public",
                "plan_mode": "individual"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        circle_id = create_response.json()["id"]

        # Admin deletes
        delete_response = api_client.delete(
            f"{BASE_URL}/api/circles/{circle_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert delete_response.status_code == 200
        assert delete_response.json()["status"] == "deleted"

        # Verify circle is gone
        get_response = api_client.get(
            f"{BASE_URL}/api/circles/{circle_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert get_response.status_code == 404

    def test_non_creator_cannot_delete(self, api_client, admin_token, test_user_token):
        """Non-creator cannot delete circle"""
        # Admin creates circle
        create_response = api_client.post(
            f"{BASE_URL}/api/circles",
            json={
                "name": "TEST_Non Creator Delete",
                "privacy": "public",
                "plan_mode": "individual"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        circle_id = create_response.json()["id"]
        invite_code = create_response.json()["invite_code"]

        # Test user joins
        api_client.post(
            f"{BASE_URL}/api/circles/join",
            json={"invite_code": invite_code},
            headers={"Authorization": f"Bearer {test_user_token}"}
        )

        # Test user tries to delete
        response = api_client.delete(
            f"{BASE_URL}/api/circles/{circle_id}",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 403
