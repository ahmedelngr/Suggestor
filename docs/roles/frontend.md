# Role: Frontend

## Mission
Build the mobile app where people sign up, finish the screening, and swipe.

## Owns
`frontend/` (React Native with Expo)

## Deliverables (proposed)
1. **Week 1:** Expo app runs on a real phone via Expo Go; screen navigation skeleton.
2. **Week 2-3:** sign-up and login screens, built against the API contract (mock data until Backend is ready).
3. **Week 3-4:** onboarding screening (10-15 seed restaurants, swipe through them).
4. **Week 4-5:** swipe card stack (photo, name, cuisine, price tier, distance) with right = like, left = pass.
5. **Week 5-6:** search bar, empty and error states, location permission.

## Definition of done
- Works on iOS and Android through Expo Go.
- Loading, empty and error states exist for every screen.
- Required Yelp attribution is shown on cards if the terms require it.

## Inputs and outputs
- **Needs from Backend:** documented API. **Needs from Data:** image URLs, seed set.
- **Hands to everyone:** a demo-able app.

## Guardrails
- Talk only to the documented API. No recommendation logic in the app; ranking happens on the server.
- Never store passwords or tokens in plain storage; use the platform secure store.
- Ask for location permission only when needed and explain why.
- Do not display phone numbers or other users' data.
- Keep screens simple; polish comes after the loop works end to end.

## Learning resources
Expo docs; React Navigation; a swipe-card library such as react-native-deck-swiper.

## Who to ask
Backend for API questions; lead for UX decisions.
