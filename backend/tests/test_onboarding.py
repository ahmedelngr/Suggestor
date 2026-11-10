import os

import psycopg
import pytest
from fastapi.testclient import TestClient

from backend.app import main
from backend.app.auth import current_user
from backend.app.db import get_conn
from backend.app.main import app
from backend.app.onboarding import get_onboarding_items, mark_onboarded, swipe_count

client = TestClient(app)

TEST_DB = os.environ.get("TEST_DATABASE_URL", "")
AUTH_ID = "00000000-0000-0000-0000-000000000003"

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


def make_user(conn):
    return conn.execute(
        "INSERT INTO users (email, auth_id) VALUES ('pytest-onboarding@example.test', %s) RETURNING id",
        (AUTH_ID,),
    ).fetchone()[0]


def make_item(conn, name, seed):
    return conn.execute(
        "INSERT INTO items (type, source, source_id, title, is_onboarding_seed) VALUES ('restaurant', 'pytest', %s, %s, %s) RETURNING id",
        (name, f"pytest-{name}", seed),
    ).fetchone()[0]


@needs_scratch_db
def test_onboarding_items_are_only_the_seeds(conn):
    make_item(conn, "seed", True)
    make_item(conn, "other", False)
    titles = [r["title"] for r in get_onboarding_items(conn) if r["title"].startswith("pytest-")]
    assert titles == ["pytest-seed"]


@needs_scratch_db
def test_swipe_count_counts_each_restaurant_once(conn):
    user_id = make_user(conn)
    a = make_item(conn, "a", True)
    b = make_item(conn, "b", True)
    for item, liked, age in [(a, True, "3 days"), (a, False, "2 days"), (b, True, "1 day")]:
        conn.execute(
            "INSERT INTO swipes (user_id, item_id, liked, created_at) VALUES (%s, %s, %s, now() - %s::interval)",
            (user_id, item, liked, age),
        )
    assert swipe_count(conn, user_id) == 2


@needs_scratch_db
def test_mark_onboarded_sets_the_time_only_once(conn):
    user_id = make_user(conn)
    mark_onboarded(conn, user_id)
    conn.execute("UPDATE users SET onboarded_at = now() - interval '1 day' WHERE id = %s", (user_id,))
    mark_onboarded(conn, user_id)
    older = conn.execute(
        "SELECT onboarded_at < now() - interval '12 hours' FROM users WHERE id = %s", (user_id,)
    ).fetchone()[0]
    assert older is True


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


def test_onboarding_requires_a_token():
    assert client.get("/onboarding").status_code == 401


def test_onboarding_returns_the_seed_restaurants(monkeypatch):
    app.dependency_overrides[current_user] = lambda: {"auth_id": AUTH_ID, "token": "t"}
    app.dependency_overrides[get_conn] = lambda: None
    monkeypatch.setattr(main, "get_onboarding_items", lambda conn: [{"id": 1, "title": "Taco Place"}])
    response = client.get("/onboarding")
    assert response.status_code == 200
    assert response.json() == [{"id": 1, "title": "Taco Place"}]
