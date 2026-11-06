# data/

## Foursquare OS Places loader

`load_places.py` loads restaurants within 15 miles of Cal Poly Pomona into `items`
(`source='fsq_os'`). Source: Foursquare OS Places on Hugging Face (Apache-2.0).
We use this instead of the Yelp or Foursquare APIs because their terms bar storing the data.

### Setup
1. Request access to `foursquare/fsq-os-places` on Hugging Face (one-time form).
2. Create a read-only token at huggingface.co/settings/tokens.
3. In the repo-root `.env` (never committed) add `HF_TOKEN=...` and `DATABASE_URL=...`.
4. `pip install -r data/requirements.txt`

### Run (from the repo root)
```bash
set -a; source .env; set +a
python data/load_places.py --describe   # check columns exist
python data/load_places.py --dry-run    # count and sample, no writes
python data/load_places.py              # upsert into items
```
Re-running is safe: rows are upserted on `(source, source_id)` and `embedding` is never overwritten.

### Not stored
Photos, price and ratings are not in the open dataset. They are fetched live (later) or use placeholders.
