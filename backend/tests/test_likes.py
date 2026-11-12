import os

import psycopg
import pytest
from fastapi.testclient import TestClient

from backend.app import main
from backend.app.auth import current_user
from backend.app.db import get_conn
from backend.app.main import app
from backend.app.swipes import get_likes

client = TestClient(app)

TEST_DB = os.environ.get("TEST_DATABASE_URL", "")
AUTH_ID = "00000000-0000-0000-0000-000000000004"

needs_scratch_db = pytest.mark.skipif(
    not ("localhost" in TEST_DB or "127.0.0.1" in TEST_DB),
    reason="set TEST_DATABASE_URL to a local scratch Postgres to run this",
)


@pytest.fixture
def conn():
    c = psycopg.connect(TEST_DB)
    yield c
    c.rollback()
    c.close()


def make_item(conn, name):
    return conn.execute(
        "INSERT INTO items (type, source, source_id, title) VALUES ('restaurant', 'pytest', %s, %s) RETURNING id",
        (name, f"pytest-{name}"),
    ).fetchone()[0]


def add_swipe(conn, user_id, item_id, liked, age):
    conn.execute(
        "INSERT INTO swipes (user_id, item_id, liked, created_at) VALUES (%s, %s, %s, now() - %s::interval)",
        (user_id, item_id, liked, age),
    )


@needs_scratch_db
def test_likes_are_latest_liked_swipes_newest_first(conn):
    user_id = conn.execute(
        "INSERT INTO users (email, auth_id) VALUES ('pytest-likes@example.test', %s) RETURNING id",
        (AUTH_ID,),
    ).fetchone()[0]
    a = make_item(conn, "a")
    b = make_item(conn, "b")
    c = make_item(conn, "c")
    d = make_item(conn, "d")
    add_swipe(conn, user_id, a, True, "3 days")
    add_swipe(conn, user_id, a, False, "2 days")
    add_swipe(conn, user_id, b, True, "1 day")
    add_swipe(conn, user_id, c, True, "2 hours")
    add_swipe(conn, user_id, d, False, "1 hour")
    rows = get_likes(conn, user_id, 50)
    titles = [r["title"] for r in rows if r["title"].startswith("pytest-")]
    assert titles == ["pytest-c", "pytest-b"]
    assert rows[0]["liked_at"] is not None


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


def signed_in(monkeypatch, profile):
    app.dependency_overrides[current_user] = lambda: {"auth_id": AUTH_ID, "token": "t"}
    app.dependency_overrides[get_conn] = lambda: None
    monkeypatch.setattr(main, "get_profile", lambda conn, auth_id: profile)


def test_likes_requires_a_token():
    assert client.get("/likes").status_code == 401


def test_likes_without_profile_is_404(monkeypatch):
    signed_in(monkeypatch, None)
    assert client.get("/likes").status_code == 404


def test_likes_returns_rows(monkeypatch):
    signed_in(monkeypatch, {"id": 5, "has_taste": True, "onboarded": True})
    monkeypatch.setattr(main, "get_likes", lambda conn, user_id, limit: [{"id": 7, "title": "Taco Place"}])
    response = client.get("/likes")
    assert response.status_code == 200
    assert response.json() == [{"id": 7, "title": "Taco Place"}]


def test_likes_rejects_bad_limit(monkeypatch):
    signed_in(monkeypatch, {"id": 5, "has_taste": True, "onboarded": True})
    assert client.get("/likes?limit=0").status_code == 422
