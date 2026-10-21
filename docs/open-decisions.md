# Open decisions (not yet decided; do not silently pick)

| Decision | Owner | Notes |
|---|---|---|
| Yelp Fusion vs Google Places | Data + lead | Check terms on caching/storage, rate limits, cost, photo attribution. Fallbacks: Foursquare, OpenStreetMap. |
| Cooldown length (24h / 2 weeks / 2 months) | Team (product call) | Controls eligibility only; taste vector controls ranking. Configured via `COOLDOWN_DAYS`. |
| Taste-vector update weighting | Modeling | Consider separate like/dislike weights or clipping dislikes to avoid drift. |
| GPU for ML (Colab vs local) | Modeling | all-MiniLM fine-tuning is small; Colab is likely enough. |
| React web vs React Native | Frontend + lead | One frontend dev, 8 weeks: web (mobile-responsive) is the lower-risk choice. |
| Eval data | Modeling | No real swipes yet. Plan: synthetic-user simulator as a clearly labeled proxy. |

## Decided rules

- Cooldown, not permanent exclusion. Swipes are never deleted; taste math uses full history.
- Re-swiping the same `item_id` replaces the previous nudge (latest signal wins), never stacks.
- "Dedup" has two meanings: swipe exclusion by exact `item_id`, and data-cleaning merge of the same real restaurant across sources.
