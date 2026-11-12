"""Shared Pytest fixtures for Unit, API, and UI testing."""
import os
import sys
import socket
import threading
import time
from pathlib import Path
from typing import Generator

import pytest
import uvicorn
from fastapi.testclient import TestClient

# Ensure demo_auth_app is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.main import app
from app.auth.storage import storage as global_storage, UserStorage
from app.auth.service import UserService

def get_free_port() -> int:
    """Finds an unused ephemeral port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]

@pytest.fixture(autouse=True)
def clean_storage():
    """Resets in-memory user and token storage before and after every test."""
    global_storage.clear()
    UserService(global_storage).clear_tokens()
    yield
    global_storage.clear()
    UserService(global_storage).clear_tokens()

@pytest.fixture
def isolated_user_storage() -> UserStorage:
    """Provides an isolated UserStorage instance for unit tests."""
    return UserStorage()

@pytest.fixture
def user_service(isolated_user_storage: UserStorage) -> UserService:
    """Provides a UserService configured with an isolated storage instance."""
    return UserService(isolated_user_storage)

@pytest.fixture
def api_client() -> Generator[TestClient, None, None]:
    """FastAPI TestClient fixture for API testing."""
    with TestClient(app, base_url="http://testserver") as client:
        yield client

@pytest.fixture(scope="session")
def live_server_url() -> Generator[str, None, None]:
    """
    Launches a real live server in a background thread for browser UI testing.
    """
    port = get_free_port()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # Poll until server is ready
    url = f"http://127.0.0.1:{port}"
    timeout = 10.0
    start = time.time()
    ready = False

    while time.time() - start < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                ready = True
                break
        except OSError:
            time.sleep(0.1)

    if not ready:
        raise RuntimeError(f"Could not connect to live test server at {url} within {timeout}s")

    yield url

    server.should_exit = True
    thread.join(timeout=2.0)

