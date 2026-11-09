import { StyleSheet, Text, TextInput, View, type TextInputProps } from 'react-native';

import { colors } from '../theme';

interface Props extends TextInputProps {
  label: string;
  /** Shown under the input in red. */
  error?: string;
  /** Shown under the input when there is no error. */
  hint?: string;
}

export function TextField({ label, error, hint, style, ...inputProps }: Props) {
  return (
    <View style={styles.field}>
      <Text style={styles.label}>{label}</Text>
      <TextInput
        accessibilityLabel={label}
        placeholderTextColor={colors.textMuted}
        style={[styles.input, error ? styles.inputError : null, style]}
        {...inputProps}
      />
      {error ? (
        <Text style={styles.error}>{error}</Text>
      ) : hint ? (
        <Text style={styles.hint}>{hint}</Text>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  field: {
    gap: 6,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.text,
  },
  input: {
    minHeight: 48,
    paddingHorizontal: 14,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 10,
    backgroundColor: colors.card,
    fontSize: 16,
    color: colors.text,
  },
  inputError: {
    borderColor: colors.dislike,
  },
  error: {
    fontSize: 13,
    color: colors.dislike,
  },
  hint: {
    fontSize: 13,
    color: colors.textMuted,
  },
});
