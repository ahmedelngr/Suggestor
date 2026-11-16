import os

import pytest

from backend.app import db

TEST_DB = os.environ.get("TEST_DATABASE_URL", "")

needs_scratch_db = pytest.mark.skipif(
    not ("localhost" in TEST_DB or "127.0.0.1" in TEST_DB),
    reason="set TEST_DATABASE_URL to a local scratch Postgres to run this",
)


@pytest.fixture
def pool_on_scratch_db(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", TEST_DB)
    monkeypatch.setattr(db, "_pool", None)
    yield
    if db._pool is not None:
        db._pool.close()


def database_session_used_by_one_request():
    request = db.get_conn()
    conn = next(request)
    pid = conn.execute("SELECT pg_backend_pid()").fetchone()[0]
    next(request, None)  # the request ends and the connection goes back to the pool
    return pid


@needs_scratch_db
def test_requests_share_a_few_connections(pool_on_scratch_db):
    sessions = {database_session_used_by_one_request() for _ in range(12)}
    assert len(sessions) <= db.get_pool().max_size


@needs_scratch_db
def test_there_is_one_shared_pool(pool_on_scratch_db):
    assert db.get_pool() is db.get_pool()
