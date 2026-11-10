import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';

import { SessionProvider, useSession } from '../auth/SessionProvider';

export default function RootLayout() {
  return (
    <SessionProvider>
      <RootStack />
      <StatusBar style="dark" />
    </SessionProvider>
  );
}

function RootStack() {
  const signedIn = useSession().session !== null;

  // When a guard turns false (signing in or out), the router sends the user to
  // `redirectTo` and drops that group's screens from the back history.
  return (
    // Screens draw their own header, so it looks the same on iOS, Android and web.
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Protected guard={signedIn} redirectTo="/sign-in">
        <Stack.Screen name="index" />
        <Stack.Screen name="profile" />
      </Stack.Protected>
      <Stack.Protected guard={!signedIn} redirectTo="/">
        <Stack.Screen name="sign-in" />
        <Stack.Screen name="sign-up" />
      </Stack.Protected>
    </Stack>
  );
}
