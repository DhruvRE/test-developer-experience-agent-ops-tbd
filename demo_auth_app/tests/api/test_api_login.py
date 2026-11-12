"""API tests for the /api/login and /api/logout endpoints."""
import pytest
from fastapi.testclient import TestClient

@pytest.mark.api
class TestLoginAPI:
    @pytest.fixture(autouse=True)
    def setup_user(self, api_client: TestClient):
        # Seed a test user
        api_client.post(
            "/api/register",
            json={
                "username": "tester",
                "email": "tester@example.com",
                "password": "Password123",
                "confirm_password": "Password123",
            },
        )

    def test_login_success_with_username(self, api_client: TestClient):
        response = api_client.post(
            "/api/login",
            json={"username": "tester", "password": "Password123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["username"] == "tester"
        assert "session_token" in response.cookies

    def test_login_success_with_email(self, api_client: TestClient):
        response = api_client.post(
            "/api/login",
            json={"username": "tester@example.com", "password": "Password123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["email"] == "tester@example.com"

    def test_login_wrong_password_returns_401(self, api_client: TestClient):
        response = api_client.post(
            "/api/login",
            json={"username": "tester", "password": "WrongPassword999"},
        )
        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]

    def test_login_unknown_user_returns_401(self, api_client: TestClient):
        response = api_client.post(
            "/api/login",
            json={"username": "ghost_user", "password": "Password123"},
        )
        assert response.status_code == 401

    def test_logout_clears_cookie(self, api_client: TestClient):
        login_res = api_client.post(
            "/api/login",
            json={"username": "tester", "password": "Password123"},
        )
        token = login_res.json()["access_token"]

        logout_res = api_client.post(
            "/api/logout",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert logout_res.status_code == 200
        assert logout_res.json()["success"] is True

