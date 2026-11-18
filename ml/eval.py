"""Offline eval scoreboard: random vs most-popular vs pretrained MiniLM, after N feed swipes.

Env: DATABASE_URL (read-only select on items).

CAVEATS (keep these in any report):
- Users are SYNTHETIC (hidden taste = a few cuisine tags + 10% noise). Proxy, not real people.
- "Popular" = likes per item among 100 separate synthetic users (still synthetic).
- Tags define both the users and the item text, so results are optimistic (circular).
"""
import os
from collections import Counter  # counts things for us

import numpy as np  # fast math on tables of numbers
import psycopg  # talks to Postgres

K = 20  # check the top 20 picks
N_USERS = 250  # fake users total
N_POP = 100  # first 100 build the popularity table, rest are scored
MAX_HELD = 50  # cap the answer key
CHECKPOINTS = [0, 10, 20, 50]  # feed swipes after onboarding
NOISE = 0.10  # 10% random mistakes in likes
HOLDOUT = 0.20  # hide 20% of likes as the answer key
W_LIKE, W_PASS = 1.0, -0.5  # like pulls toward, pass pushes away (half as hard)
SEED = 42  # same random numbers every run


# ---- Block 1: load items -------------------------------------------------
def load_items():
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:  # open DB, auto-close
        rows = conn.execute(
            "select id, tags, title, embedding, is_onboarding_seed from items order by id"
        ).fetchall()  # one tuple per restaurant, fixed order
    ids = np.array([r[0] for r in rows])  # column 0
    tags = [r[1] or [] for r in rows]  # cuisines, [] if missing
    titles = [r[2] for r in rows]  # restaurant names
    # embedding is text "[0.1,0.2,...]" -> strip brackets, split, make numbers
    E = np.array([np.array(r[3].strip("[]").split(","), dtype=float) for r in rows])
    seeds = np.array([bool(r[4]) for r in rows])  # True for the 5 seed items
    return ids, tags, titles, seeds, E


# ---- Block 2: synthetic users --------------------------------------------
def make_users(tags, rng):
    """Each user = set of 2-3 hidden cuisine tags (not too common, not too rare)."""
    counts = Counter(t for ts in tags for t in ts)  # items per tag
    vocab = sorted(t for t, c in counts.items() if 20 <= c <= 300)  # skip rare/huge tags
    # each user gets 2 or 3 random cuisines as secret taste
    return [set(rng.choice(vocab, size=rng.integers(2, 4), replace=False)) for _ in range(N_USERS)]


def true_likes(taste, tags, rng):
    """Bool per item: liked if any tag matches, then flip ~10% (noise)."""
    liked = np.array([bool(taste & set(ts)) for ts in tags])  # any tag matches = like
    flip = rng.random(len(liked)) < NOISE  # pick ~10% of items
    return liked ^ flip  # flip them (like <-> pass)


# ---- Block 3: taste vector from onboarding swipes ------------------------
def taste_vector(E, seed_idx, liked):
    """Mean of (+1.0 * liked emb, -0.5 * passed emb) over the seed swipes."""
    w = np.where(liked[seed_idx], W_LIKE, W_PASS)  # +1.0 or -0.5 per seed
    return (w[:, None] * E[seed_idx]).mean(axis=0)  # weight each, then average


# ---- Block 4: metrics ----------------------------------------------------
def top_k(scores, cand, k=K):
    s = np.where(cand, scores, -np.inf)  # banned items score worst
    return np.argpartition(-s, k)[:k]


def metrics(scores, cand, held_out):
    hits = np.isin(top_k(scores, cand), held_out).sum()
    return hits / len(held_out), hits / K  # recall@K, precision@K


# ---- Block 5: run everything ---------------------------------------------
def main():
    rng = np.random.default_rng(SEED)
    ids, tags, titles, seeds, E = load_items()
    En = E / np.linalg.norm(E, axis=1, keepdims=True)
    seed_idx = np.flatnonzero(seeds)
    tastes = make_users(tags, rng)
    likes = [true_likes(t, tags, rng) for t in tastes]

    # popularity = like count among the first N_POP users (never scored)
    pop_score = np.sum(likes[:N_POP], axis=0).astype(float)

    res = {m: {c: ([], []) for c in CHECKPOINTS} for m in ("random", "popular", "MiniLM")}
    for liked in likes[N_POP:]:
        pool = np.flatnonzero(liked & ~seeds)
        if len(pool) < MAX_HELD:
            continue
        rng.shuffle(pool)
        held_out = pool[:MAX_HELD]
        known = liked.copy()  # train likes: already owned, never ranked
        known[held_out] = False
        known |= seeds

        acc = taste_vector_sum = (np.where(liked[seed_idx], W_LIKE, W_PASS)[:, None] * En[seed_idx]).sum(0)
        seen = np.zeros(len(En), dtype=bool)
        feed_ok = ~known & ~np.isin(np.arange(len(En)), held_out)  # can be shown
        swipes = 0
        for c in CHECKPOINTS:
            while swipes < c:  # swipe the current top pick
                t = acc / np.linalg.norm(acc)
                j = top_k(En @ t, feed_ok & ~seen, 1)[0]
                seen[j] = True
                acc = acc + (W_LIKE if liked[j] else W_PASS) * En[j]
                swipes += 1
            cand = ~known & ~seen
            t = acc / np.linalg.norm(acc)
            for m, sc in (("MiniLM", En @ t), ("random", rng.random(len(En))),
                          ("popular", pop_score + rng.random(len(En)) * 0.01)):
                r, p = metrics(sc, cand, held_out)
                res[m][c][0].append(r)
                res[m][c][1].append(p)

    n = len(res["random"][0][0])
    print(f"\n{n} SYNTHETIC users (proxy). Recall@{K} / Precision@{K} by feed swipes after onboarding")
    print(f"{'method':<10}" + "".join(f"{'after '+str(c):>16}" for c in CHECKPOINTS))
    for m, d in res.items():
        print(f"{m:<10}" + "".join(f"{np.mean(d[c][0]):>8.3f}/{np.mean(d[c][1]):<7.3f}" for c in CHECKPOINTS))


if __name__ == "__main__":
    main()
