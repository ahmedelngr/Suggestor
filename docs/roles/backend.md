# Role: Backend

## Mission
Provide a reliable API and database that the app and ML code can depend on.

## Owns
`backend/` and the database migrations. Everyone else asks Backend for schema changes.

## Deliverables (proposed)
1. **Week 1:** local setup works for everyone (`docker compose up -d db`, migrations 001 and 002 apply cleanly).
2. **Week 2:** auth (sign-up, login, hashed passwords) and user profile.
3. **Week 3:** `POST /swipes` (append a row, update the taste vector with latest-swipe-wins) and onboarding endpoints (seed items in, starting vector out).
4. **Week 4:** `GET /feed` (cooldown exclusion, then pgvector cosine top-K) and search.
5. **Week 5-6:** distance from user location, cooldown as config (`COOLDOWN_DAYS`), error handling, API docs (FastAPI's `/docs`).

## Definition of done
- Endpoint has tests, including the edge cases (repeat swipe, empty profile, no items left).
- API shape is documented before Frontend builds against it.
- Migration is a new numbered file, applies on a fresh database.

## Inputs and outputs
- **Needs from Data:** items. **Needs from Modeling:** embeddings and the weighting recommendation.
- **Hands to Frontend:** a stable, documented API.

## Guardrails
- `swipes` is append-only. Never UPDATE or DELETE it (the database will refuse).
- Never edit a migration that others have applied; add a new one.
- Store only password hashes (bcrypt or argon2). Never log passwords or phone numbers.
- Phone and email stay in `users`; they must not appear in exports to `ml/` or `data/`.
- No model inference at request time.
- Secrets come from environment variables.

## Learning resources
FastAPI tutorial; psycopg or SQLAlchemy; pgvector README; OWASP password storage cheat sheet.

## Who to ask
Lead for product rules (cooldown, weighting); Modeling for vector questions.
