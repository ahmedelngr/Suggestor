import { Link } from 'expo-router';
import { useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { AuthError } from '../api/auth';
import { useSession } from '../auth/SessionProvider';
import {
  MIN_PASSWORD_LENGTH,
  hasErrors,
  validateSignUp,
  type FieldErrors,
} from '../auth/validation';
import { AuthLayout } from '../components/AuthLayout';
import { PrimaryButton } from '../components/PrimaryButton';
import { TextField } from '../components/TextField';
import { colors } from '../theme';
import type { SignUpInput } from '../types';

const EMPTY_FORM: SignUpInput = { firstName: '', lastName: '', phone: '', email: '', password: '' };

export function SignUpScreen() {
  const { signUp } = useSession();
  const [form, setForm] = useState<SignUpInput>(EMPTY_FORM);
  const [errors, setErrors] = useState<FieldErrors<SignUpInput>>({});
  const [formError, setFormError] = useState<string>();
  const [submitting, setSubmitting] = useState(false);

  const update = (field: keyof SignUpInput) => (text: string) => {
    setForm((prev) => ({ ...prev, [field]: text }));
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  const submit = async () => {
    if (submitting) return;
    const found = validateSignUp(form);
    setErrors(found);
    setFormError(undefined);
    if (hasErrors(found)) return;

    setSubmitting(true);
    try {
      // On success the guard in src/app/_layout.tsx switches to the feed.
      await signUp(form);
    } catch (err) {
      if (!(err instanceof AuthError)) console.warn('[signUp] failed', err);
      setFormError(err instanceof AuthError ? err.message : 'Something went wrong. Try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthLayout title="Create your account" error={formError}>
      <View style={styles.nameRow}>
        <View style={styles.nameField}>
          <TextField
            label="First name"
            value={form.firstName}
            onChangeText={update('firstName')}
            error={errors.firstName}
            autoComplete="given-name"
            autoCapitalize="words"
            returnKeyType="next"
          />
        </View>
        <View style={styles.nameField}>
          <TextField
            label="Last name"
            value={form.lastName}
            onChangeText={update('lastName')}
            error={errors.lastName}
            autoComplete="family-name"
            autoCapitalize="words"
            returnKeyType="next"
          />
        </View>
      </View>
      <TextField
        label="Phone"
        value={form.phone}
        onChangeText={update('phone')}
        error={errors.phone}
        inputMode="tel"
        autoComplete="tel"
        returnKeyType="next"
      />
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
        hint={`At least ${MIN_PASSWORD_LENGTH} characters.`}
        secureTextEntry
        autoComplete="new-password"
        returnKeyType="go"
        onSubmitEditing={submit}
      />
      <PrimaryButton label="Create account" onPress={submit} loading={submitting} />
      <View style={styles.switchRow}>
        <Text style={styles.switchText}>Already have an account?</Text>
        {/* Goes back to the log in screen instead of stacking a second copy of it. */}
        <Link href="/sign-in" dismissTo style={styles.link}>
          Log in
        </Link>
      </View>
    </AuthLayout>
  );
}

const styles = StyleSheet.create({
  nameRow: {
    flexDirection: 'row',
    gap: 12,
  },
  nameField: {
    flex: 1,
  },
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
