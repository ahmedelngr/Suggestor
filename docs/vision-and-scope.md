# Vision and scope

## What Suggestor is
A standalone AI product that learns your taste from swipes and recommends things you will like. It is **not** part of EventApp. EventApp may become a client of Suggestor much later.

Long-term vision: a personal taste-aware agent that recommends restaurants, events, hotels and activities, and eventually plans full itineraries.

## MVP1 (Fall 2026): "Find me something good" for restaurants
**Goal:** a working mobile app where a user swipes restaurant cards, and our recommendations measurably beat a "most popular" baseline.

**Success metric:** Recall@K on held-out swipes, compared with the most-popular baseline. If we cannot show this, we have not finished.

### In scope
- Yelp as the data source (pending the viability check in [open-decisions.md](open-decisions.md)).
- Pomona area only (about a 15-mile radius around Cal Poly Pomona).
- Accounts: first name, last name, phone, email, password.
- Sign-up screening: swipe a small seed set of restaurants to create a starting taste vector.
- Swipe card stack (right = like, left = pass) and a search bar.
- Taste vector updates on every swipe.
- Feed ranked by similarity to the taste vector, with a cooldown on swiped items.
- Fine-tuned small sentence-transformer for item embeddings.
- Eval scoreboard (Recall@K vs popularity baseline).

### Out of scope (do not build, even if easy)
- Itinerary or day planning, chat agent, SDK, EventApp adapter (MVP2 to MVP4).
- Events, hotels, or any item type other than restaurants.
- Two-tower model trained on swipe data (stretch only, after everything above works).
- SMS verification of phone numbers.
- Areas outside Pomona; "wherever the user is" is a later problem.
- Payments, social features, reviews written by users.
- Anything that needs a paid service (budget is zero).

If you think something out-of-scope is needed, raise it with the lead before writing code.

## Future MVPs (context only)
| MVP | When | What |
|---|---|---|
| MVP2 | Spring 2027 | Ranker plus day planner. Planning is a constraint-solving problem (time windows, travel time, budget), not just more item types. |
| MVP3 | Fall 2027 | Fine-tuned conversational agent. |
| MVP4 | Spring 2028 | Packaged API/SDK plus EventApp adapter. |

**Rule:** MVP1 must make these additive. That is why `items` is generic, the swipe log is kept forever, and the API is a clean boundary.
