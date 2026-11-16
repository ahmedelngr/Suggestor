import os
import threading

from psycopg_pool import ConnectionPool

_pool = None
_lock = threading.Lock()


def get_pool():
    """One shared pool, created on first use so importing the app needs no database."""
    global _pool
    with _lock:
        if _pool is None:
            _pool = ConnectionPool(
                os.environ["DATABASE_URL"],
                min_size=1,
                max_size=5,
                timeout=10,
                check=ConnectionPool.check_connection,
                open=False,
            )
            _pool.open()
        return _pool


def get_conn():
    # Borrow a connection: committed if the request succeeds, rolled back if it fails.
    with get_pool().connection() as conn:
        yield conn
