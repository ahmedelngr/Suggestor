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
def test_taste_is_normalized_weighted_sum_and_latest_swipe_wins(conn):
    user_id = make_user(conn)
    taco = make_item(conn, "taco", vec(1.0, 0.0))
    sushi = make_item(conn, "sushi", vec(0.0, 1.0))
    add_swipe(conn, user_id, taco, True, "2 days")
    add_swipe(conn, user_id, sushi, False, "1 day")
    update_taste(conn, user_id)
    assert first_two(conn, user_id) == pytest.approx([0.894427, -0.447214], abs=1e-5)

    add_swipe(conn, user_id, taco, False, "0 days")
    update_taste(conn, user_id)
    assert first_two(conn, user_id) == pytest.approx([-0.707107, -0.707107], abs=1e-5)


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


def track_calls(monkeypatch, swipes_done=0):
    calls = []
    monkeypatch.setattr(main, "record_swipe", lambda conn, uid, iid, liked: calls.append("record") or 42)
    monkeypatch.setattr(main, "swipe_count", lambda conn, uid: swipes_done)
    monkeypatch.setattr(main, "mark_onboarded", lambda conn, uid: calls.append("mark_onboarded"))
    monkeypatch.setattr(main, "update_taste", lambda conn, uid: calls.append("taste"))
    return calls


def test_swipe_without_profile_is_404(monkeypatch):
    signed_in(monkeypatch, None)
    assert client.post("/swipes", json={"item_id": 1, "liked": True}).status_code == 404


def test_swipe_on_missing_item_is_404(monkeypatch):
    signed_in(monkeypatch, {"id": 1, "has_taste": False, "onboarded": False}, item_found=False)
    assert client.post("/swipes", json={"item_id": 99, "liked": True}).status_code == 404


def test_swipe_during_onboarding_does_not_build_taste(monkeypatch):
    signed_in(monkeypatch, {"id": 5, "has_taste": False, "onboarded": False})
    calls = track_calls(monkeypatch, swipes_done=3)
    response = client.post("/swipes", json={"item_id": 3, "liked": False})
    assert response.status_code == 201
    assert response.json() == {"id": 42, "item_id": 3, "liked": False, "onboarded": False}
    assert calls == ["record"]


def test_fifth_swipe_finishes_onboarding_and_builds_taste(monkeypatch):
    signed_in(monkeypatch, {"id": 5, "has_taste": False, "onboarded": False})
    calls = track_calls(monkeypatch, swipes_done=5)
    response = client.post("/swipes", json={"item_id": 3, "liked": True})
    assert response.status_code == 201
    assert response.json()["onboarded"] is True
    assert calls == ["record", "mark_onboarded", "taste"]


def test_swipe_after_onboarding_updates_taste(monkeypatch):
    signed_in(monkeypatch, {"id": 5, "has_taste": True, "onboarded": True})
    calls = track_calls(monkeypatch, swipes_done=9)
    response = client.post("/swipes", json={"item_id": 3, "liked": True})
    assert response.status_code == 201
    assert response.json()["onboarded"] is True
    assert calls == ["record", "taste"]


def test_swipe_rejects_bad_body(monkeypatch):
    signed_in(monkeypatch, {"id": 1, "has_taste": True, "onboarded": True})
    assert client.post("/swipes", json={"item_id": "x"}).status_code == 422
