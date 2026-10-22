# Suggestor

A taste-aware AI recommender. Users swipe through cards; every swipe updates their taste profile, and recommendations are ranked by similarity to that profile.

**MVP1 (Fall 2026):** "Find me something good" for restaurants. Success = recommendations measurably beat a "most popular" baseline on Recall@K.

Suggestor is a standalone product. EventApp is a future integration client only.

## Repo layout

| Folder | Owner role | Purpose |
|---|---|---|
| `data/` | Data | Ingestion, cleaning, restaurant dedup |
| `ml/` | Modeling + Testing | Embedding fine-tuning, eval scoreboard |
| `backend/` | Backend | FastAPI service, Postgres + pgvector schema |
| `frontend/` | Frontend | Swipe UI |
| `docs/` | Everyone | Design notes, open decisions |

## Quick start (database)

```bash
docker compose up -d db
```

This starts Postgres with pgvector and applies `backend/db/migrations/*.sql` on first boot.

## Documentation

Start at [docs/README.md](docs/README.md) for the scope, your role, guardrails and workflow.

## Workflow

PRs only into protected `main`, 1 approval, squash merge. See `.github/CODEOWNERS`.

## Design in one paragraph

One generic `items` table (restaurants now, events/hotels later), a `users` table with a taste vector, and an append-only `swipes` log that is the source of truth. Item vectors come from a fine-tuned sentence-transformer, computed offline. User taste vectors are a running weighted average of liked/disliked item vectors, updated with plain arithmetic. The feed is a pgvector cosine query that excludes items swiped within the cooldown window. No model inference at swipe or feed time. See `docs/open-decisions.md`.
