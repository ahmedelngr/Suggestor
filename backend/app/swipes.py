import json
import math
import os

from psycopg.rows import dict_row


def item_exists(conn, item_id):
    return conn.execute("SELECT 1 FROM items WHERE id = %s", (item_id,)).fetchone() is not None


def record_swipe(conn, user_id, item_id, liked):
    row = conn.execute(
        "INSERT INTO swipes (user_id, item_id, liked) VALUES (%s, %s, %s) RETURNING id",
        (user_id, item_id, liked),
    ).fetchone()
    return row[0]


def update_taste(conn, user_id):
    like_weight = float(os.environ.get("LIKE_WEIGHT", "1.0"))
    dislike_weight = float(os.environ.get("DISLIKE_WEIGHT", "0.5"))
    rows = conn.execute(
        """
        SELECT ls.liked, i.embedding::text
        FROM latest_swipes ls
        JOIN items i ON i.id = ls.item_id
        WHERE ls.user_id = %s AND i.embedding IS NOT NULL
        """,
        (user_id,),
    ).fetchall()
    if not rows:
        return
    total = None
    for liked, text in rows:
        weight = like_weight if liked else -dislike_weight
        vector = json.loads(text)
        if total is None:
            total = [0.0] * len(vector)
        for k, x in enumerate(vector):
            total[k] += weight * x
    norm = math.sqrt(sum(x * x for x in total))
    if norm == 0:
        return
    taste = [x / norm for x in total]
    conn.execute(
        "UPDATE users SET taste_vector = %s::vector WHERE id = %s",
        (json.dumps(taste), user_id),
    )


def get_likes(conn, user_id, limit):
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT i.id, i.title, i.description, i.latitude, i.longitude,
                   i.price_tier, i.tags, i.image_url, ls.created_at AS liked_at
            FROM latest_swipes ls
            JOIN items i ON i.id = ls.item_id
            WHERE ls.user_id = %s AND ls.liked
            ORDER BY ls.created_at DESC
            LIMIT %s
            """,
            (user_id, limit),
        )
        return cur.fetchall()
