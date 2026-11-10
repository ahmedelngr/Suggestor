import type { Friend } from '../types';

// Made-up friends for the demo account, most in common first. Not real people.
// MOCKUP: friends are outside MVP1 scope (see src/api/friends.ts).
export const FAKE_FRIENDS: Record<string, Friend[]> = {
  'demo@suggestor.test': [
    { id: 101, displayName: 'Maya R.', placesInCommon: 4 },
    { id: 102, displayName: 'Priya S.', placesInCommon: 3 },
    { id: 103, displayName: 'Chris T.', placesInCommon: 2 },
    { id: 104, displayName: 'Diego M.', placesInCommon: 1 },
    { id: 105, displayName: 'Sam K.', placesInCommon: 0 },
  ],
};
