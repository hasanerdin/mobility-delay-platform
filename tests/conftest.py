"""
Shared pytest fixtures available to all tests without importing.

conftest.py is special — pytest auto-discovers it and makes every fixture
defined here available in any test file in this directory or below.
"""
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_db
from app.main import app


@pytest.fixture
def mock_db():
    """
    Return a MagicMock that stands in for a SQLAlchemy Session.
    Any attribute access or method call on it returns another MagicMock,
    so tests never need a real database connection.
    """
    return MagicMock()


@pytest.fixture
def client(mock_db):
    """
    Return a TestClient with the real database dependency swapped out.

    app.dependency_overrides tells FastAPI: "whenever get_db is requested,
    call this lambda instead". The override is cleaned up after each test
    via the yield + del pattern.
    """
    app.dependency_overrides[get_db] = lambda: mock_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]
