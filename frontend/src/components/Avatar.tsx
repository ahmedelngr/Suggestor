import { StyleSheet, Text, View } from 'react-native';

import { avatarColors } from '../theme';

interface Props {
  /** e.g. "Jordan Lee" or "Maya R.". The first letters of the first two words are shown. */
  name: string;
  size: number;
}

/** A colored circle with someone's initials. The same name always gets the same color. */
export function Avatar({ name, size }: Props) {
  const initials = name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0].toUpperCase())
    .join('');

  let hash = 0;
  for (const char of name) hash = (hash * 31 + char.charCodeAt(0)) >>> 0;
  const backgroundColor = avatarColors[hash % avatarColors.length];

  return (
    <View
      // Decorative: the name is always shown next to it.
      aria-hidden
      style={[styles.circle, { width: size, height: size, borderRadius: size / 2, backgroundColor }]}
    >
      <Text style={[styles.initials, { fontSize: size * 0.4 }]}>{initials}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  circle: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  initials: {
    fontWeight: '700',
    color: '#FFFFFF',
  },
});
