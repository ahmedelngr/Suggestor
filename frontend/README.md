# Frontend

Suggestor's swipe app: React Native with Expo (SDK 58), TypeScript. It runs on iOS and Android through Expo Go, and in a web browser.

The app currently uses fake data. Nothing calls the backend yet (see [Wiring to the backend](#wiring-to-the-backend)).

## Setup

1. Install Node.js 22 LTS (22.13+) or 24 LTS (24.3+). Expo SDK 58 won't run on older versions.
2. On your phone, install **Expo Go** from the App Store or Google Play.
3. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

## Run

```bash
cd frontend
npx expo start
```

- **Phone:** scan the QR code (iOS: Camera app; Android: Expo Go). Your phone and computer must be on the same Wi-Fi. If that doesn't work (e.g. campus Wi-Fi), try `npx expo start --tunnel`.
- **Web:** press `w` in the terminal.
- `console.log` output from the app shows in this terminal (and in the browser console on web).

Before opening a PR:

```bash
npx tsc --noEmit   # typecheck
```

Add packages with `npx expo install <package>`, not `npm install`, so versions match the Expo SDK. Expo Go only includes certain native modules, so check that a library supports Expo Go before adding it.

## Layout

```
App.tsx                    root: safe-area provider + feed screen
src/
  types.ts                 SuggestorItem, Feedback
  theme.ts                 colors
  api/items.ts             getItems()        (stub: returns fake data)
  api/feedback.ts          submitFeedback()  (stub: console.log)
  data/fakeItems.ts        12 fictional Pomona-area restaurants
  components/SwipeCard.tsx one draggable card (Animated + PanResponder)
  screens/FeedScreen.tsx   the deck, Like/Dislike buttons, loading/error/empty states
```

## How swiping works

Each card is a view that moves with your finger. React Native's `PanResponder` reports how far you have dragged, and `Animated` moves and tilts the card to match. When you let go:

- dragged more than 120px right: the card flies off and counts as **like**
- dragged more than 120px left: **dislike**
- otherwise it springs back

The LIKE / NOPE stamp fades in as you drag and is fully visible at exactly the point where letting go counts. The buttons under the card call the same swipe animation.

Every swipe creates a `Feedback` record `{ itemId, action, timestamp }`, adds it to state in `FeedScreen` and passes it to `submitFeedback()`.

## Wiring to the backend

Only `src/api/` should talk to the server. Both files have comments describing the mapping:

| App function | Backend endpoint | Notes |
|---|---|---|
| `getItems()` | `GET /feed?limit=20` | Rows have `image_url`, so map it to `imageUrl`. The backend's `distance` field is the taste-vector distance, **not miles**. Miles will need to be computed from `latitude`/`longitude`, or added by Backend. |
| `submitFeedback()` | `POST /swipes` | Send `{ item_id: itemId, liked: action === 'like' }`. The server sets the timestamp itself. |

Both endpoints need a Supabase bearer token, so they depend on the login screen. When the app needs config (e.g. the API URL), put it in `frontend/.env` as `EXPO_PUBLIC_API_URL=...`, add the same key with a placeholder to `frontend/.env.example`, and never commit `.env`. Anything prefixed `EXPO_PUBLIC_` ends up in the app bundle, so it must not be a secret.
