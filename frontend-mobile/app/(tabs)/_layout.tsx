import { Tabs } from 'expo-router';
import React from 'react';
import { ShieldAlert, History, MessageSquareText, Search } from 'lucide-react-native';
import { Platform } from 'react-native';

import { HapticTab } from '@/components/haptic-tab';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { useLanguage } from '../../context/LanguageContext';

export default function TabLayout() {
  const colorScheme = useColorScheme();
  const { t, language } = useLanguage();

  console.log('TabLayout Rendering. Language:', language);

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#4caf50',
        tabBarInactiveTintColor: '#999',
        headerShown: false,
        tabBarButton: HapticTab,
        tabBarStyle: {
          height: Platform.OS === 'ios' ? 90 : 60,
          paddingBottom: Platform.OS === 'ios' ? 30 : 10,
        },
      }}>

      {/* 1. Diagnose Tab (The Home Screen) */}
      <Tabs.Screen
        name="index"
        options={{
          tabBarLabel: t('tab_diagnose'),
          title: t('tab_diagnose'),
          tabBarIcon: ({ color, size }) => <ShieldAlert size={size} color={color} />,
        }}
      />

      {/* 2. Explore Tab (Resources, Guides) */}
      <Tabs.Screen
        name="explore"
        options={{
          tabBarLabel: t('tab_explore'),
          title: t('tab_explore'),
          tabBarIcon: ({ color, size }) => <Search size={size} color={color} />,
        }}
      />

      {/* 3. History Tab (Past Diagnoses) */}
      <Tabs.Screen
        name="history"
        options={{
          tabBarLabel: t('tab_history'),
          title: t('tab_history'),
          tabBarIcon: ({ color, size }) => <History size={size} color={color} />,
        }}
      />

      {/* 4. Chat Tab (AI Assistant) */}
      <Tabs.Screen
        name="chat"
        options={{
          tabBarLabel: t('tab_chatbot'),
          title: t('tab_chatbot'),
          tabBarIcon: ({ color, size }) => <MessageSquareText size={size} color={color} />,
        }}
      />
    </Tabs>
  );
}
