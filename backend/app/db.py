import os

import psycopg


def get_conn():
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        yield conn