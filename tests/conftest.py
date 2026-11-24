"""Pytest fixtures."""
import os
import tempfile

import pytest

from app.app import create_app
from app.config import TestingConfig


@pytest.fixture()
def app():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    class TestConfig(TestingConfig):
        DATABASE_PATH = db_path

    application = create_app(TestConfig)
    yield application
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth_client(client):
    client.post(
        "/login",
        data={"username": "admin", "password": "admin123"},
        follow_redirects=True,
    )
    return client
