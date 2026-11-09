import type { SignInInput, SignUpInput } from '../types';

/** One message per invalid field. An empty object means the form is valid. */
export type FieldErrors<T> = Partial<Record<keyof T, string>>;

export const MIN_PASSWORD_LENGTH = 8;
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export const hasErrors = (errors: object) => Object.keys(errors).length > 0;

function emailError(email: string): string | undefined {
  if (!email.trim()) return 'Enter your email.';
  if (!EMAIL_PATTERN.test(email.trim())) return 'Enter a valid email address.';
}

export function validateSignIn(input: SignInInput): FieldErrors<SignInInput> {
  const errors: FieldErrors<SignInInput> = {};
  const email = emailError(input.email);
  if (email) errors.email = email;
  if (!input.password) errors.password = 'Enter your password.';
  return errors;
}

export function validateSignUp(input: SignUpInput): FieldErrors<SignUpInput> {
  const errors: FieldErrors<SignUpInput> = {};
  if (!input.firstName.trim()) errors.firstName = 'Enter your first name.';
  if (!input.lastName.trim()) errors.lastName = 'Enter your last name.';

  // Not verified in MVP1, so only check that it looks like a phone number.
  const digits = input.phone.replace(/\D/g, '');
  if (!digits) errors.phone = 'Enter your phone number.';
  else if (digits.length < 10 || digits.length > 15) errors.phone = 'Enter a valid phone number.';

  const email = emailError(input.email);
  if (email) errors.email = email;
  if (input.password.length < MIN_PASSWORD_LENGTH) {
    errors.password = `Use at least ${MIN_PASSWORD_LENGTH} characters.`;
  }
  return errors;
}
