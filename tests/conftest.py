# File: tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module")
def test_client():
    """
    Silicon Valley Standard: Test Fixture.
    Creates an isolated, in-memory instance of the HOMS API for testing.
    """
    with TestClient(app) as client:
        yield client