import { Stack } from 'expo-router';
import { AuthProvider } from '../src/AuthContext';
import { ThemeProvider } from '../src/ThemeContext';
import { StatusBar } from 'expo-status-bar';

export default function RootLayout() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <StatusBar style="auto" />
        <Stack screenOptions={{ headerShown: false }}>
          <Stack.Screen name="index" />
          <Stack.Screen name="(auth)" />
          <Stack.Screen name="(tabs)" />
          <Stack.Screen name="reader" options={{ presentation: 'card' }} />
          <Stack.Screen name="mood" options={{ presentation: 'modal' }} />
          <Stack.Screen name="circle-detail" options={{ presentation: 'card' }} />
        </Stack>
      </AuthProvider>
    </ThemeProvider>
  );
}
