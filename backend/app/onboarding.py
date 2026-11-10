from psycopg.rows import dict_row

ONBOARDING_SWIPES = 5


def get_onboarding_items(conn):
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT id, title, description, latitude, longitude, price_tier, tags, image_url
            FROM items
            WHERE is_onboarding_seed
            ORDER BY id
            """
        )
        return cur.fetchall()


def swipe_count(conn, user_id):
    row = conn.execute("SELECT count(*) FROM latest_swipes WHERE user_id = %s", (user_id,)).fetchone()
    return row[0]


def mark_onboarded(conn, user_id):
    conn.execute(
        "UPDATE users SET onboarded_at = now() WHERE id = %s AND onboarded_at IS NULL",
        (user_id,),
    )
