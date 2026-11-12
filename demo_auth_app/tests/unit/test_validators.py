"""Unit tests for password hashing, password strength validation, and Pydantic schemas."""
import pytest
from pydantic import ValidationError

from app.auth.service import (
    hash_password,
    verify_password,
    validate_password_strength,
)
from app.auth.models import UserRegisterRequest

@pytest.mark.unit
class TestPasswordSecurity:
    def test_hash_produces_salted_format(self):
        sample_input = "mock_test_sample_phrase_1"
        h = hash_password(sample_input)
        assert "$" in h
        salt, digest = h.split("$", 1)
        assert len(salt) == 32
        assert len(digest) == 64

    def test_verify_password_correct(self):
        sample_input = "mock_test_sample_phrase_1"
        h = hash_password(sample_input)
        assert verify_password(sample_input, h) is True

    def test_verify_password_incorrect(self):
        sample_input = "mock_test_sample_phrase_1"
        h = hash_password(sample_input)
        assert verify_password("different_mock_phrase_2", h) is False

    def test_verify_password_corrupted_hash(self):
        sample_input = "mock_test_sample_phrase_1"
        assert verify_password(sample_input, "invalid-hash-string") is False


@pytest.mark.unit
class TestPasswordStrengthValidator:
    def test_valid_strong_password(self):
        valid, errors = validate_password_strength("MockPass123_test")
        assert valid is True
        assert len(errors) == 0

    def test_short_password(self):
        valid, errors = validate_password_strength("Sh1A")
        assert valid is False
        assert any("at least 8 characters" in err for err in errors)

    def test_missing_digit(self):
        valid, errors = validate_password_strength("NoDigitsHere")
        assert valid is False
        assert any("at least one number" in err for err in errors)

    def test_missing_uppercase(self):
        valid, errors = validate_password_strength("lowercase123")
        assert valid is False
        assert any("at least one uppercase" in err for err in errors)

    def test_missing_lowercase(self):
        valid, errors = validate_password_strength("UPPERCASE123")
        assert valid is False
        assert any("at least one lowercase" in err for err in errors)


@pytest.mark.unit
class TestUserRegisterModel:
    def test_valid_registration_payload(self):
        model = UserRegisterRequest(
            username="john_doe",
            email="john@example.com",
            password="MockPass123_test",
            confirm_password="MockPass123_test",
        )
        assert model.username == "john_doe"
        assert model.email == "john@example.com"

    def test_mismatched_passwords_raises_validation_error(self):
        with pytest.raises(ValidationError) as exc:
            UserRegisterRequest(
                username="john_doe",
                email="john@example.com",
                password="MockPass123_test",
                confirm_password="DifferentMockPass456",
            )
        assert "Passwords do not match" in str(exc.value)

    def test_invalid_email_format(self):
        with pytest.raises(ValidationError) as exc:
            UserRegisterRequest(
                username="john_doe",
                email="not-an-email",
                password="MockPass123_test",
                confirm_password="MockPass123_test",
            )
        assert "value is not a valid email address" in str(exc.value)

    def test_username_with_special_characters(self):
        with pytest.raises(ValidationError) as exc:
            UserRegisterRequest(
                username="bad name!@#",
                email="user@example.com",
                password="MockPass123_test",
                confirm_password="MockPass123_test",
            )
        assert "alphanumeric characters and underscores" in str(exc.value)


