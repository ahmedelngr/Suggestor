import type { Session, UserProfile } from '../types';
import { getFakeAccountName } from './auth';

// Pretend network delay, so the loading state on the profile is visible.
const FAKE_LATENCY_MS = 400;
const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Loads the signed-in user's profile.
 *
 * STUB: reads the name the fake account was created with. To wire it to the
 * backend, call `GET /me` with the user's bearer token and map the row:
 *   { first_name, last_name, email } -> UserProfile
 * `first_name` and `last_name` can be null for accounts made without them.
 * Never show the phone number, even though the user typed it at sign-up.
 */
export async function getProfile(session: Session): Promise<UserProfile> {
  await wait(FAKE_LATENCY_MS);
  const name = getFakeAccountName(session.email);
  if (!name) throw new Error('Profile not found');
  return { ...name, email: session.email };
}
