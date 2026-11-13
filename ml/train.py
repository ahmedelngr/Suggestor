"""Fine-tune all-MiniLM-L6-v2 on cuisine pairs and compare it to the pretrained model.

Run from repo root:  python ml/train.py
Env: DATABASE_URL (read-only use). Writes only to ml/out/ (gitignored). Never writes to the DB.

Idea: two restaurants that share a specific cuisine tag should be close in embedding space.
- Items are split 80/20 by id (fixed seed). Training pairs come from the 80% only.
- Loss: MultipleNegativesRankingLoss (other pairs in the batch act as negatives).
- Test: for each held-out item, are its nearest neighbours (among ALL items) the same cuisine?
  Metric = precision@10 on the 20% held-out items. Reported for pretrained AND fine-tuned.
Caveat: the "cuisine" truth here is the same tag metadata the pairs come from, so this is a proxy.
"""
import os
import random
import sys

import numpy as np
import psycopg
import torch
from datasets import Dataset
from sentence_transformers import (SentenceTransformer, SentenceTransformerTrainer,
                                   SentenceTransformerTrainingArguments, losses)
from sentence_transformers.training_args import BatchSamplers

BASE = "sentence-transformers/all-MiniLM-L6-v2"
OUT = "ml/out"
SEED = 42
GENERIC = {"Restaurant"}      # too vague to define a cuisine
HOLDOUT, TOPK = 0.20, 10


def item_text(title, description, tags):   # must match ml/embed_items.py
    return ". ".join(p for p in [title, description or "", ", ".join(tags or [])] if p)


def load():
    url = os.environ.get("DATABASE_URL") or sys.exit("DATABASE_URL missing (put it in .env)")
    with psycopg.connect(url) as c:
        return c.execute("SELECT id, title, description, tags FROM items WHERE source='fsq_os' ORDER BY id").fetchall()


def specific(tags):
    return {t for t in (tags or []) if t not in GENERIC}


def make_pairs(rows, train_idx, rng):
    by_tag = {}
    for i in train_idx:
        for t in specific(rows[i][3]):
            by_tag.setdefault(t, []).append(i)
    pairs = []
    for i in train_idx:
        tags = [t for t in specific(rows[i][3]) if len(by_tag[t]) > 1]
        if not tags:
            continue
        t = rng.choice(tags)
        j = rng.choice([k for k in by_tag[t] if k != i and rows[k][1] != rows[i][1]] or [None])
        if j is not None:
            pairs.append((texts[i], texts[j]))
    return pairs


def precision_at_k(emb, rows, test_idx):
    """Share of each held-out item's top-K neighbours that share one of its specific tags."""
    tagsets = [specific(r[3]) for r in rows]
    scores = []
    for i in test_idx:
        if not tagsets[i]:
            continue
        sims = emb @ emb[i]
        sims[i] = -9
        top = np.argpartition(-sims, TOPK)[:TOPK]
        scores.append(np.mean([bool(tagsets[i] & tagsets[j]) for j in top]))
    return float(np.mean(scores)), len(scores)


if __name__ == "__main__":
    rows = load()
    texts = [item_text(*r[1:]) for r in rows]
    rng = random.Random(SEED)
    idx = list(range(len(rows)))
    rng.shuffle(idx)
    cut = int(len(idx) * (1 - HOLDOUT))
    train_idx, test_idx = idx[:cut], idx[cut:]
    pairs = make_pairs(rows, train_idx, rng)
    print(f"{len(rows)} items | train {len(train_idx)} | held-out {len(test_idx)} | {len(pairs)} training pairs")

    model = SentenceTransformer(BASE, device="mps" if torch.backends.mps.is_available() else "cpu")
    base_emb = model.encode(texts, normalize_embeddings=True, batch_size=128)
    base_p, n = precision_at_k(base_emb, rows, test_idx)
    print(f"pretrained  precision@{TOPK} on {n} held-out items: {base_p:.3f}")

    ds = Dataset.from_dict({"anchor": [a for a, _ in pairs], "positive": [b for _, b in pairs]})
    args = SentenceTransformerTrainingArguments(
        output_dir=f"{OUT}/checkpoints", num_train_epochs=1, per_device_train_batch_size=64,
        learning_rate=2e-5, warmup_ratio=0.1, seed=SEED, report_to="none",
        batch_sampler=BatchSamplers.NO_DUPLICATES, save_strategy="no")
    SentenceTransformerTrainer(model=model, args=args, train_dataset=ds,
                               loss=losses.MultipleNegativesRankingLoss(model)).train()

    ft_emb = model.encode(texts, normalize_embeddings=True, batch_size=128)
    ft_p, _ = precision_at_k(ft_emb, rows, test_idx)
    print(f"fine-tuned  precision@{TOPK} on {n} held-out items: {ft_p:.3f}  (pretrained {base_p:.3f})")

    os.makedirs(OUT, exist_ok=True)
    np.save(f"{OUT}/ids.npy", np.array([r[0] for r in rows]))
    np.save(f"{OUT}/emb_pretrained.npy", base_emb)
    np.save(f"{OUT}/emb_finetuned.npy", ft_emb)
    np.save(f"{OUT}/test_idx.npy", np.array(test_idx))
    model.save(f"{OUT}/minilm-finetuned")
    print(f"saved to {OUT}/ (not committed)")
