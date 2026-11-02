import os

import psycopg
import pytest
from fastapi.testclient import TestClient

from backend.app import main
from backend.app.auth import current_user
from backend.app.db import get_conn
from backend.app.feed import get_feed
from backend.app.main import app

client = TestClient(app)

TEST_DB = os.environ.get("TEST_DATABASE_URL", "")
AUTH_ID = "00000000-0000-0000-0000-000000000001"

needs_scratch_db = pytest.mark.skipif(
    not ("localhost" in TEST_DB or "127.0.0.1" in TEST_DB),
    reason="set TEST_DATABASE_URL to a local scratch Postgres to run this",
)


def vec(a, b):
    return "[" + ",".join(str(x) for x in [a, b] + [0] * 382) + "]"


@pytest.fixture
def conn():
    c = psycopg.connect(TEST_DB)
    yield c
    c.rollback()
    c.close()


@needs_scratch_db
def test_feed_ranks_by_taste_and_hides_recent_swipes(conn):
    user_id = conn.execute(
        "INSERT INTO users (email, auth_id, taste_vector) VALUES ('pytest@example.test', %s, %s::vector) RETURNING id",
        (AUTH_ID, vec(1.0, 0.2)),
    ).fetchone()[0]
    ids = {}
    for name, v in [("taco", vec(1.0, 0.0)), ("burrito", vec(0.9, 0.1)), ("sushi", vec(0.0, 1.0))]:
        ids[name] = conn.execute(
            "INSERT INTO items (type, source, source_id, title, embedding) VALUES ('restaurant', 'pytest', %s, %s, %s::vector) RETURNING id",
            (name, f"pytest-{name}", v),
        ).fetchone()[0]
    conn.execute("INSERT INTO swipes (user_id, item_id, liked) VALUES (%s, %s, true)", (user_id, ids["burrito"]))
    conn.execute(
        "INSERT INTO swipes (user_id, item_id, liked, created_at) VALUES (%s, %s, false, now() - interval '20 days')",
        (user_id, ids["taco"]),
    )
    rows = get_feed(conn, AUTH_ID, 50)
    titles = [r["title"] for r in rows if r["title"].startswith("pytest-")]
    assert titles == ["pytest-taco", "pytest-sushi"]


def feed_as_test_user(monkeypatch, profile):
    app.dependency_overrides[current_user] = lambda: {"auth_id": AUTH_ID, "token": "t"}
    app.dependency_overrides[get_conn] = lambda: None
    monkeypatch.setattr(main, "get_profile", lambda conn, auth_id: profile)


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


def test_feed_without_profile_is_404(monkeypatch):
    feed_as_test_user(monkeypatch, None)
    assert client.get("/feed").status_code == 404


def test_feed_without_taste_is_409(monkeypatch):
    feed_as_test_user(monkeypatch, {"id": 1, "has_taste": False})
    assert client.get("/feed").status_code == 409


def test_feed_returns_rows(monkeypatch):
    feed_as_test_user(monkeypatch, {"id": 1, "has_taste": True})
    monkeypatch.setattr(main, "get_feed", lambda conn, auth_id, limit: [{"id": 7, "title": "Taco Place"}])
    response = client.get("/feed")
    assert response.status_code == 200
    assert response.json()[0]["title"] == "Taco Place"


def test_feed_rejects_bad_limit(monkeypatch):
    feed_as_test_user(monkeypatch, {"id": 1, "has_taste": True})
    assert client.get("/feed?limit=0").status_code == 422