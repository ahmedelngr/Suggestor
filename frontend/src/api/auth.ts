import { FAKE_ACCOUNTS } from '../data/fakeAccounts';
import type { Session, SignInInput, SignUpInput } from '../types';

/** A problem the user can fix, like a wrong password. The message is shown in the form. */
export class AuthError extends Error {}

// STUB: accounts live in memory and reset when the app reloads. Never log
// passwords or phone numbers, here or anywhere else.
const accounts = new Map(
  FAKE_ACCOUNTS.map(({ email, ...account }) => [email, account]),
);

// Pretend network delay, so the loading state on the buttons is visible.
const FAKE_LATENCY_MS = 500;
const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const normalizeEmail = (email: string) => email.trim().toLowerCase();

const fakeSession = (email: string): Session => ({
  accessToken: `fake-token-${Date.now()}`,
  email,
});

/**
 * STUB. Real version: `supabase.auth.signInWithPassword({ email, password })`,
 * then build the Session from `data.session.access_token`.
 */
export async function signIn(input: SignInInput): Promise<Session> {
  await wait(FAKE_LATENCY_MS);
  const email = normalizeEmail(input.email);
  if (accounts.get(email)?.password !== input.password) {
    throw new AuthError('Incorrect email or password.');
  }
  return fakeSession(email);
}

/**
 * STUB. Real version (see backend/db/migrations/003):
 *   supabase.auth.signUp({ email, password,
 *     options: { data: { first_name, last_name, phone } } })
 * A database trigger then creates the user's row from that metadata.
 * If email confirmation is turned on in Supabase, sign-up returns no session
 * until the user confirms, so the app would need a "check your email" step.
 */
export async function signUp(input: SignUpInput): Promise<Session> {
  await wait(FAKE_LATENCY_MS);
  const email = normalizeEmail(input.email);
  if (accounts.has(email)) {
    throw new AuthError('An account with this email already exists.');
  }
  accounts.set(email, {
    password: input.password,
    firstName: input.firstName.trim(),
    lastName: input.lastName.trim(),
  });
  return fakeSession(email);
}

/** STUB helper for api/profile.ts: the name an account was created with. */
export function getFakeAccountName(email: string) {
  const account = accounts.get(email);
  return account && { firstName: account.firstName, lastName: account.lastName };
}

/** STUB. Real version: `supabase.auth.signOut()`. */
export async function signOut(): Promise<void> {}
