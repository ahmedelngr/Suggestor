import os

from psycopg.rows import dict_row

# Cal Poly Pomona, the same centre the data loader uses.
DEFAULT_LAT = 34.0575
DEFAULT_LON = -117.8210

FEED_SQL = """
WITH me AS (
    SELECT id, taste_vector FROM users WHERE auth_id = %(auth_id)s::uuid
)
SELECT i.id, i.title, i.description, i.latitude, i.longitude,
       i.price_tier, i.tags, i.image_url,
       i.embedding <=> me.taste_vector AS distance,
       CASE WHEN i.latitude IS NULL OR i.longitude IS NULL THEN NULL ELSE
           3958.8 * 2 * asin(least(1.0, sqrt(
               power(sin(radians(i.latitude - %(lat)s) / 2), 2)
               + cos(radians(%(lat)s)) * cos(radians(i.latitude))
                 * power(sin(radians(i.longitude - %(lon)s) / 2), 2)
           )))
       END AS miles
FROM me, items i
WHERE i.type = 'restaurant'
  AND i.embedding IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM swipes s
      WHERE s.user_id = me.id
        AND s.item_id = i.id
        AND s.created_at > now() - make_interval(days => %(cooldown_days)s)
  )
ORDER BY i.embedding <=> me.taste_vector
LIMIT %(limit)s
"""


def get_profile(conn, auth_id):
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "SELECT id, taste_vector IS NOT NULL AS has_taste, onboarded_at IS NOT NULL AS onboarded "
            "FROM users WHERE auth_id = %s::uuid",
            (auth_id,),
        )
        return cur.fetchone()


def get_feed(conn, auth_id, limit, lat=DEFAULT_LAT, lon=DEFAULT_LON):
    cooldown_days = int(os.environ.get("COOLDOWN_DAYS", "14"))
    params = {
        "auth_id": auth_id,
        "cooldown_days": cooldown_days,
        "limit": limit,
        "lat": lat,
        "lon": lon,
    }
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(FEED_SQL, params)
        return cur.fetchall()
