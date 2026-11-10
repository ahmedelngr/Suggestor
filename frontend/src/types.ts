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
