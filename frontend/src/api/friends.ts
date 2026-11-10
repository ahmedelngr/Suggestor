import { FAKE_FRIENDS } from '../data/fakeFriends';
import type { Friend, Session } from '../types';

/**
 * The user's friends.
 *
 * MOCKUP, outside MVP1 scope: docs/vision-and-scope.md lists social features
 * as out of scope, so there is no backend for this. Returns fake people for
 * the demo account and nobody for new accounts.
 */
export async function getFriends(session: Session): Promise<Friend[]> {
  return FAKE_FRIENDS[session.email] ?? [];
}
