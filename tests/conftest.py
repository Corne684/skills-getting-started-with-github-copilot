"""
Pytest configuration and fixtures for FastAPI tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Arrange: Provide a TestClient for making HTTP requests to the FastAPI app.
    """
    return TestClient(app)


@pytest.fixture
def sample_email():
    """
    Arrange: Provide a sample email for test data.
    """
    return "test.student@mergington.edu"
