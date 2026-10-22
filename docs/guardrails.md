# Guardrails (everyone, always)

## Privacy and secrets
- Never commit API keys, passwords, tokens or `.env` files. Use `.env` locally and keep a `.env.example` with fake values in git.
- If you commit a secret by accident, tell the lead immediately; the key must be rotated (deleting the commit is not enough).
- Phone numbers and emails live only in the `users` table. They must not go into datasets, notebooks, logs, screenshots or chat.
- Passwords are stored only as hashes.

## Data and legal
- Follow the data provider's terms. Until the Yelp viability memo is approved, do not bulk-store Yelp data.
- No scraping. Respect rate limits.
- Show required attribution wherever provider data is displayed.

## Database
- `swipes` is append-only. Never update or delete rows.
- Migrations are numbered, additive, and never edited after merge. Schema changes go through Backend.
- Embedding dimension is 384; changing it needs a migration and a re-embed.

## ML and product rules
- No model inference on the swipe or feed path.
- Cooldown decides what may appear; the taste vector decides ranking. Keep them separate.
- Latest swipe on an item replaces the earlier nudge; never stack.
- Synthetic-user results are a proxy and are always labeled so.
- Never evaluate on training data.

## Scope
- Do not build out-of-scope items (see [vision-and-scope.md](vision-and-scope.md)). Ask the lead first.
- Nothing that costs money without approval (budget is zero).

## Code and AI tools
- Small PRs. No giant dumps.
- Using an AI assistant is fine, but you must understand and be able to explain every line you submit. Explain the concept in the PR description.
- Do not paste private data (phone numbers, keys) into AI tools.

## Conduct
- Ask for help early. Blocked for more than a day means say so.
- Review feedback is about the code, not the person.
