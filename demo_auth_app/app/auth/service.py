"""Core business logic for user authentication, validation, and tokens."""
import hashlib
import hmac
import os
import re
import secrets
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from app.auth.storage import UserStorage, storage as default_storage

# Token store for in-memory session tokens: token -> {user_id, expires_at}
_active_tokens: Dict[str, dict] = {}

def hash_password(password: str, salt: Optional[str] = None) -> str:
    """Hashes a password using PBKDF2-HMAC-SHA256 with salt."""
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations=100_000,
    ).hex()
    return f"{salt}${hashed}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the stored salt$hash string."""
    try:
        salt, expected_hash = hashed_password.split("$", 1)
        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations=100_000,
        ).hex()
        return hmac.compare_digest(expected_hash, actual_hash)
    except (ValueError, AttributeError):
        return False

def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
    """
    Validates password against security rules.
    Rules:
      - At least 8 characters
      - Contains at least one digit
      - Contains at least one uppercase letter
      - Contains at least one lowercase letter
    """
    errors: List[str] = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if not re.search(r"\d", password):
        errors.append("Password must contain at least one number.")
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter.")
    return (len(errors) == 0, errors)

class UserService:
    """Service handling registration, login, and profile lookup."""

    def __init__(self, user_storage: Optional[UserStorage] = None):
        self.storage = user_storage or default_storage

    def register(self, username: str, email: str, password: str, confirm_password: str) -> dict:
        """Registers a new user after verifying business rules."""
        username = username.strip()
        email = email.strip().lower()

        # 1. Validation checks
        if password != confirm_password:
            raise ValueError("Passwords do not match.")

        is_strong, strength_errors = validate_password_strength(password)
        if not is_strong:
            raise ValueError(" ".join(strength_errors))

        # 2. Duplicate checks
        if self.storage.get_by_username(username):
            raise ValueError("Username is already taken.")

        if self.storage.get_by_email(email):
            raise ValueError("Email is already registered.")

        # 3. Create user record
        user_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        user_data = {
            "id": user_id,
            "username": username,
            "email": email,
            "password_hash": hash_password(password),
            "created_at": created_at,
        }
        return self.storage.create(user_data)

    def authenticate(self, username_or_email: str, password: str) -> Optional[dict]:
        """Authenticates a user by username or email and password."""
        ident = username_or_email.strip()
        user = self.storage.get_by_username(ident) or self.storage.get_by_email(ident)
        if not user:
            return None

        if not verify_password(password, user["password_hash"]):
            return None

        return user

    def create_session_token(self, user_id: str, ttl_seconds: int = 3600) -> str:
        """Creates an in-memory session token for the user."""
        token = secrets.token_urlsafe(32)
        _active_tokens[token] = {
            "user_id": user_id,
            "expires_at": time.time() + ttl_seconds,
        }
        return token

    def get_user_from_token(self, token: str) -> Optional[dict]:
        """Returns user profile if token is valid and not expired."""
        session = _active_tokens.get(token)
        if not session:
            return None

        if time.time() > session["expires_at"]:
            _active_tokens.pop(token, None)
            return None

        return self.storage.get_by_id(session["user_id"])

    def revoke_token(self, token: str) -> None:
        """Revokes a session token upon logout."""
        _active_tokens.pop(token, None)

    def clear_tokens(self) -> None:
        """Clears all session tokens (used for test teardown)."""
        _active_tokens.clear()

