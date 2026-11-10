/**
 * One swipeable card. Mirrors the backend's generic `items` table
 * (restaurants in MVP1, other item types later).
 */
export interface SuggestorItem {
  /** `items.id` (bigint) in the backend. */
  id: number;
  title: string;
  description: string;
  tags: string[];
  /** Miles from the user. */
  distance: number;
  imageUrl: string;
}

export type FeedbackAction = 'like' | 'dislike';

/** One swipe. Created on every like or dislike. */
export interface Feedback {
  itemId: number;
  action: FeedbackAction;
  /** ISO 8601, e.g. "2026-11-09T19:04:12.345Z". */
  timestamp: string;
}

/** A place the user liked. */
export interface LikedItem {
  item: SuggestorItem;
  /** ISO 8601. When they last swiped right on it. */
  likedAt: string;
}

/** The signed-in user. */
export interface Session {
  /** Sent to the backend as `Authorization: Bearer <accessToken>`. */
  accessToken: string;
  email: string;
}

/** The signed-in user's own profile. Subset of what `GET /me` returns. */
export interface UserProfile {
  firstName: string;
  lastName: string;
  email: string;
}

export interface SignInInput {
  email: string;
  password: string;
}

/** Same fields the Supabase sign-up trigger reads (backend migration 003). */
export interface SignUpInput extends SignInInput {
  firstName: string;
  lastName: string;
  phone: string;
}
