import type { ReactNode } from 'react';
import { KeyboardAvoidingView, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { colors } from '../theme';

interface Props {
  title: string;
  /** Problem with the whole form, e.g. a wrong password. Shown above the fields. */
  error?: string;
  children: ReactNode;
}

/** Shared frame for the log in and sign up screens. */
export function AuthLayout({ title, error, children }: Props) {
  return (
    <SafeAreaView style={styles.screen}>
      {/* Expo apps draw edge to edge, so Android needs a behavior too, not just iOS. */}
      <KeyboardAvoidingView style={styles.screen} behavior="padding">
        <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
          <Text style={styles.brand}>Suggestor</Text>
          <Text style={styles.title}>{title}</Text>
          {error ? (
            <View style={styles.errorBox} accessibilityRole="alert">
              <Text style={styles.errorText}>{error}</Text>
            </View>
          ) : null}
          {children}
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    flexGrow: 1,
    justifyContent: 'center',
    width: '100%',
    maxWidth: 440,
    alignSelf: 'center',
    padding: 24,
    gap: 16,
  },
  brand: {
    fontSize: 32,
    fontWeight: '800',
    textAlign: 'center',
    color: colors.primary,
  },
  title: {
    marginBottom: 8,
    fontSize: 20,
    fontWeight: '700',
    textAlign: 'center',
    color: colors.text,
  },
  errorBox: {
    padding: 12,
    borderRadius: 10,
    backgroundColor: colors.errorBackground,
  },
  errorText: {
    fontSize: 14,
    color: colors.dislike,
  },
});
