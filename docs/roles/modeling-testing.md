# Role: Modeling + Testing

## Mission
Produce item embeddings that make recommendations better than "most popular", and build the scoreboard that proves it. This is the hardest role; two people share it, and the eval is as important as the model.

## Owns
`ml/`

## Deliverables (proposed)
1. **Week 1-2: eval harness first.** Recall@K metric, a "most popular" baseline, and a synthetic-user simulator (fake users with hidden tastes who swipe on real restaurants). Run it on an off-the-shelf all-MiniLM embedding. This is the number to beat.
2. **Week 3-4:** training pairs from metadata (same cuisine, price tier, nearby = positive; dissimilar = negative). Constructing good pairs is the core skill; document your rules.
3. **Week 4-5:** fine-tune the small sentence-transformer with contrastive learning. Write embeddings back to `items.embedding` (384 dims).
4. **Week 5-6:** compare against the pretrained baseline and the popularity baseline; recommend a taste-vector weighting scheme (open decision).
5. **Stretch only:** two-tower model on real swipe data.

## Definition of done
- Scoreboard prints Recall@K for popularity, pretrained MiniLM, and fine-tuned model on the same held-out split.
- Results are reproducible (fixed seeds, versions recorded).
- Synthetic-user results are labeled as a proxy everywhere they are shown.

## Inputs and outputs
- **Needs from Data:** populated `items`. **Needs from Backend:** swipe export and DB access.
- **Hands to Backend:** the model and a script that embeds new items in batch.

## Guardrails
- Never evaluate on data used for training pairs. Split by user and by item.
- Always report the pretrained (not fine-tuned) baseline. If fine-tuning does not help, say so; that is a valid result.
- No model inference on the swipe or feed path. Embeddings are batch only.
- Embedding dimension must match the schema (384). Changing it needs a migration.
- Do not claim the app "works" from synthetic data alone.
- GPU: Colab is acceptable; commit code and small configs, not model weights or large data.

## Learning resources
sentence-transformers docs (contrastive / MultipleNegativesRankingLoss); Recall@K explained; pgvector README.

## Who to ask
Each other first, then the lead. Backend for DB questions.
