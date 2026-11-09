import type { Feedback } from '../types';

/**
 * Sends one swipe to the server.
 *
 * STUB: only logs. To wire it to the backend, call `POST /swipes` with the
 * user's bearer token and this body:
 *   { item_id: feedback.itemId, liked: feedback.action === 'like' }
 * The server records its own timestamp, so `feedback.timestamp` is not sent.
 */
export async function submitFeedback(feedback: Feedback): Promise<void> {
  console.log('[submitFeedback stub]', feedback);
}
