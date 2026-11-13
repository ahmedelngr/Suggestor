import os

import httpx
import psycopg
from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel

from backend.app.auth import current_user, supabase_headers
from backend.app.db import get_conn
from backend.app.feed import get_feed, get_profile
from backend.app.onboarding import (
    ONBOARDING_SWIPES,
    get_onboarding_items,
    mark_onboarded,
    swipe_count,
)
from backend.app.swipes import item_exists, record_swipe, update_taste, get_likes

app = FastAPI(title="Suggestor")


class SwipeIn(BaseModel):
    item_id: int
    liked: bool


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/db")
def health_db(conn: psycopg.Connection = Depends(get_conn)) -> dict[str, str]:
    conn.execute("SELECT 1")
    return {"status": "ok"}


@app.get("/me")
def me(user: dict[str, str] = Depends(current_user)) -> dict:
    url = f"{os.environ['SUPABASE_URL']}/rest/v1/users"
    resp = httpx.get(
        url,
        params={"select": "id,first_name,last_name,email,onboarded_at"},
        headers=supabase_headers(user["token"]),
        timeout=10,
    )

    if resp.status_code == 401:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Could not reach the profile service")
    rows = resp.json()
    if not rows:
        raise HTTPException(status_code=404, detail="Profile not found")
    profile = rows[0]
    return {**profile, "onboarded": profile.get("onboarded_at") is not None}


@app.get("/feed")
def feed(
    limit: int = Query(20, ge=1, le=50),
    user: dict[str, str] = Depends(current_user),
    conn: psycopg.Connection = Depends(get_conn),
) -> list[dict]:
    profile = get_profile(conn, user["auth_id"])
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    if not profile["has_taste"]:
        raise HTTPException(status_code=409, detail="Finish onboarding first")
    return get_feed(conn, user["auth_id"], limit)


@app.post("/swipes", status_code=201)
def swipe(
    body: SwipeIn,
    user: dict[str, str] = Depends(current_user),
    conn: psycopg.Connection = Depends(get_conn),
) -> dict:
    profile = get_profile(conn, user["auth_id"])
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    if not item_exists(conn, body.item_id):
        raise HTTPException(status_code=404, detail="Item not found")
    swipe_id = record_swipe(conn, profile["id"], body.item_id, body.liked)
    onboarded = profile["onboarded"]
    if not onboarded and swipe_count(conn, profile["id"]) >= ONBOARDING_SWIPES:
        mark_onboarded(conn, profile["id"])
        onboarded = True
    if onboarded:
        update_taste(conn, profile["id"])
    return {"id": swipe_id, "item_id": body.item_id, "liked": body.liked, "onboarded": onboarded}


@app.get("/onboarding")
def onboarding(
    user: dict[str, str] = Depends(current_user),
    conn: psycopg.Connection = Depends(get_conn),
) -> list[dict]:
    return get_onboarding_items(conn)


@app.get("/likes")
def likes(
    limit: int = Query(100, ge=1, le=200),
    user: dict[str, str] = Depends(current_user),
    conn: psycopg.Connection = Depends(get_conn),
) -> list[dict]:
    profile = get_profile(conn, user["auth_id"])
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return get_likes(conn, profile["id"], limit)
