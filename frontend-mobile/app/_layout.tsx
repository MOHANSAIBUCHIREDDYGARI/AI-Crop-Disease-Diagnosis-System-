import { DarkTheme, DefaultTheme, ThemeProvider } from '@react-navigation/native';
import { Stack, useRouter, useSegments } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { useEffect } from 'react';
import 'react-native-reanimated';
import { AuthProvider, useAuth } from '../context/AuthContext';
import { LanguageProvider, useLanguage } from '../context/LanguageContext';
import { AppThemeProvider } from '../context/ThemeContext';

import { useColorScheme } from '@/hooks/use-color-scheme';

function RootLayoutContent() {
  const colorScheme = useColorScheme();
  const { user, token, isLoading, isGuest } = useAuth();
  const { t } = useLanguage();
  const segments = useSegments();
  const router = useRouter();

  // Handle authentication routing
  useEffect(() => {
    if (isLoading) return;

    const inAuthGroup = segments[0] === 'login' || segments[0] === 'register';

    if (!token && !isGuest) {
      // No session at all → send to login
      if (!inAuthGroup) {
        router.replace('/login');
      }
    } else if (token && inAuthGroup) {
      // Has a real token but is on login/register → already logged in, go to dashboard
      // NOTE: Guests are allowed to navigate to login/register (to create an account)
      router.replace('/(tabs)');
    }
  }, [isLoading, token, isGuest, segments]);

  return (
    <ThemeProvider value={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
      {/* The Stack Navigator handles moving between screens (like pages in a book) */}
      <Stack screenOptions={{ headerShown: false }}>
        {/* The main tabs (Home, Explorer, History, Chat) */}
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        {/* Authentication Screens */}
        <Stack.Screen name="login" options={{ title: t('login') || 'Login' }} />
        <Stack.Screen name="register" options={{ title: t('register') || 'Register' }} />

        {/* Feature Screens */}
        <Stack.Screen name="results" options={{ title: t('diagnosisResults') || 'Diagnosis Results', headerShown: true }} />
        <Stack.Screen name="profile" options={{ title: t('profile') || 'Profile', headerShown: true }} />
        <Stack.Screen name="help" options={{ title: t('helpCenter') || 'Help Center', headerShown: true, presentation: 'modal' }} />
        <Stack.Screen name="privacy" options={{ title: t('privacyPolicy') || 'Privacy Policy', headerShown: true, presentation: 'modal' }} />
      </Stack>
      <StatusBar style="auto" />
    </ThemeProvider>
  );
}

export default function RootLayout() {
  // Wrap the entire app with our "Providers" so every screen can access Auth and Language settings
  return (
    <AuthProvider>
      <LanguageProvider>
        <AppThemeProvider>
          <RootLayoutContent />
        </AppThemeProvider>
      </LanguageProvider>
    </AuthProvider>
  );
}
