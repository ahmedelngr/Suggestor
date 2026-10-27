from fastapi.testclient import TestClient

from backend.app.db import get_conn
from backend.app.main import app

client = TestClient(app)


class FakeConn:
    def execute(self, query):
        return None


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_health_db_with_fake_connection():
    app.dependency_overrides[get_conn] = lambda: FakeConn()
    try:
        assert client.get("/health/db").json() == {"status": "ok"}
    finally:
        app.dependency_overrides.clear()