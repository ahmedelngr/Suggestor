# Open decisions (not yet decided; do not silently pick)

| Decision | Owner | Notes |
|---|---|---|
| Taste-vector update weighting | Modeling | Consider separate like/dislike weights or clipping dislikes to avoid drift. In use for now: like 1.0, pass 0.5 (`LIKE_WEIGHT`, `DISLIKE_WEIGHT`). |
| GPU for ML (Colab vs local) | Modeling | all-MiniLM fine-tuning is small; Colab is likely enough. |
| Eval data | Modeling | No real swipes yet. Plan: synthetic-user simulator as a clearly labeled proxy. |

## Decided rules

- Cooldown, not permanent exclusion. Swipes are never deleted; taste math uses full history.
- Re-swiping the same `item_id` replaces the previous nudge (latest signal wins), never stacks.
- "Dedup" has two meanings: swipe exclusion by exact `item_id`, and data-cleaning merge of the same real restaurant across sources.

## Decided (team, Oct 2026)

- Data source: Foursquare OS Places, an open dataset (Apache-2.0). Yelp and the Foursquare API were ruled out because their terms bar storing the data. See the decision log.
- Frontend: React Native (Expo).
- Accounts: first name, last name, phone, email + password. Phone is unverified in MVP1 and stays in `users` only.
- Onboarding: sign-up screening of a small seed set of restaurants (`items.is_onboarding_seed`) creates the starting taste vector; it refines with usage. Seed set should span cuisines and price tiers.
- Area: Pomona, as a radius (~15 miles around Cal Poly Pomona) for ingestion; user location is used for distance ranking.
- Budget: none. Free tiers only; run the API locally or on a free host (see `backend/README.md`).
- Cooldown: 14 days (`COOLDOWN_DAYS`).
- Onboarding: 5 swipes on the seed restaurants, then the taste vector is built.
