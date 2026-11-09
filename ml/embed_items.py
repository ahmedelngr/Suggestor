"""Fill items.embedding with pretrained all-MiniLM-L6-v2 (384-dim). This is the baseline.

Run from repo root:  python ml/embed_items.py [--all]
Env: DATABASE_URL. Only rows with embedding IS NULL are embedded unless --all.
"""
import argparse
import os
import sys

import psycopg
from sentence_transformers import SentenceTransformer

MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def item_text(title, description, tags):
    parts = [title, description or "", ", ".join(tags or [])]
    return ". ".join(p for p in parts if p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="re-embed every item")
    args = ap.parse_args()
    url = os.environ.get("DATABASE_URL")
    if not url:
        sys.exit("DATABASE_URL is missing. Put it in .env (never in git).")

    model = SentenceTransformer(MODEL)
    where = "" if args.all else "WHERE embedding IS NULL"
    with psycopg.connect(url) as conn:
        rows = conn.execute(f"SELECT id, title, description, tags FROM items {where}").fetchall()
        print(f"embedding {len(rows)} items")
        for start in range(0, len(rows), 256):
            batch = rows[start:start + 256]
            vecs = model.encode([item_text(*r[1:]) for r in batch], normalize_embeddings=True)
            conn.cursor().executemany(
                "UPDATE items SET embedding = %s::vector WHERE id = %s",
                [("[" + ",".join(f"{x:.6f}" for x in v) + "]", r[0]) for v, r in zip(vecs, batch)],
            )
    print("done")


if __name__ == "__main__":
    main()
