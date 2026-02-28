import { DarkTheme, DefaultTheme, ThemeProvider } from '@react-navigation/native';
import { Stack, useRouter, useSegments } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { useEffect } from 'react';
import { TouchableOpacity } from 'react-native';
import { ChevronLeft } from 'lucide-react-native';
import 'react-native-reanimated';
import { AuthProvider, useAuth } from '../context/AuthContext';
import { LanguageProvider, useLanguage } from '../context/LanguageContext';
import { AppThemeProvider } from '../context/ThemeContext';

import { useAppTheme } from '../context/ThemeContext';

function RootLayoutContent() {
  const { isDarkMode } = useAppTheme();
  const colorScheme = isDarkMode ? 'dark' : 'light';
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
      <Stack screenOptions={{ headerShown: false, headerBackVisible: true, headerStyle: { backgroundColor: colorScheme === 'dark' ? '#1e1e1e' : '#fff' }, headerTintColor: colorScheme === 'dark' ? '#fff' : '#000' }}>
        {/* The main tabs (Home, Explorer, History, Chat) */}
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        {/* Authentication Screens */}
        <Stack.Screen name="login" options={{ title: t('login') || 'Login' }} />
        <Stack.Screen name="register" options={{ title: t('register') || 'Register' }} />

        {/* Feature Screens */}
        {/* Feature Screens */}
        <Stack.Screen name="results" options={{
          title: t('diagnosisResults') || 'Diagnosis Results',
          headerShown: true,
          headerLeft: () => (
            <TouchableOpacity onPress={() => router.back()} style={{ padding: 8 }}>
              <ChevronLeft size={24} color={colorScheme === 'dark' ? '#fff' : '#000'} />
            </TouchableOpacity>
          )
        }} />
        <Stack.Screen name="profile" options={{
          title: t('profile') || 'Profile',
          headerShown: true,
          headerLeft: () => (
            <TouchableOpacity onPress={() => router.back()} style={{ padding: 8 }}>
              <ChevronLeft size={24} color={colorScheme === 'dark' ? '#fff' : '#000'} />
            </TouchableOpacity>
          )
        }} />
        <Stack.Screen name="help" options={{
          title: t('helpCenter') || 'Help Center',
          headerShown: true,
          presentation: 'modal',
          headerLeft: () => (
            <TouchableOpacity onPress={() => router.back()} style={{ padding: 8 }}>
              <ChevronLeft size={24} color={colorScheme === 'dark' ? '#fff' : '#000'} />
            </TouchableOpacity>
          )
        }} />
        <Stack.Screen name="privacy" options={{
          title: t('privacyPolicy') || 'Privacy Policy',
          headerShown: true,
          presentation: 'modal',
          headerLeft: () => (
            <TouchableOpacity onPress={() => router.back()} style={{ padding: 8 }}>
              <ChevronLeft size={24} color={colorScheme === 'dark' ? '#fff' : '#000'} />
            </TouchableOpacity>
          )
        }} />
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
