"""User data storage layer."""
from typing import Dict, Optional, List
import threading

class UserStorage:
    """Thread-safe in-memory user repository for demo and testing."""

    def __init__(self):
        self._users_by_id: Dict[str, dict] = {}
        self._lock = threading.Lock()

    def create(self, user_data: dict) -> dict:
        with self._lock:
            user_id = user_data["id"]
            stored = dict(user_data)
            self._users_by_id[user_id] = stored
            return dict(stored)

    def get_by_id(self, user_id: str) -> Optional[dict]:
        with self._lock:
            user = self._users_by_id.get(user_id)
            return dict(user) if user else None

    def get_by_username(self, username: str) -> Optional[dict]:
        with self._lock:
            uname_lower = username.lower()
            for user in self._users_by_id.values():
                if user["username"].lower() == uname_lower:
                    return dict(user)
            return None

    def get_by_email(self, email: str) -> Optional[dict]:
        with self._lock:
            email_lower = email.lower()
            for user in self._users_by_id.values():
                if user["email"].lower() == email_lower:
                    return dict(user)
            return None

    def list_all(self) -> List[dict]:
        with self._lock:
            return [dict(u) for u in self._users_by_id.values()]

    def count(self) -> int:
        with self._lock:
            return len(self._users_by_id)

    def clear(self) -> None:
        with self._lock:
            self._users_by_id.clear()

# Global default instance
storage = UserStorage()

