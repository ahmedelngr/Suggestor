import math
import os

import psycopg
import pytest
from fastapi.testclient import TestClient

from backend.app import main
from backend.app.auth import current_user
from backend.app.db import get_conn
from backend.app.feed import DEFAULT_LAT, DEFAULT_LON, get_feed
from backend.app.main import app

client = TestClient(app)

TEST_DB = os.environ.get("TEST_DATABASE_URL", "")
AUTH_ID = "00000000-0000-0000-0000-000000000001"

needs_scratch_db = pytest.mark.skipif(
    not ("localhost" in TEST_DB or "127.0.0.1" in TEST_DB),
    reason="set TEST_DATABASE_URL to a local scratch Postgres to run this",
)


def reference_miles(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 3958.8 * 2 * math.asin(math.sqrt(a))


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
    monkeypatch.setattr(main, "get_feed", lambda conn, auth_id, limit, lat, lon: [{"id": 7, "title": "Taco Place"}])
    response = client.get("/feed")
    assert response.status_code == 200
    assert response.json()[0]["title"] == "Taco Place"


def test_feed_rejects_bad_limit(monkeypatch):
    feed_as_test_user(monkeypatch, {"id": 1, "has_taste": True})
    assert client.get("/feed?limit=0").status_code == 422


def capture_feed_args(monkeypatch):
    seen = {}

    def fake_get_feed(conn, auth_id, limit, lat, lon):
        seen.update(lat=lat, lon=lon)
        return []

    monkeypatch.setattr(main, "get_feed", fake_get_feed)
    return seen


def test_feed_falls_back_to_cal_poly_pomona(monkeypatch):
    feed_as_test_user(monkeypatch, {"id": 1, "has_taste": True})
    seen = capture_feed_args(monkeypatch)
    assert client.get("/feed").status_code == 200
    assert seen == {"lat": DEFAULT_LAT, "lon": DEFAULT_LON}


def test_feed_uses_the_given_location(monkeypatch):
    feed_as_test_user(monkeypatch, {"id": 1, "has_taste": True})
    seen = capture_feed_args(monkeypatch)
    assert client.get("/feed?lat=34.1&lon=-117.9").status_code == 200
    assert seen == {"lat": 34.1, "lon": -117.9}


def test_feed_needs_both_lat_and_lon(monkeypatch):
    feed_as_test_user(monkeypatch, {"id": 1, "has_taste": True})
    assert client.get("/feed?lat=34.1").status_code == 422
    assert client.get("/feed?lon=-117.9").status_code == 422


def test_feed_rejects_out_of_range_location(monkeypatch):
    feed_as_test_user(monkeypatch, {"id": 1, "has_taste": True})
    assert client.get("/feed?lat=91&lon=0").status_code == 422
    assert client.get("/feed?lat=0&lon=181").status_code == 422


@needs_scratch_db
def test_feed_miles_match_a_reference_haversine(conn):
    user_id = conn.execute(
        "INSERT INTO users (email, auth_id, taste_vector) VALUES ('pytest-miles@example.test', %s, %s::vector) RETURNING id",
        ("00000000-0000-0000-0000-000000000009", vec(1.0, 0.0)),
    ).fetchone()[0]
    assert user_id
    places = {"downtown": (34.0522, -118.2437), "ontario": (34.0633, -117.6509), "nowhere": (None, None)}
    for name, (lat, lon) in places.items():
        conn.execute(
            "INSERT INTO items (type, source, source_id, title, latitude, longitude, embedding) "
            "VALUES ('restaurant', 'pytest', %s, %s, %s, %s, %s::vector)",
            (name, f"pytest-miles-{name}", lat, lon, vec(1.0, 0.0)),
        )
    rows = {r["title"]: r for r in get_feed(conn, "00000000-0000-0000-0000-000000000009", 50, 34.0575, -117.8210)}
    assert rows["pytest-miles-nowhere"]["miles"] is None
    for name in ("downtown", "ontario"):
        lat, lon = places[name]
        assert rows[f"pytest-miles-{name}"]["miles"] == pytest.approx(reference_miles(34.0575, -117.8210, lat, lon), abs=0.01)
    assert 20 < rows["pytest-miles-downtown"]["miles"] < 30
