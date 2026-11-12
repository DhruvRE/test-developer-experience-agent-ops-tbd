"""API tests for protected endpoints (e.g., /api/me)."""
import pytest
from fastapi.testclient import TestClient

@pytest.mark.api
class TestProtectedEndpoints:
    def test_unauthenticated_request_returns_401(self, api_client: TestClient):
        response = api_client.get("/api/me")
        assert response.status_code == 401
        assert "Missing authentication credentials" in response.json()["detail"]

    def test_authenticated_with_bearer_header(self, api_client: TestClient):
        # 1. Register & login
        api_client.post(
            "/api/register",
            json={
                "username": "secured_user",
                "email": "secured@example.com",
                "password": "Password123",
                "confirm_password": "Password123",
            },
        )
        login_res = api_client.post(
            "/api/login",
            json={"username": "secured_user", "password": "Password123"},
        )
        token = login_res.json()["access_token"]

        # 2. Access /api/me
        response = api_client.get(
            "/api/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        user = response.json()
        assert user["username"] == "secured_user"
        assert user["email"] == "secured@example.com"

    def test_authenticated_with_session_cookie(self, api_client: TestClient):
        api_client.post(
            "/api/register",
            json={
                "username": "cookie_user",
                "email": "cookie@example.com",
                "password": "Password123",
                "confirm_password": "Password123",
            },
        )
        # Login automatically stores cookie in api_client session
        api_client.post(
            "/api/login",
            json={"username": "cookie_user", "password": "Password123"},
        )

        response = api_client.get("/api/me")
        assert response.status_code == 200
        assert response.json()["username"] == "cookie_user"

    def test_invalid_bearer_token_returns_401(self, api_client: TestClient):
        response = api_client.get(
            "/api/me",
            headers={"Authorization": "Bearer invalid-dummy-token"},
        )
        assert response.status_code == 401

