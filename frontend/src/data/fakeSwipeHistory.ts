import type { Feedback } from '../types';

// Made-up past swipes for the demo account, oldest first, so the profile has
// liked places to show before any real swiping. Item ids are from fakeItems.ts.
export const FAKE_SWIPE_HISTORY: Record<string, Feedback[]> = {
  'demo@suggestor.test': [
    { itemId: 4, action: 'like', timestamp: '2026-10-18T19:42:00.000Z' },
    { itemId: 9, action: 'dislike', timestamp: '2026-10-18T19:42:30.000Z' },
    { itemId: 2, action: 'like', timestamp: '2026-10-22T01:15:00.000Z' },
    { itemId: 10, action: 'dislike', timestamp: '2026-10-22T01:15:20.000Z' },
    { itemId: 12, action: 'like', timestamp: '2026-10-25T23:40:00.000Z' },
    { itemId: 11, action: 'like', timestamp: '2026-10-29T20:05:00.000Z' },
    { itemId: 7, action: 'like', timestamp: '2026-11-03T18:30:00.000Z' },
    { itemId: 3, action: 'dislike', timestamp: '2026-11-03T18:31:00.000Z' },
    { itemId: 6, action: 'like', timestamp: '2026-11-07T02:10:00.000Z' },
  ],
};
