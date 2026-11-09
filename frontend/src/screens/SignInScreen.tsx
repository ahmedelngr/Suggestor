import { Link } from 'expo-router';
import { useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { AuthError } from '../api/auth';
import { useSession } from '../auth/SessionProvider';
import { hasErrors, validateSignIn, type FieldErrors } from '../auth/validation';
import { AuthLayout } from '../components/AuthLayout';
import { PrimaryButton } from '../components/PrimaryButton';
import { TextField } from '../components/TextField';
import { colors } from '../theme';
import type { SignInInput } from '../types';

export function SignInScreen() {
  const { signIn } = useSession();
  const [form, setForm] = useState<SignInInput>({ email: '', password: '' });
  const [errors, setErrors] = useState<FieldErrors<SignInInput>>({});
  const [formError, setFormError] = useState<string>();
  const [submitting, setSubmitting] = useState(false);

  const update = (field: keyof SignInInput) => (text: string) => {
    setForm((prev) => ({ ...prev, [field]: text }));
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  const submit = async () => {
    if (submitting) return;
    const found = validateSignIn(form);
    setErrors(found);
    setFormError(undefined);
    if (hasErrors(found)) return;

    setSubmitting(true);
    try {
      // On success the guard in src/app/_layout.tsx switches to the feed.
      await signIn(form);
    } catch (err) {
      if (!(err instanceof AuthError)) console.warn('[signIn] failed', err);
      setFormError(err instanceof AuthError ? err.message : 'Something went wrong. Try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthLayout title="Log in" error={formError}>
      <TextField
        label="Email"
        value={form.email}
        onChangeText={update('email')}
        error={errors.email}
        inputMode="email"
        autoComplete="email"
        autoCapitalize="none"
        autoCorrect={false}
        returnKeyType="next"
      />
      <TextField
        label="Password"
        value={form.password}
        onChangeText={update('password')}
        error={errors.password}
        secureTextEntry
        autoComplete="current-password"
        returnKeyType="go"
        onSubmitEditing={submit}
      />
      <PrimaryButton label="Log in" onPress={submit} loading={submitting} />
      <View style={styles.switchRow}>
        <Text style={styles.switchText}>New to Suggestor?</Text>
        <Link href="/sign-up" style={styles.link}>
          Create an account
        </Link>
      </View>
    </AuthLayout>
  );
}

const styles = StyleSheet.create({
  switchRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    flexWrap: 'wrap',
    gap: 6,
  },
  switchText: {
    fontSize: 15,
    color: colors.textMuted,
  },
  link: {
    fontSize: 15,
    fontWeight: '700',
    color: colors.primary,
  },
});
