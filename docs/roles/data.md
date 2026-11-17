# Role: Data

## Mission
Get clean, legally usable restaurant data for the Pomona area into the database so everyone else can build on it.

## Owns
`data/`

## Deliverables (proposed)
1. **Week 1:** data source decision. Done: Foursquare OS Places (open dataset, Apache-2.0), loaded by `data/load_places.py`. Yelp and the Foursquare API were ruled out because their terms bar storing the data.
2. **Week 2:** ingestion script that pulls restaurants within about 15 miles of Cal Poly Pomona and writes them to `items` (`source`, `source_id`, title, tags, coordinates). Price tier and image URL are not in the open dataset.
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
- Follow the dataset's license. Do not bulk-store data from any API whose terms bar storing it.
- No scraping.
- If the license asks for attribution, tell Frontend.
- Keys and tokens (such as `HF_TOKEN`) live in `.env` (never in git).
- Do not change the schema. Request a migration from Backend.

## Learning resources
DuckDB; the Foursquare OS Places dataset card on Hugging Face; PostgreSQL `INSERT ... ON CONFLICT`.

## Who to ask
Lead for decisions on data source; Backend for schema.
