import {
  ActivityIndicator,
  Pressable,
  StyleSheet,
  Text,
  type StyleProp,
  type ViewStyle,
} from 'react-native';

import { colors } from '../theme';

interface Props {
  label: string;
  onPress: () => void;
  /** Shows a spinner and ignores presses, e.g. while a request is running. */
  loading?: boolean;
  style?: StyleProp<ViewStyle>;
}

export function PrimaryButton({ label, onPress, loading = false, style }: Props) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={label}
      // aria-* rather than accessibilityState: react-native-web only reads these.
      aria-busy={loading}
      aria-disabled={loading}
      disabled={loading}
      onPress={onPress}
      style={({ pressed }) => [styles.button, style, (pressed || loading) && styles.dimmed]}
    >
      {loading ? <ActivityIndicator color="#FFFFFF" /> : <Text style={styles.label}>{label}</Text>}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  button: {
    minHeight: 50,
    paddingHorizontal: 28,
    borderRadius: 999,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.primary,
  },
  dimmed: {
    opacity: 0.6,
  },
  label: {
    fontSize: 16,
    fontWeight: '700',
    color: '#FFFFFF',
  },
});
