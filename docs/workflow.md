# Workflow

## Rules
- `main` is protected. All changes arrive by pull request, with 1 approval, and are squash-merged.
- Never push directly to `main`.
- CODEOWNERS routes reviews by folder.

## Day to day
1. Pull the latest `main`.
2. Create a branch: `role/short-description`, e.g. `data/yelp-ingest`, `backend/swipe-endpoint`.
3. Make small commits. A PR should be reviewable in about 15 minutes.
4. Open a PR using the template. Say what changed, why, and how to test it. For non-trivial code, include a short explanation of the concept.
5. Request review from the folder owner. Reviewers aim to respond within 48 hours.
6. Address feedback, get 1 approval, squash and merge, delete the branch.

## Commit messages
Short, present tense, say what: `Add swipe endpoint with latest-wins update`.

## Run the database locally
```bash
docker compose up -d db
```
Migrations in `backend/db/migrations/` apply on the first start. To reset: `docker compose down -v` and start again (this deletes local data).

## Definition of done (every PR)
- It does what the PR says, and you ran it.
- Tests or eval output included where relevant.
- No secrets, no unrelated changes.
- Docs updated if behavior or a decision changed.
- Guardrails checklist in the PR template is ticked.

## Cross-role handoffs
Post in the team chat when you hand something off, and link the PR. The receiving role confirms it works for them.
