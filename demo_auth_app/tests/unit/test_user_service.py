"""Unit tests for UserService business logic in isolation."""
import pytest
from app.auth.service import UserService

@pytest.mark.unit
class TestUserService:
    def test_register_user_success(self, user_service: UserService):
        user = user_service.register(
            username="alice",
            email="alice@example.com",
            password="StrongPassword123",
            confirm_password="StrongPassword123",
        )
        assert user["id"] is not None
        assert user["username"] == "alice"
        assert user["email"] == "alice@example.com"
        assert "password_hash" in user
        assert user["password_hash"] != "StrongPassword123"

    def test_register_duplicate_username_raises_error(self, user_service: UserService):
        user_service.register(
            username="alice",
            email="alice@example.com",
            password="StrongPassword123",
            confirm_password="StrongPassword123",
        )
        with pytest.raises(ValueError) as exc:
            user_service.register(
                username="alice",
                email="another@example.com",
                password="StrongPassword123",
                confirm_password="StrongPassword123",
            )
        assert "Username is already taken" in str(exc.value)

    def test_register_duplicate_email_raises_error(self, user_service: UserService):
        user_service.register(
            username="alice",
            email="alice@example.com",
            password="StrongPassword123",
            confirm_password="StrongPassword123",
        )
        with pytest.raises(ValueError) as exc:
            user_service.register(
                username="bob",
                email="alice@example.com",
                password="StrongPassword123",
                confirm_password="StrongPassword123",
            )
        assert "Email is already registered" in str(exc.value)

    def test_authenticate_with_username_success(self, user_service: UserService):
        user_service.register(
            username="charlie",
            email="charlie@example.com",
            password="Password999",
            confirm_password="Password999",
        )
        auth = user_service.authenticate("charlie", "Password999")
        assert auth is not None
        assert auth["username"] == "charlie"

    def test_authenticate_with_email_success(self, user_service: UserService):
        user_service.register(
            username="david",
            email="david@example.com",
            password="Password999",
            confirm_password="Password999",
        )
        auth = user_service.authenticate("david@example.com", "Password999")
        assert auth is not None
        assert auth["username"] == "david"

    def test_authenticate_wrong_password_returns_none(self, user_service: UserService):
        user_service.register(
            username="eve",
            email="eve@example.com",
            password="Password999",
            confirm_password="Password999",
        )
        auth = user_service.authenticate("eve", "IncorrectPassword123")
        assert auth is None

    def test_authenticate_unknown_user_returns_none(self, user_service: UserService):
        auth = user_service.authenticate("ghost", "Password999")
        assert auth is None

    def test_session_token_lifecycle(self, user_service: UserService):
        user = user_service.register(
            username="frank",
            email="frank@example.com",
            password="Password999",
            confirm_password="Password999",
        )
        token = user_service.create_session_token(user["id"])
        retrieved_user = user_service.get_user_from_token(token)
        assert retrieved_user is not None
        assert retrieved_user["id"] == user["id"]

        # Revoke token
        user_service.revoke_token(token)
        assert user_service.get_user_from_token(token) is None

