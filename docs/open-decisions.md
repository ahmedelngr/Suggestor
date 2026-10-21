# Open decisions (not yet decided; do not silently pick)

| Decision | Owner | Notes |
|---|---|---|
| Yelp API viability | Data + lead | Team chose Yelp, but third-party sources say the free tier ended (30-day / 5,000-call trial, then paid) and caching may be limited to ~24h. Read docs.developer.yelp.com plans + storage clause before building. Fallbacks: Foursquare, OpenStreetMap. |
| Cooldown length (24h / 2 weeks / 2 months) | Team (product call) | Controls eligibility only; taste vector controls ranking. Configured via `COOLDOWN_DAYS`. |
| Taste-vector update weighting | Modeling | Consider separate like/dislike weights or clipping dislikes to avoid drift. |
| GPU for ML (Colab vs local) | Modeling | all-MiniLM fine-tuning is small; Colab is likely enough. |
| Eval data | Modeling | No real swipes yet. Plan: synthetic-user simulator as a clearly labeled proxy. |

## Decided rules

- Cooldown, not permanent exclusion. Swipes are never deleted; taste math uses full history.
- Re-swiping the same `item_id` replaces the previous nudge (latest signal wins), never stacks.
- "Dedup" has two meanings: swipe exclusion by exact `item_id`, and data-cleaning merge of the same real restaurant across sources.

## Decided (team, Oct 2026)

- Data source: Yelp (pending the viability check above).
- Frontend: React Native (Expo).
- Accounts: first name, last name, phone, email + password. Phone is unverified in MVP1 and stays in `users` only.
- Onboarding: sign-up screening of a small seed set of restaurants (`items.is_onboarding_seed`) creates the starting taste vector; it refines with usage. Seed set should span cuisines and price tiers.
- Area: Pomona, as a radius (~15 miles around Cal Poly Pomona) for ingestion; user location is used for distance ranking.
- Budget: none. Free tiers only; run locally, deploy later.
