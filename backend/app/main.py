import psycopg
from fastapi import FastAPI, Depends

from backend.app.db import get_conn

app = FastAPI(title="Suggestor")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/db")
def health_db(conn: psycopg.Connection = Depends(get_conn)) -> dict[str, str]:
    conn.execute("SELECT 1")
    return {"status": "ok"}
