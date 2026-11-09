# Frontend

Suggestor's swipe app: React Native with Expo (SDK 58), TypeScript. It runs on iOS and Android through Expo Go, and in a web browser.

The app currently uses fake data and a fake login. Nothing calls the backend yet (see [Wiring to the backend](#wiring-to-the-backend)).

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
- **Log in** with the fake account `demo@suggestor.test` / `password123`, or create a new one on the sign-up screen. Accounts and the login only live in memory, so reloading the app signs you out and forgets new accounts.
- `console.log` output from the app shows in this terminal (and in the browser console on web).
- After switching branches or changing `package.json` or `app.json`, restart with `npx expo start --clear`.

Before opening a PR:

```bash
npx tsc --noEmit   # typecheck
```

Add packages with `npx expo install <package>`, not `npm install`, so versions match the Expo SDK. Expo Go only includes certain native modules, so check that a library supports Expo Go before adding it.

## Layout

Navigation uses [Expo Router](https://docs.expo.dev/router/introduction/): every file in `src/app/` is a screen, and its path is the URL (`sign-in.tsx` is `/sign-in`). Route files stay one line long; the screens themselves live in `src/screens/`.

```
src/
  app/_layout.tsx                 root stack + route guards (signed in vs signed out)
  app/index.tsx                   /         -> FeedScreen
  app/sign-in.tsx                 /sign-in  -> SignInScreen
  app/sign-up.tsx                 /sign-up  -> SignUpScreen
  screens/                        FeedScreen, SignInScreen, SignUpScreen
  components/                     SwipeCard, PrimaryButton, TextField, AuthLayout
  auth/SessionProvider.tsx        who is signed in (useSession())
  auth/validation.ts              sign-in / sign-up form checks
  api/auth.ts                     signIn(), signUp(), signOut()  (stub: in-memory accounts)
  api/items.ts                    getItems()                     (stub: returns fake data)
  api/feedback.ts                 submitFeedback()               (stub: console.log)
  data/fakeItems.ts               12 fictional Pomona-area restaurants
  data/fakeAccounts.ts            the demo login
  types.ts                        SuggestorItem, Feedback, Session, SignInInput, SignUpInput
  theme.ts                        colors
```

## How the login works

`SessionProvider` holds the current session (or `null`). `src/app/_layout.tsx` wraps the screens in two `Stack.Protected` groups:

- **Signed in:** the feed (`/`). Signed-out users who open it are sent to `/sign-in`.
- **Signed out:** `/sign-in` and `/sign-up`. Signed-in users who open them are sent to `/`.

Signing in or out flips those guards, and the router moves to the right screen on its own. That's why the screens never navigate after a successful login.

## How swiping works

Each card is a view that moves with your finger. React Native's `PanResponder` reports how far you have dragged, and `Animated` moves and tilts the card to match. When you let go:

- dragged more than 120px right: the card flies off and counts as **like**
- dragged more than 120px left: **dislike**
- otherwise it springs back

The LIKE / NOPE stamp fades in as you drag and is fully visible at exactly the point where letting go counts. The buttons under the card call the same swipe animation.

Every swipe creates a `Feedback` record `{ itemId, action, timestamp }`, adds it to state in `FeedScreen` and passes it to `submitFeedback()`.

## Wiring to the backend

Only `src/api/` should talk to the server. Each file has comments describing the mapping:

| App function | Real call | Notes |
|---|---|---|
| `signIn()` | `supabase.auth.signInWithPassword` | Build the `Session` from `data.session.access_token`. |
| `signUp()` | `supabase.auth.signUp` | Pass `first_name`, `last_name`, `phone` in `options.data`; a database trigger creates the user row (backend migration 003). If email confirmation is on in Supabase, no session comes back until the user confirms. |
| `signOut()` | `supabase.auth.signOut` | |
| `getItems()` | `GET /feed?limit=20` | Rows have `image_url`, so map it to `imageUrl`. The backend's `distance` field is the taste-vector distance, **not miles**. Miles will need to be computed from `latitude`/`longitude`, or added by Backend. |
| `submitFeedback()` | `POST /swipes` | Send `{ item_id: itemId, liked: action === 'like' }`. The server sets the timestamp itself. |

The backend endpoints need the session's access token as `Authorization: Bearer <token>`. Once auth is real, the session must be stored with `expo-secure-store` (team guardrail: never plain storage), and the app needs a short loading state on launch while it reads the saved session.

When the app needs config (e.g. the API URL or Supabase project URL), put it in `frontend/.env` as `EXPO_PUBLIC_...=...`, add the same key with a placeholder to `frontend/.env.example`, and never commit `.env`. Anything prefixed `EXPO_PUBLIC_` ends up in the app bundle, so it must not be a secret (the Supabase anon key is fine; the service role key never is).

Never log passwords or phone numbers.
