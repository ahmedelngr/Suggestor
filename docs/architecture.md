# Architecture in one page

Each idea has an analogy first, then the technical version.

## Three tables (one PostgreSQL database with pgvector)
- `items`: every restaurant (generic, so events or hotels can be added later).
- `users`: each person, plus their `taste_vector`.
- `swipes`: every like or pass, ever.

**Analogy:** `items` is the menu, `users` is the customer list, `swipes` is the receipt book.
**Technical:** see `backend/db/migrations/`. `swipes` is append-only (a database trigger blocks UPDATE and DELETE). It is the source of truth for training and evaluation.

## Two kinds of vectors
A vector is a list of numbers that places something on a "map of meaning". Similar things sit close together.

1. **Item vectors** come from a fine-tuned sentence-transformer, computed offline in batches (when items are added or the model is retrained).
2. **User taste vectors** are NOT model output. They are a running weighted average of the vectors of items the user liked or disliked.

**Analogy:** each restaurant is a pin on a map. Your taste is a point on that map that drifts toward places you like and away from places you pass on.
**Technical:** on a like, move the taste vector toward the item vector; on a pass, move away. Plain arithmetic, no model call. Exact weighting is an open decision.

## The feed
1. Exclude items this user swiped within the cooldown window (by exact `item_id`).
2. Run a pgvector cosine-similarity query of the taste vector against the remaining item vectors.
3. Return the top K cards. No model runs at swipe or feed time.

**Analogy:** hide the dishes you recently turned down, then show the closest matches to your taste.

## Rules that are already decided
- **Cooldown controls eligibility; the taste vector controls ranking.** They are independent. Swipes are never deleted, and taste math uses full history.
- **Latest swipe wins.** If a user swipes the same `item_id` again, the new signal replaces the old nudge instead of stacking. Use the `latest_swipes` view.
- **Two meanings of "dedup":** (a) swipe exclusion by exact `item_id`; (b) data-cleaning that merges the same real restaurant appearing twice across sources. Do not confuse them.

## Where things live
| Folder | What |
|---|---|
| `data/` | ingestion and cleaning scripts |
| `ml/` | training and eval |
| `backend/` | FastAPI service and migrations |
| `frontend/` | React Native (Expo) app |
