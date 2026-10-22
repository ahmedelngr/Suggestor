# Role: Data

## Mission
Get clean, legally usable restaurant data for the Pomona area into the database so everyone else can build on it.

## Owns
`data/`

## Deliverables (proposed)
1. **Week 1:** Yelp viability memo. Read the current plans, free-trial limits and the data-storage clause at docs.developer.yelp.com. Answer: can we get a key for free, and may we store data for a semester? If not, recommend Foursquare or OpenStreetMap.
2. **Week 2:** ingestion script that pulls restaurants within about 15 miles of Cal Poly Pomona and writes them to `items` (`source`, `source_id`, title, tags, price tier, coordinates, image URL).
3. **Week 3:** cleaning (missing fields, closed businesses) and cross-source dedup if more than one source is used.
4. **Week 3-4:** pick the onboarding seed set and mark `is_onboarding_seed`. It must span cuisines and price tiers, not just whatever is popular.
5. Ongoing: a short data card in `data/README.md` (what is in the dataset, counts, known gaps).

## Definition of done
- Script is re-runnable without creating duplicates (`UNIQUE (source, source_id)`).
- Row counts and field coverage are reported in the PR.
- No API key is committed.

## Inputs and outputs
- **Needs from Backend:** applied migrations and a way to connect to the database.
- **Hands to Modeling:** a populated `items` table. Hands to Frontend: image URLs and the seed set.

## Guardrails
- Do not store or cache Yelp data beyond what the terms allow. Until the memo is done, do not build a large pipeline.
- No scraping. Use the API only.
- Keep Yelp attribution requirements in mind and tell Frontend about them.
- Keys live in `.env` (never in git).
- Do not change the schema. Request a migration from Backend.

## Learning resources
Yelp Fusion docs; the `requests` library; PostgreSQL `INSERT ... ON CONFLICT`.

## Who to ask
Lead for decisions on data source; Backend for schema.
