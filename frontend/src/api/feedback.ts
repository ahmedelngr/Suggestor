import { FAKE_ITEMS } from '../data/fakeItems';
import { FAKE_SWIPE_HISTORY } from '../data/fakeSwipeHistory';
import type { Feedback, LikedItem, Session } from '../types';

// STUB: swipes are kept in memory per account, oldest first, starting from the
// fake history. They reset when the app reloads.
const swipesByEmail = new Map(
  Object.entries(FAKE_SWIPE_HISTORY).map(([email, swipes]) => [email, [...swipes]]),
);

/**
 * Sends one swipe to the server.
 *
 * STUB: logs it and keeps it in memory, so it shows up on the profile. To wire
 * it to the backend, call `POST /swipes` with the user's bearer token and this body:
 *   { item_id: feedback.itemId, liked: feedback.action === 'like' }
 * The server records its own timestamp, so `feedback.timestamp` is not sent.
 */
export async function submitFeedback(session: Session, feedback: Feedback): Promise<void> {
  console.log('[submitFeedback stub]', feedback);
  const swipes = swipesByEmail.get(session.email) ?? [];
  swipes.push(feedback);
  swipesByEmail.set(session.email, swipes);
}

/**
 * Places the user has liked, newest first. If they swiped the same place more
 * than once, only the latest swipe counts (same rule as the backend's
 * `latest_swipes` view).
 *
 * STUB: built from the in-memory swipes. There is no endpoint for this yet;
 * Backend would need to add one, e.g. `GET /likes` returning `latest_swipes`
 * rows where `liked` is true, joined with `items`.
 */
export async function getLikes(session: Session): Promise<LikedItem[]> {
  const latest = new Map<number, Feedback>();
  for (const swipe of swipesByEmail.get(session.email) ?? []) latest.set(swipe.itemId, swipe);

  return [...latest.values()]
    .filter((swipe) => swipe.action === 'like')
    .sort((a, b) => b.timestamp.localeCompare(a.timestamp))
    .flatMap((swipe) => {
      const item = FAKE_ITEMS.find((i) => i.id === swipe.itemId);
      return item ? [{ item, likedAt: swipe.timestamp }] : [];
    });
}
