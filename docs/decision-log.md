# Decision log

Format: date, decision, who decided, why. Add new entries at the bottom. Undecided items live in [open-decisions.md](open-decisions.md).

| Date | Decision | Decided by | Why |
|---|---|---|---|
| 2026 (fall) | MVP1 pivots from events to restaurants | Lead | Standardized data, items do not expire, no event dedup |
| 2026-10 | One PostgreSQL DB with pgvector; generic `items` table | Lead | One place for data, additive future MVPs |
| 2026-10 | Cooldown, not permanent exclusion | Lead | Mood changes; swipes never deleted |
| 2026-10 | Latest swipe on an item wins | Lead | Prevents stacked nudges from flip-flopping |
| 2026-10 | Yelp as data source (pending viability check) | Team | Team choice; terms and cost unverified |
| 2026-10 | React Native (Expo) | Team | Mobile target |
| 2026-10 | Accounts with name and phone; unverified phone | Team | Simple MVP1 |
| 2026-10 | Onboarding by swiping a seed set | Team | Seeds the taste vector |
| 2026-10 | Area: Pomona radius | Team | Bounded data pull |
| 2026-10 | Zero budget, free tiers only | Team | Club project |
| 2026-10-25 | Database and login move to Supabase (Postgres, pgvector, Auth); docker-compose removed | Lead | Supabase Auth owns passwords; one hosted database for everyone |
| 2026-11-05 | Data source is Foursquare OS Places (open dataset), not Yelp | Lead | Yelp and the Foursquare API terms bar storing the data (see `data/README.md`) |
| 2026-11-09 | Onboarding is 5 swipes on seed restaurants; the taste vector is built when it finishes | Lead | Nothing to rank before that, so `/feed` returns 409 until then |
| 2026-11-16 | Cooldown stays at 14 days | Lead | Product call |
