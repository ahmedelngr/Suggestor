import { createContext, useContext, useState, type ReactNode } from 'react';

import * as auth from '../api/auth';
import type { Session, SignInInput, SignUpInput } from '../types';

interface SessionContextValue {
  /** null when signed out. */
  session: Session | null;
  signIn: (input: SignInInput) => Promise<void>;
  signUp: (input: SignUpInput) => Promise<void>;
  signOut: () => Promise<void>;
}

const SessionContext = createContext<SessionContextValue | null>(null);

/**
 * Keeps track of who is signed in. Memory only for now, so reloading the app
 * signs you out. Once auth is real, the session must be kept in the platform
 * secure store (expo-secure-store), never in plain storage.
 */
export function SessionProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);

  const value: SessionContextValue = {
    session,
    signIn: async (input) => setSession(await auth.signIn(input)),
    signUp: async (input) => setSession(await auth.signUp(input)),
    signOut: async () => {
      try {
        await auth.signOut();
      } finally {
        setSession(null);
      }
    },
  };

  return <SessionContext value={value}>{children}</SessionContext>;
}

export function useSession(): SessionContextValue {
  const value = useContext(SessionContext);
  if (!value) throw new Error('useSession must be used inside <SessionProvider>');
  return value;
}
