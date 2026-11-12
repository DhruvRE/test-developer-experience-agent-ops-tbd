"""API tests for the /api/register endpoint."""
import pytest
from fastapi.testclient import TestClient

@pytest.mark.api
class TestRegisterAPI:
    def test_register_success(self, api_client: TestClient):
        response = api_client.post(
            "/api/register",
            json={
                "username": "api_user",
                "email": "api_user@example.com",
                "password": "ValidPassword123",
                "confirm_password": "ValidPassword123",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "api_user"
        assert data["email"] == "api_user@example.com"
        assert "id" in data
        assert "password" not in data
        assert "password_hash" not in data

    def test_register_duplicate_username_returns_400(self, api_client: TestClient):
        payload = {
            "username": "dup_user",
            "email": "user1@example.com",
            "password": "ValidPassword123",
            "confirm_password": "ValidPassword123",
        }
        res1 = api_client.post("/api/register", json=payload)
        assert res1.status_code == 201

        payload["email"] = "different_email@example.com"
        res2 = api_client.post("/api/register", json=payload)
        assert res2.status_code == 400
        assert "Username is already taken" in res2.json()["detail"]

    def test_register_duplicate_email_returns_400(self, api_client: TestClient):
        res1 = api_client.post(
            "/api/register",
            json={
                "username": "user_one",
                "email": "shared@example.com",
                "password": "ValidPassword123",
                "confirm_password": "ValidPassword123",
            },
        )
        assert res1.status_code == 201

        res2 = api_client.post(
            "/api/register",
            json={
                "username": "user_two",
                "email": "shared@example.com",
                "password": "ValidPassword123",
                "confirm_password": "ValidPassword123",
            },
        )
        assert res2.status_code == 400
        assert "Email is already registered" in res2.json()["detail"]

    def test_register_invalid_body_returns_422(self, api_client: TestClient):
        # Missing required field 'password'
        response = api_client.post(
            "/api/register",
            json={"username": "incomplete_user", "email": "inc@example.com"},
        )
        assert response.status_code == 422

