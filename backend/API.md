# API contract

Base URL (local): `http://127.0.0.1:8000`. Interactive docs: `/docs`.

## Auth

Endpoints marked **auth** need the Supabase access token from login:

```
Authorization: Bearer <access_token>
```

Tokens last about an hour. A missing, invalid or expired token returns `401`. Get a new token from Supabase, not from this API.

## Typical flow

1. Sign up or log in through Supabase and keep the access token.
2. `GET /onboarding` returns the seed restaurants to swipe on.
3. `POST /swipes` for each swipe. On the 5th swipe the response says `"onboarded": true`.
4. `GET /feed` returns personalized restaurants. Until onboarding is done it returns `409`.
5. `POST /swipes` for every like or pass in the feed.
6. `GET /likes` for the profile screen.

## Endpoints

### `GET /health`
No auth. `200` `{"status": "ok"}`.

### `GET /health/db`
No auth. `200` `{"status": "ok"}` if the database answers, otherwise `500`.

### `GET /me` (auth)
The signed-in user's profile.

- `200` `{"id", "first_name", "last_name", "email", "onboarded_at", "onboarded"}`. `onboarded` is `true` once onboarding is done, and `onboarded_at` is `null` until then.
- `401` bad or expired token
- `404` no profile row for this user
- `502` the profile service failed

### `GET /onboarding` (auth)
The seed restaurants to swipe on during onboarding. Includes all of them, even ones already swiped.

- `200` a list of `{"id", "title", "description", "latitude", "longitude", "price_tier", "tags", "image_url"}`. `price_tier` and `image_url` can be `null`.
- `401` bad or expired token

### `GET /feed?limit=20` (auth)
Restaurants ranked by closeness to the user's taste, excluding ones they swiped on in the last `COOLDOWN_DAYS` (default 14). `limit` is 1 to 50.

- `200` a list, closest first. Each item: `{"id", "title", "description", "latitude", "longitude", "price_tier", "tags", "image_url", "distance"}`. `price_tier` and `image_url` can be `null`.
- `distance` is the taste distance (smaller means a better match). It is **not miles** and should not be shown to users. Miles are not provided yet.
- An empty list means no restaurant is eligible right now.
- `401` bad or expired token
- `404` no profile row
- `409` onboarding is not finished yet
- `422` invalid `limit`

### `POST /swipes` (auth)
Record a like or a pass. Swiping the same restaurant again replaces the earlier vote.

- Body: `{"item_id": 3, "liked": true}`
- `201` `{"id", "item_id", "liked", "onboarded"}`. `onboarded` becomes `true` on the 5th swipe on distinct restaurants.
- `401` bad or expired token
- `404` no profile row, or no such restaurant
- `422` invalid body

### `GET /likes?limit=100` (auth)
The restaurants the user currently likes, meaning their latest swipe on each one was a like. Newest first. `limit` is 1 to 200.

- `200` a list of `{"id", "title", "description", "latitude", "longitude", "price_tier", "tags", "image_url", "liked_at"}`. `liked_at` is an ISO 8601 timestamp of the latest like.
- `401` bad or expired token
- `404` no profile row
- `422` invalid `limit`

## Not available yet
- Distance in miles from the user's location.
- `price_tier` and `image_url` are empty in the data for now.
