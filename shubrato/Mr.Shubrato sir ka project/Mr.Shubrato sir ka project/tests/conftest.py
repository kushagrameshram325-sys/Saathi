"""
Test configuration for SAATHI API tests.

* Adds the backend directory to sys.path so that `app.*` imports resolve.
* Sets a separate test DATABASE_URL (saathi_test.db) so tests never touch
  the developer's local database.
* Provides a session-scoped FastAPI TestClient fixture.
"""

import os
import sys
from pathlib import Path

# Ensure `backend/` is on the import path before importing the app.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

# Use an isolated test database; must be set BEFORE importing app modules
# because the SQLAlchemy engine is created at import time from this env var.
os.environ["DATABASE_URL"] = "sqlite:///./saathi_test.db"

import pytest
from fastapi.testclient import TestClient

from app.main import app  # noqa: E402  – import after env var is set


@pytest.fixture(scope="session")
def client():
    """Session-scoped FastAPI TestClient that shares one database for all tests."""
    with TestClient(app) as test_client:
        yield test_client
