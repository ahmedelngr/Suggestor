import type { SuggestorItem } from '../types';

// Fictional restaurants around Cal Poly Pomona, for building the UI before the
// backend feed is wired up. Images are random placeholders, not the real food.
const image = (seed: string) => `https://picsum.photos/seed/${seed}/600/800`;

export const FAKE_ITEMS: SuggestorItem[] = [
  {
    id: 1,
    title: 'Garey Ave Taqueria',
    description:
      'Al pastor carved off the trompo, handmade tortillas and a salsa bar with six options. Open until 2am on weekends.',
    tags: ['Mexican', 'Tacos', 'Late night'],
    distance: 2.4,
    imageUrl: image('garey-taqueria'),
  },
  {
    id: 2,
    title: 'Bronco Boba Bar',
    description:
      'Brown sugar milk tea, fruit teas and mochi donuts. Long tables and outlets everywhere, so it fills up during finals.',
    tags: ['Boba', 'Desserts', 'Study spot'],
    distance: 0.8,
    imageUrl: image('bronco-boba'),
  },
  {
    id: 3,
    title: 'Seoul Fire K-BBQ',
    description:
      'All-you-can-eat Korean BBQ with brisket, pork belly and bulgogi grilled at your table. Best with a group of four or more.',
    tags: ['Korean', 'BBQ', 'Groups'],
    distance: 6.1,
    imageUrl: image('seoul-fire-kbbq'),
  },
  {
    id: 4,
    title: 'Foothill Ramen House',
    description:
      'Rich tonkotsu broth simmered for 18 hours, plus a spicy miso bowl and a vegan shoyu option. Expect a short line at dinner.',
    tags: ['Japanese', 'Ramen', 'Vegan options'],
    distance: 4.3,
    imageUrl: image('foothill-ramen'),
  },
  {
    id: 5,
    title: 'Pho Saigon Corner',
    description:
      'Big bowls of pho, crispy imperial rolls and Vietnamese iced coffee. Fast, cheap and quiet enough to talk.',
    tags: ['Vietnamese', 'Pho', 'Budget'],
    distance: 3.7,
    imageUrl: image('pho-saigon'),
  },
  {
    id: 6,
    title: 'Village Slice Co.',
    description:
      'New York style pizza by the slice in the Claremont Village. Grab a slice and walk around the shops.',
    tags: ['Pizza', 'Italian', 'Quick bite'],
    distance: 3.2,
    imageUrl: image('village-slice'),
  },
  {
    id: 7,
    title: 'Masala Junction',
    description:
      'North Indian curries, tandoori and fresh garlic naan. The weekday lunch buffet is the best deal in the area.',
    tags: ['Indian', 'Curry', 'Vegetarian options'],
    distance: 5.5,
    imageUrl: image('masala-junction'),
  },
  {
    id: 8,
    title: 'Diamond Bar Dim Sum',
    description:
      'Push-cart dim sum on weekends: har gow, siu mai, egg tarts and turnip cakes. Come before 11am to skip the wait.',
    tags: ['Chinese', 'Dim sum', 'Weekend brunch'],
    distance: 5.9,
    imageUrl: image('diamond-bar-dimsum'),
  },
  {
    id: 9,
    title: 'Route 66 Smashburgers',
    description:
      'Thin smashed patties with crispy edges, garlic fries and thick shakes. A classic diner on Foothill Blvd.',
    tags: ['American', 'Burgers', 'Late night'],
    distance: 7.8,
    imageUrl: image('route66-burgers'),
  },
  {
    id: 10,
    title: 'Green Spoon Kitchen',
    description:
      'Plant-based bowls, jackfruit tacos and cold-pressed juices. Everything on the menu is vegan.',
    tags: ['Vegan', 'Healthy', 'Bowls'],
    distance: 2.9,
    imageUrl: image('green-spoon'),
  },
  {
    id: 11,
    title: 'Thai Orchid Express',
    description:
      'Pad see ew, green curry and mango sticky rice. You choose the spice level from 1 to 5, and 5 is no joke.',
    tags: ['Thai', 'Noodles', 'Spicy'],
    distance: 1.6,
    imageUrl: image('thai-orchid'),
  },
  {
    id: 12,
    title: 'Lola’s Filipino Kitchen',
    description:
      'Chicken adobo, lumpia and garlic rice plates. Finish with halo-halo or an ube cheesecake.',
    tags: ['Filipino', 'Comfort food', 'Desserts'],
    distance: 8.2,
    imageUrl: image('lolas-filipino'),
  },
];
