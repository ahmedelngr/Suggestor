"""Row Level Security: one user must not be able to read or change another user's data.

RLS only exists on Supabase, so this test builds a small stand-in for Supabase's
`auth` schema and roles in a throwaway database, then applies the real migrations
(001, 002 and 003) and checks the real policies. It needs a local Postgres with
pgvector and a superuser, and never touches any other database.
"""
import os
import uuid
from pathlib import Path

import psycopg
import pytest
from psycopg.conninfo import make_conninfo

TEST_DB = os.environ.get("TEST_DATABASE_URL", "")
MIGRATIONS = Path(__file__).resolve().parents[1] / "db" / "migrations"

needs_scratch_db = pytest.mark.skipif(
    not ("localhost" in TEST_DB or "127.0.0.1" in TEST_DB),
    reason="set TEST_DATABASE_URL to a local scratch Postgres to run this",
)

# A tiny stand-in for what Supabase provides.
SUPABASE_STAND_IN = """
DO $$ BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'anon') THEN CREATE ROLE anon NOLOGIN; END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'authenticated') THEN CREATE ROLE authenticated NOLOGIN; END IF;
END $$;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE SCHEMA auth;
CREATE TABLE auth.users (id uuid PRIMARY KEY, email text, raw_user_meta_data jsonb);
CREATE FUNCTION auth.uid() RETURNS uuid LANGUAGE sql STABLE AS
    $$ SELECT nullif(current_setting('request.jwt.claim.sub', true), '')::uuid $$;
GRANT USAGE ON SCHEMA auth, public TO anon, authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO anon, authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO anon, authenticated;
"""


@pytest.fixture
def db():
    name = "rls_test_" + uuid.uuid4().hex[:8]
    with psycopg.connect(TEST_DB, autocommit=True) as admin:
        admin.execute(f'CREATE DATABASE "{name}"')
    conn = psycopg.connect(make_conninfo(TEST_DB, dbname=name))
    try:
        conn.execute(SUPABASE_STAND_IN)
        for migration in ("001_init.sql", "002_accounts_and_onboarding.sql", "003_supabase_auth_and_rls.sql"):
            conn.execute((MIGRATIONS / migration).read_text(encoding="utf-8"))
        yield conn
    finally:
        conn.close()
        with psycopg.connect(TEST_DB, autocommit=True) as admin:
            admin.execute(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)')


@pytest.fixture
def two_users(db):
    """User A and user B, each with a profile row (made by the sign-up trigger) and two swipes."""
    ids = {}
    for who in ("a", "b"):
        auth_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO auth.users (id, email, raw_user_meta_data) VALUES (%s, %s, %s::jsonb)",
            (auth_id, f"{who}@example.test", '{"first_name": "' + who + '"}'),
        )
        profile_id = db.execute("SELECT id FROM users WHERE auth_id = %s", (auth_id,)).fetchone()[0]
        ids[who] = {"auth_id": auth_id, "profile_id": profile_id}
    items = [
        db.execute(
            "INSERT INTO items (type, source, source_id, title) VALUES ('restaurant', 'pytest', %s, %s) RETURNING id",
            (name, name),
        ).fetchone()[0]
        for name in ("one", "two")
    ]
    for who in ("a", "b"):
        for item_id in items:
            db.execute(
                "INSERT INTO swipes (user_id, item_id, liked) VALUES (%s, %s, true)",
                (ids[who]["profile_id"], item_id),
            )
    return ids


def act_as(db, auth_id):
    """Behave like a signed-in Supabase user: the `authenticated` role plus that user's id."""
    db.execute("RESET ROLE")
    db.execute("SET LOCAL ROLE authenticated")
    db.execute("SELECT set_config('request.jwt.claim.sub', %s, true)", (auth_id,))


@needs_scratch_db
def test_user_a_only_reads_their_own_swipes(db, two_users):
    act_as(db, two_users["a"]["auth_id"])
    seen = {row[0] for row in db.execute("SELECT user_id FROM swipes").fetchall()}
    assert seen == {two_users["a"]["profile_id"]}
    assert two_users["b"]["profile_id"] not in seen


@needs_scratch_db
def test_user_a_only_reads_their_own_swipes_through_the_view(db, two_users):
    act_as(db, two_users["a"]["auth_id"])
    seen = {row[0] for row in db.execute("SELECT user_id FROM latest_swipes").fetchall()}
    assert seen == {two_users["a"]["profile_id"]}


@needs_scratch_db
def test_user_a_cannot_read_user_bs_profile(db, two_users):
    act_as(db, two_users["a"]["auth_id"])
    seen = {row[0] for row in db.execute("SELECT id FROM users").fetchall()}
    assert seen == {two_users["a"]["profile_id"]}


@needs_scratch_db
def test_user_a_cannot_insert_a_swipe_for_user_b(db, two_users):
    act_as(db, two_users["a"]["auth_id"])
    item_id = db.execute("SELECT id FROM items LIMIT 1").fetchone()[0]
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        with db.transaction():
            db.execute(
                "INSERT INTO swipes (user_id, item_id, liked) VALUES (%s, %s, false)",
                (two_users["b"]["profile_id"], item_id),
            )


@needs_scratch_db
def test_user_a_cannot_change_user_bs_swipes(db, two_users):
    act_as(db, two_users["a"]["auth_id"])
    result = db.execute("UPDATE swipes SET liked = false WHERE user_id = %s", (two_users["b"]["profile_id"],))
    assert result.rowcount == 0


@needs_scratch_db
def test_signed_out_visitors_cannot_read_swipes(db, two_users):
    db.execute("RESET ROLE")
    db.execute("SET LOCAL ROLE anon")
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        with db.transaction():
            db.execute("SELECT * FROM swipes")
