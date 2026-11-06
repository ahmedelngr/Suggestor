"""Load Pomona-area restaurants from the Foursquare OS Places dataset into `items`.

Source: https://huggingface.co/datasets/foursquare/fsq-os-places (Apache-2.0, gated).
Only the rows we need are read, using DuckDB's remote Parquet reads, so the 263 GB
dataset is never downloaded.

Run from the repo root (see data/README.md):
    python data/load_places.py --describe     # show columns, no database needed
    python data/load_places.py --dry-run      # query and print a sample, no writes
    python data/load_places.py                # query and upsert into `items`

Env (in .env, never committed): HF_TOKEN, DATABASE_URL.
"""
import argparse
import math
import os
import re
import sys

import duckdb

RELEASE = "2026-10-15"
HF_BASE = f"hf://datasets/foursquare/fsq-os-places/release/dt={RELEASE}"
RESTAURANTS_LEVEL2 = "4d4b7105d754a06374d81259"  # Foursquare "Dining and Drinking"

# Cal Poly Pomona and the search radius (miles).
CENTER_LAT, CENTER_LON, RADIUS_MI = 34.0575, -117.8210, 15.0
LAT_DEG = RADIUS_MI / 69.0
LON_DEG = RADIUS_MI / (69.0 * math.cos(math.radians(CENTER_LAT)))

SOURCE = "fsq_os"
NEEDED = {"fsq_place_id", "name", "latitude", "longitude", "locality", "region",
          "date_closed", "fsq_category_ids", "fsq_category_labels"}


def miles_between(lat1, lon1, lat2, lon2):
    """Haversine distance in miles."""
    lat1, lon1, lat2, lon2 = map(float, (lat1, lon1, lat2, lon2))
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 3958.8 * 2 * math.asin(math.sqrt(a))


def connect_duckdb(local_dir):
    con = duckdb.connect()
    if local_dir:
        return con
    token = os.environ.get("HF_TOKEN", "")
    if not re.fullmatch(r"[A-Za-z0-9_\-]+", token):
        sys.exit("HF_TOKEN is missing or malformed. Put it in .env (never in git).")
    con.execute(f"CREATE SECRET hf (TYPE HUGGINGFACE, TOKEN '{token}')")
    return con


def sources(local_dir):
    if local_dir:
        return f"{local_dir}/places/*.parquet", f"{local_dir}/categories/*.parquet"
    return f"{HF_BASE}/places/parquet/*.parquet", f"{HF_BASE}/categories/parquet/*.parquet"


def describe(con, places):
    cols = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{places}')").fetchall()
    for name, ctype, *_ in cols:
        print(f"{name:28} {ctype}")
    missing = NEEDED - {c[0] for c in cols}
    print("\nmissing columns we need:", sorted(missing) or "none")


def fetch_restaurants(con, places, cats):
    sql = f"""
    SELECT fsq_place_id, name, latitude, longitude, locality, region, fsq_category_labels
    FROM read_parquet('{places}')
    WHERE latitude  BETWEEN {CENTER_LAT - LAT_DEG} AND {CENTER_LAT + LAT_DEG}
      AND longitude BETWEEN {CENTER_LON - LON_DEG} AND {CENTER_LON + LON_DEG}
      AND date_closed IS NULL
      AND list_has_any(
            fsq_category_ids,
            (SELECT list(category_id) FROM read_parquet('{cats}')
             WHERE level2_category_id = '{RESTAURANTS_LEVEL2}'))
    """
    rows = con.execute(sql).fetchall()
    return [r for r in rows
            if miles_between(CENTER_LAT, CENTER_LON, r[2], r[3]) <= RADIUS_MI]


def to_item(row):
    place_id, name, lat, lon, locality, region, labels = row
    # Labels look like "Dining and Drinking > Restaurant > Mexican Restaurant".
    leaves = sorted({(l.split(">")[-1]).strip() for l in (labels or [])})
    where = ", ".join(x for x in (locality, region) if x)
    kind = leaves[0] if leaves else "Restaurant"
    return {
        "source_id": place_id,
        "title": name,
        "description": f"{kind} in {where}" if where else kind,
        "latitude": float(lat),
        "longitude": float(lon),
        "tags": leaves,
    }


UPSERT = """
INSERT INTO items (type, source, source_id, title, description, latitude, longitude, tags)
VALUES ('restaurant', %(source)s, %(source_id)s, %(title)s, %(description)s,
        %(latitude)s, %(longitude)s, %(tags)s)
ON CONFLICT (source, source_id) DO UPDATE SET
    title = EXCLUDED.title, description = EXCLUDED.description,
    latitude = EXCLUDED.latitude, longitude = EXCLUDED.longitude, tags = EXCLUDED.tags
"""  # embedding is deliberately not touched: Modeling fills it later.


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--describe", action="store_true", help="print columns and exit")
    ap.add_argument("--dry-run", action="store_true", help="query, print sample, no writes")
    ap.add_argument("--local-dir", help="read local Parquet (places/, categories/) instead of Hugging Face")
    args = ap.parse_args()

    con = connect_duckdb(args.local_dir)
    places, cats = sources(args.local_dir)

    if args.describe:
        describe(con, places)
        return

    items = [to_item(r) for r in fetch_restaurants(con, places, cats)]
    print(f"{len(items)} restaurants within {RADIUS_MI:g} miles of Cal Poly Pomona")
    for it in items[:5]:
        print(" ", it["title"], "|", it["description"], "|", it["tags"])
    if args.dry_run or not items:
        return

    import psycopg  # imported late so --describe and --dry-run need no database

    url = os.environ.get("DATABASE_URL")
    if not url:
        sys.exit("DATABASE_URL is missing. Put it in .env (never in git).")
    with psycopg.connect(url) as conn, conn.cursor() as cur:
        cur.executemany(UPSERT, [{**it, "source": SOURCE} for it in items])
    print(f"upserted {len(items)} rows into items (source='{SOURCE}')")


if __name__ == "__main__":
    main()
