import json
import os

import psycopg
import pytest
from fastapi.testclient import TestClient

from backend.app import main
from backend.app.auth import current_user
from backend.app.db import get_conn
from backend.app.main import app
from backend.app.swipes import record_swipe, update_taste

client = TestClient(app)

TEST_DB = os.environ.get("TEST_DATABASE_URL", "")
AUTH_ID = "00000000-0000-0000-0000-000000000002"

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


def make_user(conn):
    return conn.execute(
        "INSERT INTO users (email, auth_id) VALUES ('pytest-swipes@example.test', %s) RETURNING id",
        (AUTH_ID,),
    ).fetchone()[0]


def make_item(conn, name, embedding):
    return conn.execute(
        "INSERT INTO items (type, source, source_id, title, embedding) VALUES ('restaurant', 'pytest', %s, %s, %s::vector) RETURNING id",
        (name, f"pytest-{name}", embedding),
    ).fetchone()[0]


def add_swipe(conn, user_id, item_id, liked, age):
    conn.execute(
        "INSERT INTO swipes (user_id, item_id, liked, created_at) VALUES (%s, %s, %s, now() - %s::interval)",
        (user_id, item_id, liked, age),
    )


def first_two(conn, user_id):
    text = conn.execute("SELECT taste_vector::text FROM users WHERE id = %s", (user_id,)).fetchone()[0]
    return json.loads(text)[:2]


@needs_scratch_db
def test_taste_is_weighted_average_and_latest_swipe_wins(conn):
    user_id = make_user(conn)
    taco = make_item(conn, "taco", vec(1.0, 0.0))
    sushi = make_item(conn, "sushi", vec(0.0, 1.0))
    add_swipe(conn, user_id, taco, True, "2 days")
    add_swipe(conn, user_id, sushi, False, "1 day")
    update_taste(conn, user_id)
    assert first_two(conn, user_id) == pytest.approx([0.5, -0.25])

    add_swipe(conn, user_id, taco, False, "0 days")
    update_taste(conn, user_id)
    assert first_two(conn, user_id) == pytest.approx([-0.25, -0.25])


@needs_scratch_db
def test_record_swipe_returns_new_id(conn):
    user_id = make_user(conn)
    taco = make_item(conn, "taco", vec(1.0, 0.0))
    assert isinstance(record_swipe(conn, user_id, taco, True), int)


@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()


def signed_in(monkeypatch, profile, item_found=True):
    app.dependency_overrides[current_user] = lambda: {"auth_id": AUTH_ID, "token": "t"}
    app.dependency_overrides[get_conn] = lambda: None
    monkeypatch.setattr(main, "get_profile", lambda conn, auth_id: profile)
    monkeypatch.setattr(main, "item_exists", lambda conn, item_id: item_found)


def test_swipe_without_profile_is_404(monkeypatch):
    signed_in(monkeypatch, None)
    assert client.post("/swipes", json={"item_id": 1, "liked": True}).status_code == 404


def test_swipe_on_missing_item_is_404(monkeypatch):
    signed_in(monkeypatch, {"id": 1, "has_taste": False}, item_found=False)
    assert client.post("/swipes", json={"item_id": 99, "liked": True}).status_code == 404


def test_swipe_records_and_updates_taste(monkeypatch):
    signed_in(monkeypatch, {"id": 5, "has_taste": False})
    calls = []

    def fake_record(conn, user_id, item_id, liked):
        calls.append(("record", user_id, item_id, liked))
        return 42

    def fake_update(conn, user_id):
        calls.append(("taste", user_id))

    monkeypatch.setattr(main, "record_swipe", fake_record)
    monkeypatch.setattr(main, "update_taste", fake_update)
    response = client.post("/swipes", json={"item_id": 3, "liked": False})
    assert response.status_code == 201
    assert response.json() == {"id": 42, "item_id": 3, "liked": False}
    assert calls == [("record", 5, 3, False), ("taste", 5)]


def test_swipe_rejects_bad_body(monkeypatch):
    signed_in(monkeypatch, {"id": 1, "has_taste": True})
    assert client.post("/swipes", json={"item_id": "x"}).status_code == 422
