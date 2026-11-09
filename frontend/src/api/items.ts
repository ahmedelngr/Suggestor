import { FAKE_ITEMS } from '../data/fakeItems';
import type { SuggestorItem } from '../types';

/**
 * Loads the cards to swipe on.
 *
 * STUB: returns local fake data. To wire it to the backend, call
 * `GET /feed?limit=20` with the user's bearer token and map each row:
 *   { id, title, description, tags, image_url } -> SuggestorItem
 * Note: the backend's `distance` field is the cosine distance to the user's
 * taste vector, not miles. Miles need to be computed from latitude/longitude
 * and the user's location, or added to the API by Backend.
 */
export async function getItems(): Promise<SuggestorItem[]> {
  return FAKE_ITEMS;
}
